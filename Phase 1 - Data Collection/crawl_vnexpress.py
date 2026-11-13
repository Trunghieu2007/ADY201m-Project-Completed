import os
import re
import sys
import time
import json
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REQUEST_DELAY = 0.05
TIMEOUT = 12
CRAWL_DAYS = 7  # Phạm vi lấy bài: 7 ngày gần nhất

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
}

CATEGORIES = [
    "thoi-su", "the-gioi", "kinh-doanh", "bat-dong-san", "khoa-hoc-cong-nghe",
    "giai-tri", "the-thao", "phap-luat", "giao-duc", "suc-khoe", "doi-song",
    "du-lich", "oto-xe-may", "tam-su", "y-kien", "thu-gian"
]

def fetch(url):
    """Tải nội dung trang web với xử lý timeout và User-Agent."""
    time.sleep(REQUEST_DELAY)
    try:
        res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        res.raise_for_status()
        res.encoding = "utf-8"
        return res.text
    except Exception:
        return ""

def normalize_datetime(raw):
    """Chuẩn hóa chuỗi thời gian xuất bản sang định dạng 'YYYY-MM-DD HH:MM:SS'."""
    if not raw:
        return None
    iso = re.search(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}", raw)
    if iso:
        return datetime.strptime(iso.group(0).replace("T", " "), "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M:%S")

    dm = re.search(r"\d{1,2}/\d{1,2}/\d{4}", raw)
    tm = re.search(r"\d{1,2}:\d{2}", raw)
    if dm:
        try:
            dt = datetime.strptime(dm.group(0), "%d/%m/%Y")
            if tm:
                h, m = map(int, tm.group(0).split(":"))
                dt = dt.replace(hour=h, minute=m)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    return None

def extract_author(soup):
    """Trích xuất tên tác giả bài viết từ thẻ tác giả hoặc thẻ chữ đậm cuối bài."""
    author_tag = soup.find("p", class_="author_mail") or soup.find("p", class_="author")
    if author_tag:
        author_text = author_tag.text.strip()
        if author_text:
            return author_text
    
    # Thử lấy dòng chữ đậm cuối cùng của phần thân bài (thường là bút danh phóng viên)
    strong_tags = soup.select(".fck_detail p.Normal strong, article p strong")
    if strong_tags:
        last_strong = strong_tags[-1].text.strip()
        if last_strong and len(last_strong.split()) <= 6 and not last_strong.endswith(":"):
            return last_strong

    meta_author = soup.find("meta", {"name": "author"})
    if meta_author and meta_author.get("content"):
        return meta_author["content"].strip()

    return "VnExpress"

def extract_article(html, url, fallback_date=None, default_category="Khác"):
    """Bóc tách đầy đủ các trường dữ liệu bài viết từ HTML của VnExpress."""
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    og = soup.find("meta", {"property": "og:type"})
    og_type = og.get("content", "").lower() if og else "unknown"

    date_tag = soup.find("span", class_="date")
    raw_date = date_tag.text.strip() if date_tag else ""
    if not raw_date:
        m_date = soup.find("meta", {"name": "pubdate"})
        raw_date = m_date.get("content", "").strip() if m_date else ""
    published_at = normalize_datetime(raw_date) or fallback_date

    h1 = soup.find("h1", class_="title-detail") or soup.find("h1")
    title = h1.text.strip() if h1 else ""

    desc_tag = soup.find("p", class_="description")
    description = desc_tag.text.strip() if desc_tag else ""
    if not description:
        m_desc = soup.find("meta", {"name": "description"}) or soup.find("meta", {"property": "og:description"})
        description = m_desc.get("content", "").strip() if m_desc else ""

    crumbs = [
        a.text.strip() for a in soup.select("ul.breadcrumb li a")
        if a.text.strip().lower() not in ["", "trang chủ"]
    ]
    category = crumbs[0] if crumbs else default_category
    subcategory = crumbs[1] if len(crumbs) > 1 else "Không có"

    paragraphs = [
        p.text.strip() for p in soup.select(".fck_detail p.Normal, .fck_detail p, article p")
        if p.text.strip()
    ]
    content = "\n".join(paragraphs)

    author = extract_author(soup)

    meta_id = soup.find("meta", {"name": "tt_article_id"})
    aid = meta_id["content"] if meta_id and meta_id.get("content") else url.split("?")[0].split("-")[-1].replace(".html", "")

    return {
        "article_id": aid,
        "title": title,
        "description": description,
        "content": content,
        "author": author,
        "published_at": published_at,
        "category": category,
        "subcategory": subcategory,
        "url": url,
        "og_type": og_type,
        "raw_word_count": len(content.split()),
        "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def collect_rss_urls():
    """Quét toàn bộ danh mục RSS của VnExpress để lấy danh sách liên kết bài viết."""
    print("[*] Đang kết nối tới 16 chuyên mục RSS VnExpress...")
    cutoff_dt = datetime.now() - timedelta(days=CRAWL_DAYS)
    urls = {}
    for cat in CATEGORIES:
        rss_url = f"https://vnexpress.net/rss/{cat}.rss"
        xml = fetch(rss_url)
        if not xml:
            continue
        try:
            soup = BeautifulSoup(xml, "xml")
            for item in soup.find_all("item"):
                link_tag = item.find("link")
                link = link_tag.text.strip() if link_tag else ""
                if not link or not link.endswith(".html"):
                    continue

                pub_tag = item.find("pubDate")
                pub_str = None
                is_within = True
                if pub_tag and pub_tag.text:
                    try:
                        dt = parsedate_to_datetime(pub_tag.text.strip()).astimezone().replace(tzinfo=None)
                        pub_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                        if dt < cutoff_dt:
                            is_within = False
                    except Exception:
                        pass

                if not is_within:
                    continue

                clean_url = link.split("?")[0]
                if clean_url not in urls:
                    urls[clean_url] = (pub_str, cat)
        except Exception:
            pass

    print(f"[+] Tìm thấy tổng cộng {len(urls)} bài viết độc nhất trong {CRAWL_DAYS} ngày gần nhất.")
    return urls

def crawl_fresh_batch(output_path=None):
    """Cào dữ liệu một đợt bài viết mới hoàn toàn và lưu ra file JSON thô."""
    if output_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(base_dir, "data", "raw", "vnexpress_raw.json")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    links_dict = collect_rss_urls()
    print(f"[*] Bắt đầu cào {len(links_dict)} bài viết bằng đa luồng...")

    raw_articles = []
    start_time = time.time()

    def process_item(item):
        url, (pub_date, cat) = item
        html = fetch(url)
        return extract_article(html, url, pub_date, cat)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_item, item): item[0] for item in links_dict.items()}
        for i, future in enumerate(as_completed(futures), start=1):
            art = future.result()
            if art:
                raw_articles.append(art)
            if i % 100 == 0 or i == len(links_dict):
                print(f"    -> Đã cào {i}/{len(links_dict)} bài viết ({len(raw_articles)} thành công)...")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(raw_articles, f, ensure_ascii=False, indent=2)

    elapsed = round(time.time() - start_time, 2)
    print(f"[+] HOÀN TẤT THU THẬP DỮ LIỆU TƯƠI:")
    print(f"    - Tổng bài viết thô lưu trữ: {len(raw_articles)} bài")
    print(f"    - Thời gian thực thi: {elapsed} giây")
    print(f"    - Tệp dữ liệu thô: {output_path}")
    return output_path

if __name__ == "__main__":
    crawl_fresh_batch()
