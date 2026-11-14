import os
import sys
import json
import pyodbc
import pandas as pd

def get_mssql_connection():
    """Tạo kết nối tới Microsoft SQL Server (tự động phát hiện driver và tạo database ADY201m nếu chưa có)."""
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
        raise RuntimeError("Không tìm thấy ODBC Driver Microsoft SQL Server trên máy tính.")

    servers = [
        r"localhost\SQLEXPRESS",
        r".\SQLEXPRESS",
        "localhost",
        "."
    ]

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
        raise RuntimeError(f"Không thể kết nối tới Microsoft SQL Server service trên các địa chỉ: {servers}")

    conn_master.autocommit = True
    cursor_master = conn_master.cursor()
    cursor_master.execute("IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'ADY201m') CREATE DATABASE ADY201m;")
    conn_master.close()

    conn_str_db = f"DRIVER={{{selected_driver}}};SERVER={connected_server};DATABASE=ADY201m;Trusted_Connection=yes;TrustServerCertificate=yes;"
    conn_db = pyodbc.connect(conn_str_db, timeout=5)
    return conn_db, f"Microsoft SQL Server ({connected_server}) qua driver [{selected_driver}]"

def load_data_to_mssql(clean_path=None):
    """
    Vai trò chính của Module này:
    Khởi tạo bảng dbo.VnExpress_Articles và nạp toàn bộ tập dữ liệu đã làm sạch vào Microsoft SQL Server.
    Đóng vai trò kho lưu trữ trung tâm (Data Storage & Integration) cho dự án.
    Không tự động chạy ngầm các câu truy vấn phân tích nghiệp vụ; các câu truy vấn được lưu tại DemoTruyVan.sql
    để người dùng hoặc chuyên viên phân tích chủ động thực thi khi cần thiết.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if clean_path is None:
        clean_path = os.path.join(base_dir, "Phase 2 - Data Preprocessing & Quality", "vnexpress_clean.json")

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
    print(f"[*] Đã kết nối thành công tới: {target_name}")
    cursor = conn.cursor()

    # Tạo bảng 16 cột chuẩn hóa trên Microsoft SQL Server
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
        category            NVARCHAR(255)  NOT NULL,
        subcategory         NVARCHAR(255)  NULL,
        url                 NVARCHAR(1000) NOT NULL,
        word_count          INT            NOT NULL,
        title_length        INT            NOT NULL,
        desc_length         INT            NOT NULL
    );
    """)

    # Tạo các chỉ mục tối ưu hóa truy vấn
    cursor.execute("CREATE NONCLUSTERED INDEX IX_VnExpress_Category ON dbo.VnExpress_Articles(category);")
    cursor.execute("CREATE NONCLUSTERED INDEX IX_VnExpress_PublishDate ON dbo.VnExpress_Articles(publish_date);")
    cursor.execute("CREATE NONCLUSTERED INDEX IX_VnExpress_Author ON dbo.VnExpress_Articles(author);")
    conn.commit()

    # Nạp dữ liệu theo lô (Batch Insert)
    insert_sql = f"""
    INSERT INTO dbo.VnExpress_Articles (
        {', '.join(insert_cols)}
    ) VALUES ({', '.join(['?'] * len(insert_cols))})
    """
    records = []
    for _, row in df.iterrows():
        rec = (
            str(row["article_id"]),
            str(row["title"]),
            str(row["description"]) if pd.notna(row["description"]) else "",
            str(row["content"]),
            str(row["author"]),
            str(row["published_at"]),
            str(row["publish_date"]),
            int(row["publish_hour"]),
            str(row["publish_dayofweek"]),
            int(row["is_weekend"]),
            str(row["category"]),
            str(row["subcategory"]) if pd.notna(row["subcategory"]) else "",
            str(row["url"]),
            int(row["word_count"]),
            int(row["title_length"]),
            int(row["desc_length"])
        )
        records.append(rec)

    cursor.fast_executemany = True
    cursor.executemany(insert_sql, records)
    conn.commit()
    print(f"[+] ĐÃ NẠP THÀNH CÔNG {len(records)} BẢN GHI VÀO MICROSOFT SQL SERVER (dbo.VnExpress_Articles).")
    print("[*] Kịch bản truy vấn phân tích nghiệp vụ được lưu tại: DemoTruyVan.sql")

    conn.close()

if __name__ == "__main__":
    load_data_to_mssql()
