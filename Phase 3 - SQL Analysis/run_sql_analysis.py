"""
MODULE: LƯU TRỮ VÀ KIỂM ĐỊNH DỮ LIỆU TRÊN MICROSOFT SQL SERVER
Phụ trách: Nguyễn Hữu Hùng (Phase 3 - SQL Analysis)
Đề tài: Báo cáo Khoa học Dữ liệu Báo điện tử VnExpress (ADY201m)
"""

import os
import sys
import json
import pandas as pd

def get_mssql_connection():
    """
    Tự động dò tìm ODBC Driver và kết nối tới Microsoft SQL Server (hoặc SQL Server Express).
    Hỗ trợ kết nối vào Database ADY201m.
    """
    try:
        import pyodbc
    except ImportError:
        return None, "Chưa cài đặt thư viện pyodbc (chạy: pip install pyodbc)"

    drivers = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
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
        return None, f"Không tìm thấy ODBC Driver cho Microsoft SQL Server (Hiện có: {available_drivers})"

    servers = [
        r"localhost\SQLEXPRESS",
        r".\SQLEXPRESS",
        "localhost",
        ".",
        r"(localdb)\mssqllocaldb"
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
        return None, "Không thể kết nối tới Microsoft SQL Server service trên máy tính (Đảm bảo SQL Server đang chạy)."

    try:
        conn_master.autocommit = True
        cursor_master = conn_master.cursor()
        cursor_master.execute("IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'ADY201m') CREATE DATABASE ADY201m;")
        conn_master.close()
    except Exception as e:
        return None, f"Lỗi khởi tạo Database ADY201m trên Microsoft SQL Server: {e}"

    # Kết nối trực tiếp vào Database ADY201m
    try:
        conn_str_db = f"DRIVER={{{selected_driver}}};SERVER={connected_server};DATABASE=ADY201m;Trusted_Connection=yes;TrustServerCertificate=yes;"
        conn_db = pyodbc.connect(conn_str_db, timeout=5)
        return conn_db, f"Microsoft SQL Server [{connected_server}] qua Driver [{selected_driver}]"
    except Exception as e:
        return None, f"Lỗi kết nối tới Database ADY201m trên Microsoft SQL Server: {e}"

def run_sql_pipeline(clean_path=None):
    """
    Nạp dữ liệu sạch từ vnexpress_clean.json vào bảng dbo.VnExpress_Articles trên Microsoft SQL Server
    và thực hiện quy trình kiểm định chất lượng, tính toàn vẹn, chống trùng lặp.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if clean_path is None:
        clean_path = os.path.join(base_dir, "Phase 2 - Data Preprocessing & Quality", "vnexpress_clean.json")

    print("====================================================================")
    print("PHASE 3: NẠP VÀ KIỂM ĐỊNH DỮ LIỆU TRÊN MICROSOFT SQL SERVER")
    print("Thành viên phụ trách: Nguyễn Hữu Hùng")
    print("====================================================================")

    if not os.path.exists(clean_path):
        print(f"[-] Không tìm thấy tệp dữ liệu sạch tại: {clean_path}")
        return False

    with open(clean_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    total_records = len(df)
    print(f"[+] Đã đọc {total_records} bản ghi từ tệp: {os.path.basename(clean_path)}")

    # 1. Kiểm tra tính toàn vẹn dữ liệu trước khi nạp
    dup_id = df["article_id"].duplicated().sum()
    null_counts = df[["article_id", "title", "content", "author", "category"]].isnull().sum().sum()
    print(f"[*] Kiểm định chất lượng: {dup_id} trùng lặp, {null_counts} trường hợp Null.")

    # 2. CHUẨN BỊ ĐẦY ĐỦ 16 CỘT THEO SCHEMA MICROSOFT SQL SERVER
    dt_series = pd.to_datetime(df["published_at"])
    df["published_at"] = dt_series.dt.strftime("%Y-%m-%d %H:%M:%S")
    df["publish_date"] = dt_series.dt.strftime("%Y-%m-%d")
    df["publish_hour"] = dt_series.dt.hour
    df["publish_dayofweek"] = dt_series.dt.day_name()
    df["is_weekend"] = dt_series.dt.dayofweek.apply(lambda d: 1 if d >= 5 else 0)
    df["title_length"] = df["title"].fillna("").apply(lambda t: len(str(t).split()))
    df["desc_length"] = df["description"].fillna("").apply(lambda d: len(str(d).split()))

    insert_cols = [
        "article_id", "title", "description", "content", "author",
        "published_at", "publish_date", "publish_hour", "publish_dayofweek", "is_weekend",
        "category", "subcategory", "url", "word_count", "title_length", "desc_length"
    ]

    # 3. KẾT NỐI VÀO MICROSOFT SQL SERVER
    conn, info = get_mssql_connection()
    if conn is None:
        print(f"\n[-] Thông báo: {info}")
        print("[*] Hướng dẫn thực hiện:")
        print("    1. Mở SQL Server Management Studio (SSMS).")
        print("    2. Mở file 'SQLschema.sql' và nhấn Execute (F5) để tạo Database ADY201m và bảng dbo.VnExpress_Articles.")
        print("    3. Đảm bảo dịch vụ SQL Server (SQLEXPRESS) đang chạy và thực thi lại script này.")
        return False

    print(f"\n[+] Kết nối thành công tới: {info}")
    cursor = conn.cursor()

    # Kiểm tra bảng dbo.VnExpress_Articles (đã được tạo bằng SQLschema.sql trong SSMS)
    cursor.execute("SELECT OBJECT_ID(N'dbo.VnExpress_Articles', N'U');")
    table_exists = cursor.fetchone()[0] is not None

    if table_exists:
        print("[*] Phát hiện bảng dbo.VnExpress_Articles đã được tạo sẵn từ SSMS.")
        print("[*] Đang làm sạch dữ liệu cũ (TRUNCATE) để đảm bảo không bị nhân bản dữ liệu...")
        cursor.execute("TRUNCATE TABLE dbo.VnExpress_Articles;")
        conn.commit()
    else:
        print("[!] Bảng dbo.VnExpress_Articles chưa tồn tại. Đang tự động khởi tạo theo lược đồ SQLschema.sql...")
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
        print("[+] Đã khởi tạo bảng và 3 Index thành công!")

    # 4. BƠM (INSERT) 655 BÀI BÁO VÀO MICROSOFT SQL SERVER
    print(f"\n[*] Đang bơm đồng loạt {total_records} bản ghi vào bảng dbo.VnExpress_Articles...")
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
    print(f"[+] Bơm dữ liệu thành công: Đã ghi nhận {total_records} bản ghi vào Microsoft SQL Server!")

    # 5. Xác nhận nạp dữ liệu hoàn tất
    cursor.execute("SELECT COUNT(*) FROM dbo.VnExpress_Articles;")
    sql_total = cursor.fetchone()[0]
    conn.close()

    print(f"\n[+] HOÀN TẤT: Đã nạp thành công {sql_total} bài viết sạch vào bảng dbo.VnExpress_Articles trên Microsoft SQL Server!")
    return True

if __name__ == "__main__":
    run_sql_pipeline()
