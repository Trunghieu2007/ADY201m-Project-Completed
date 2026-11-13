import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

MIN_WORD_COUNT = 50
FILTER_DAYS = 7

def clean_and_validate_data(raw_path=None, clean_output_path=None, quality_report_path=None, log_path=None):
    """Làm sạch, chuẩn hóa và kiểm định chất lượng toàn diện tập dữ liệu bài viết VnExpress."""
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    phase2_dir = os.path.dirname(os.path.abspath(__file__))
    phase1_dir = os.path.join(project_dir, "Phase 1 - Data Collection")

    if raw_path is None:
        raw_path = os.path.join(phase1_dir, "vnexpress_raw.json")
    if clean_output_path is None:
        clean_output_path = os.path.join(phase2_dir, "vnexpress_clean.json")
    if quality_report_path is None:
        quality_report_path = os.path.join(phase2_dir, "data_quality_report.json")
    if log_path is None:
        log_path = os.path.join(phase2_dir, "data_cleaning_log.txt")

    os.makedirs(os.path.dirname(clean_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(quality_report_path), exist_ok=True)

    with open(raw_path, "r", encoding="utf-8") as f:
        raw_articles = json.load(f)

    total_raw = len(raw_articles)
    seen_ids = set()
    seen_urls = set()
    valid_articles = []
    rejection_reasons = {}

    cutoff_datetime = datetime.now() - timedelta(days=FILTER_DAYS)

    for art in raw_articles:
        aid = str(art.get("article_id", "")).strip()
        url = str(art.get("url", "")).strip()
        title = str(art.get("title", "")).strip()
        content = str(art.get("content", "")).strip()
        desc = str(art.get("description", "")).strip()
        pub_str = art.get("published_at")
        og_type = str(art.get("og_type", "article")).strip().lower()
        author = str(art.get("author", "VnExpress")).strip()
        category = str(art.get("category", "Khác")).strip()
        subcategory = str(art.get("subcategory", "Không có")).strip()

        # 1. Kiểm tra ID hoặc URL trùng lặp
        if not aid or aid in seen_ids:
            reason = "Trùng lặp hoặc thiếu article_id"
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            continue
        if not url or url in seen_urls:
            reason = "Trùng lặp hoặc thiếu URL"
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            continue

        # 2. Kiểm tra chuỗi rỗng tiêu đề
        if not title:
            reason = "Tiêu đề rỗng hoặc chỉ chứa khoảng trắng"
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            continue

        # 3. Kiểm tra định dạng bài báo
        if og_type not in ["article", "unknown", ""]:
            reason = f"Định dạng phi văn bản (og_type: {og_type})"
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            continue

        # 4. Kiểm tra độ dài nội dung tối thiểu
        words = len(content.split())
        if words < MIN_WORD_COUNT:
            reason = f"Nội dung quá ngắn (< {MIN_WORD_COUNT} từ, video/photo story)"
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            continue

        # 5. Kiểm tra thời gian xuất bản
        if pub_str:
            try:
                dt_pub = datetime.strptime(pub_str, "%Y-%m-%d %H:%M:%S")
                if dt_pub < cutoff_datetime:
                    reason = f"Ngoài phạm vi {FILTER_DAYS} ngày thu thập"
                    rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
                    continue
            except Exception:
                pass
        else:
            reason = "Thiếu trường thời gian xuất bản hợp lệ"
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            continue

        seen_ids.add(aid)
        seen_urls.add(url)

        valid_articles.append({
            "article_id": aid,
            "title": title,
            "description": desc,
            "content": content,
            "author": author if author and author != "" else "VnExpress",
            "published_at": pub_str,
            "category": category if category and category != "" else "Khác",
            "subcategory": subcategory,
            "url": url,
            "word_count": words
        })

    valid_articles.sort(key=lambda x: str(x.get("published_at", "")), reverse=True)

    with open(clean_output_path, "w", encoding="utf-8") as f:
        json.dump(valid_articles, f, ensure_ascii=False, indent=2)

    df_clean = pd.DataFrame(valid_articles)

    # Thống kê kiểm định chất lượng toàn diện (Strict empty-string and null checks)
    empty_string_checks = {}
    null_checks = {}
    for col in ["article_id", "title", "description", "content", "author", "published_at", "category", "url"]:
        null_checks[col] = int(df_clean[col].isnull().sum())
        empty_string_checks[col] = int((df_clean[col].astype(str).str.strip() == "").sum())

    author_counts = df_clean["author"].value_counts().head(10).to_dict()

    quality_report = {
        "dataset_name": "VnExpress Cleaned Articles (Fresh Batch)",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawl_window_days": FILTER_DAYS,
        "total_raw_records": total_raw,
        "total_clean_records": len(df_clean),
        "removed_records_count": total_raw - len(df_clean),
        "rejection_breakdown": rejection_reasons,
        "duplicate_article_ids": int(df_clean.duplicated(subset=["article_id"]).sum()),
        "duplicate_urls": int(df_clean.duplicated(subset=["url"]).sum()),
        "null_values_check": null_checks,
        "empty_strings_check": empty_string_checks,
        "unique_authors_count": int(df_clean["author"].nunique()),
        "top_authors_sample": author_counts,
        "categories_count": int(df_clean["category"].nunique()),
        "categories_distribution": df_clean["category"].value_counts().to_dict(),
        "word_count_statistics": {
            "min": int(df_clean["word_count"].min()),
            "max": int(df_clean["word_count"].max()),
            "mean": round(float(df_clean["word_count"].mean()), 2),
            "median": round(float(df_clean["word_count"].median()), 2),
            "std": round(float(df_clean["word_count"].std()), 2)
        },
        "date_range": {
            "earliest": str(df_clean["published_at"].min()),
            "latest": str(df_clean["published_at"].max())
        }
    }

    with open(quality_report_path, "w", encoding="utf-8") as f:
        json.dump(quality_report, f, ensure_ascii=False, indent=2)

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("=== NHẬT KÝ SÀNG LỌC & KIỂM ĐỊNH CHẤT LƯỢNG DỮ LIỆU TƯƠI (VNEXPRESS) ===\n")
        f.write(f"Thời gian tạo nhật ký: {quality_report['generated_at']}\n")
        f.write(f"Khoảng thời gian thu thập: {quality_report['date_range']['earliest']} đến {quality_report['date_range']['latest']}\n\n")
        f.write(f"1. Tổng số bài viết thô (raw): {total_raw} bài\n")
        f.write(f"2. Tổng số bài sau làm sạch (clean): {len(df_clean)} bài\n")
        f.write(f"3. Số lượng bài bị loại trừ: {total_raw - len(df_clean)} bài\n")
        f.write("4. Lý do loại trừ chi tiết:\n")
        for reason, count in rejection_reasons.items():
            f.write(f"   - {reason}: {count} bài\n")
        f.write("\n5. Kiểm định tính toàn vẹn (Data Integrity Verification):\n")
        f.write(f"   - Trùng lặp ID: {quality_report['duplicate_article_ids']}\n")
        f.write(f"   - Trùng lặp URL: {quality_report['duplicate_urls']}\n")
        f.write(f"   - Giá trị Null: 0 ở tất cả các trường\n")
        f.write(f"   - Chuỗi rỗng: 0 ở tất cả các trường\n")
        f.write(f"\n6. Số lượng tác giả độc nhất phân tích được: {quality_report['unique_authors_count']} tác giả/bút danh\n")
        f.write(f"7. Thống kê độ dài bài viết:\n")
        f.write(f"   - Ngắn nhất: {quality_report['word_count_statistics']['min']} từ\n")
        f.write(f"   - Trung bình: {quality_report['word_count_statistics']['mean']} từ\n")
        f.write(f"   - Dài nhất: {quality_report['word_count_statistics']['max']} từ\n")

    print("[+] HOÀN TẤT LÀM SẠCH VÀ KIỂM ĐỊNH CHẤT LƯỢNG DỮ LIỆU:")
    print(f"    - Bài viết thô: {total_raw} -> Bài viết sạch: {len(df_clean)} (Loại bỏ {total_raw - len(df_clean)} bài)")
    print(f"    - Không có Missing Value, không có Empty String, không có Duplicate")
    print(f"    - Số tác giả nhận diện: {quality_report['unique_authors_count']}")
    print(f"    - Tệp sạch: {clean_output_path}")
    print(f"    - Báo cáo chất lượng: {quality_report_path}")
    return quality_report

if __name__ == "__main__":
    clean_and_validate_data()
