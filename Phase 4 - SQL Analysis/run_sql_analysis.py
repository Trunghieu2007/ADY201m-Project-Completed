import os
import sys
import json
import sqlite3
import pandas as pd

def get_mssql_connection():
    """Tạo kết nối tới Microsoft SQL Server (tự động phát hiện driver và tạo database nếu chưa có)."""
    try:
        import pyodbc
    except ImportError:
        return None, "Chưa cài đặt thư viện pyodbc"

    drivers = [
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 18 for SQL Server",
        "SQL Server Native Client 11.0",
        "SQL Server"
    ]
    available_drivers = pyodbc.drivers()
    selected_driver = None
    for d in drivers:
        if d in available_drivers:
            selected_driver = d
            break

    if not selected_driver:
        return None, "Không tìm thấy ODBC Driver Microsoft SQL Server phù hợp trên máy tính"

    servers = [
        r"localhost\SQLEXPRESS",
        r".\SQLEXPRESS",
        "localhost",
        "."
    ]

    # 1. Thử kết nối tới server master để đảm bảo Database ADY201m tồn tại
    conn_master = None
    connected_server = None
    for s in servers:
        try:
            conn_str = f"DRIVER={{{selected_driver}}};SERVER={s};DATABASE=master;Trusted_Connection=yes;TrustServerCertificate=yes;"
            conn_master = pyodbc.connect(conn_str, timeout=3)
            connected_server = s
            break
        except Exception:
            continue

    if conn_master is None:
        return None, "Không thể kết nối tới Microsoft SQL Server service trên máy tính"

    conn_master.autocommit = True
    cursor_master = conn_master.cursor()
    cursor_master.execute("IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'ADY201m') CREATE DATABASE ADY201m;")
    conn_master.close()

    # 2. Kết nối trực tiếp vào Database ADY201m
    conn_str_db = f"DRIVER={{{selected_driver}}};SERVER={connected_server};DATABASE=ADY201m;Trusted_Connection=yes;TrustServerCertificate=yes;"
    conn_db = pyodbc.connect(conn_str_db, timeout=5)
    return conn_db, f"Microsoft SQL Server ({connected_server}) qua driver [{selected_driver}]"

def run_sql_pipeline(clean_path=None, output_json_path=None):
    """Nạp dữ liệu vào Microsoft SQL Server (ưu tiên) hoặc SQLite dự phòng và thực thi bộ 6 câu truy vấn phân tích nghiệp vụ."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if clean_path is None:
        clean_path = os.path.join(base_dir, "Phase 2 - Data Preprocessing & Quality", "vnexpress_clean.json")
    if output_json_path is None:
        output_json_path = os.path.join(base_dir, "Phase 4 - SQL Analysis", "sql_analysis_results.json")

    with open(clean_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    df["published_at_dt"] = pd.to_datetime(df["published_at"])
    df["publish_date"] = df["published_at_dt"].dt.strftime("%Y-%m-%d")
    df["publish_hour"] = df["published_at_dt"].dt.hour
    df["publish_dayofweek"] = df["published_at_dt"].dt.day_name()
    df["is_weekend"] = df["published_at_dt"].dt.dayofweek.apply(lambda d: 1 if d >= 5 else 0)
    df["title_length"] = df["title"].fillna("").apply(lambda t: len(str(t).split()))
    df["desc_length"] = df["description"].fillna("").apply(lambda d: len(str(d).split()))

    insert_cols = [
        "article_id", "title", "description", "content", "author",
        "published_at", "publish_date", "publish_hour", "publish_dayofweek", "is_weekend",
        "category", "subcategory", "url", "word_count", "title_length", "desc_length"
    ]

    conn, target_name = get_mssql_connection()
    is_mssql = conn is not None

    if is_mssql:
        print(f"[*] Đã kết nối thành công tới: {target_name}")
        cursor = conn.cursor()

        # Tạo bảng 16 cột trên Microsoft SQL Server
        cursor.execute("IF OBJECT_ID(N'dbo.VnExpress_Articles', N'U') IS NOT NULL DROP TABLE dbo.VnExpress_Articles;")
        cursor.execute("""
        CREATE TABLE dbo.VnExpress_Articles (
            article_id          NVARCHAR(50)   NOT NULL CONSTRAINT PK_VnExpress_Articles PRIMARY KEY,
            title               NVARCHAR(1000) NOT NULL,
            description         NVARCHAR(MAX)  NULL,
            content             NVARCHAR(MAX)  NOT NULL,
            author              NVARCHAR(255)  NOT NULL,
            published_at        DATETIME       NOT NULL,
            publish_date        DATE           NOT NULL,
            publish_hour        INT            NOT NULL,
            publish_dayofweek   NVARCHAR(50)   NOT NULL,
            is_weekend          INT            NOT NULL,
            category            NVARCHAR(100)  NOT NULL,
            subcategory         NVARCHAR(100)  NULL,
            url                 NVARCHAR(1000) NOT NULL,
            word_count          INT            NOT NULL,
            title_length        INT            NOT NULL,
            desc_length         INT            NOT NULL
        );
        """)
        cursor.execute("CREATE INDEX IX_Articles_Category ON dbo.VnExpress_Articles(category);")
        cursor.execute("CREATE INDEX IX_Articles_Author ON dbo.VnExpress_Articles(author);")
        cursor.execute("CREATE INDEX IX_Articles_PublishDate ON dbo.VnExpress_Articles(publish_date);")
        conn.commit()

        # Chèn dữ liệu vào MS SQL Server bằng batch executemany
        sql_insert = """
        INSERT INTO dbo.VnExpress_Articles (
            article_id, title, description, content, author,
            published_at, publish_date, publish_hour, publish_dayofweek, is_weekend,
            category, subcategory, url, word_count, title_length, desc_length
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        records = [tuple(row[col] for col in insert_cols) for _, row in df.iterrows()]
        cursor.fast_executemany = True
        cursor.executemany(sql_insert, records)
        conn.commit()

        table_ref = "dbo.VnExpress_Articles"
        cast_wc = "CAST(word_count AS FLOAT)"
        cast_tl = "CAST(title_length AS FLOAT)"
    else:
        print(f"[-] Thông báo: {target_name}. Sử dụng SQLite làm CSDL quan hệ tương đương.")
        db_path = os.path.join(base_dir, "Phase 4 - SQL Analysis", "vnexpress_analysis.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS VnExpress_Articles;")
        cursor.execute("""
        CREATE TABLE VnExpress_Articles (
            article_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            published_at TEXT NOT NULL,
            publish_date TEXT NOT NULL,
            publish_hour INTEGER NOT NULL,
            publish_dayofweek TEXT NOT NULL,
            is_weekend INTEGER NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT,
            url TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            title_length INTEGER NOT NULL,
            desc_length INTEGER NOT NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_category ON VnExpress_Articles(category);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_author ON VnExpress_Articles(author);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_pubdate ON VnExpress_Articles(publish_date);")
        df[insert_cols].to_sql("VnExpress_Articles", conn, if_exists="append", index=False)
        conn.commit()

    conn.close()
    print(f"[+] ĐÃ NẠP THÀNH CÔNG {len(df)} BẢN GHI VÀO { 'MICROSOFT SQL SERVER (ADY201m.dbo.VnExpress_Articles)' if is_mssql else 'SQLITE (vnexpress_analysis.db)' }")
    return True

if __name__ == "__main__":
    run_sql_pipeline()
