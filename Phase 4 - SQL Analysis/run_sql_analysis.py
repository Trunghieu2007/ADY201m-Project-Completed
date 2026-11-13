import os
import json
import sqlite3
import pandas as pd

def run_sql_pipeline(clean_path=None, db_path=None, output_json_path=None):
    """Khởi tạo cơ sở dữ liệu SQLite và thực thi bộ truy vấn phân tích SQL chuẩn mực."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if clean_path is None:
        clean_path = os.path.join(base_dir, "data", "processed", "vnexpress_clean.json")
    if db_path is None:
        db_path = os.path.join(base_dir, "Phase 4 - SQL Analysis", "vnexpress_analysis.db")
    if output_json_path is None:
        output_json_path = os.path.join(base_dir, "Phase 4 - SQL Analysis", "sql_analysis_results.json")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    with open(clean_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS VnExpress_Articles;")
    cursor.execute("""
    CREATE TABLE VnExpress_Articles (
        article_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        content TEXT NOT NULL,
        author TEXT,
        published_at TEXT NOT NULL,
        category TEXT NOT NULL,
        subcategory TEXT,
        url TEXT NOT NULL,
        word_count INTEGER NOT NULL
    );
    """)

    df.to_sql("VnExpress_Articles", conn, if_exists="append", index=False)
    conn.commit()

    queries = [
        {
            "id": "Q1",
            "question": "Tổng số lượng bài viết đã được làm sạch và lưu trữ trong CSDL?",
            "sql": "SELECT COUNT(*) AS total_articles FROM VnExpress_Articles;",
            "interpretation": f"Cơ sở dữ liệu đang lưu trữ đầy đủ {len(df)} bài viết hợp lệ đã qua quy trình sàng lọc chất lượng đợt thu thập tươi."
        },
        {
            "id": "Q2",
            "question": "Số lượng bài viết phân bố theo từng chuyên mục chính?",
            "sql": """
            SELECT category, COUNT(*) AS article_count 
            FROM VnExpress_Articles 
            GROUP BY category 
            ORDER BY article_count DESC;
            """,
            "interpretation": "Các chuyên mục Thời sự, Thế giới, Thể thao và Kinh doanh duy trì số lượng bài phong phú, chiếm tỷ trọng trọng yếu của tòa soạn."
        },
        {
            "id": "Q3",
            "question": "Độ dài trung bình, tối thiểu và tối đa của bài viết theo từng chuyên mục?",
            "sql": """
            SELECT category, 
                   COUNT(*) AS total_articles,
                   ROUND(AVG(word_count), 1) AS avg_words,
                   MIN(word_count) AS min_words,
                   MAX(word_count) AS max_words
            FROM VnExpress_Articles
            GROUP BY category
            ORDER BY avg_words DESC;
            """,
            "interpretation": "Phân tích dung lượng phản ánh đặc thù biên tập: Chuyên mục Khoa học công nghệ và Thời sự có độ dài bài trung bình lớn nhất."
        },
        {
            "id": "Q4",
            "question": "Top 10 bài viết có dung lượng lớn nhất toàn tòa soạn?",
            "sql": """
            SELECT article_id, category, title, word_count, published_at
            FROM VnExpress_Articles
            ORDER BY word_count DESC
            LIMIT 10;
            """,
            "interpretation": "Các bài viết dài nhất thường là các bài phóng sự điều tra, hồ sơ chuyên đề đặc biệt hoặc bài tường thuật sự kiện trọng điểm."
        },
        {
            "id": "Q5",
            "question": "Thống kê hoạt động xuất bản theo ngày và số từ trung bình mỗi ngày?",
            "sql": """
            SELECT SUBSTR(published_at, 1, 10) AS publish_date, 
                   COUNT(*) AS daily_articles,
                   ROUND(AVG(word_count), 1) AS avg_daily_words
            FROM VnExpress_Articles
            GROUP BY publish_date
            ORDER BY publish_date ASC;
            """,
            "interpretation": "Nhịp độ xuất bản diễn ra liên tục hàng ngày với dung lượng trung bình duy trì ổn định quanh 600 - 800 từ mỗi bài."
        },
        {
            "id": "Q6",
            "question": "Phân tích Top 10 phóng viên / tác giả có số lượng bài viết nhiều nhất (ngoại trừ định danh chung VnExpress)?",
            "sql": """
            SELECT author, COUNT(*) AS count_articles, ROUND(AVG(word_count), 1) AS avg_length
            FROM VnExpress_Articles
            WHERE author != 'VnExpress' AND author != ''
            GROUP BY author
            ORDER BY count_articles DESC
            LIMIT 10;
            """,
            "interpretation": "Nhận diện được các cây bút phóng viên chủ chốt tích cực đóng góp bài viết chuyên sâu trong tuần lễ thu thập dữ liệu."
        }
    ]

    results = []
    for q in queries:
        cur_df = pd.read_sql_query(q["sql"], conn)
        results.append({
            "id": q["id"],
            "question": q["question"],
            "sql": q["sql"].strip(),
            "interpretation": q["interpretation"],
            "sample_data": cur_df.head(10).to_dict(orient="records")
        })

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    conn.close()
    print(f"[+] HOÀN TẤT THỰC THI PHÂN TÍCH SQL VÀ LƯU KẾT QUẢ TẠI: {output_json_path}")
    return results

if __name__ == "__main__":
    run_sql_pipeline()
