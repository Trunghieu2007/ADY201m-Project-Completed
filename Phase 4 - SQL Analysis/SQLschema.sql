-- ====================================================================
-- KỊCH BẢN TẠO CSDL VÀ BẢNG DUY NHẤT TRÊN MICROSOFT SQL SERVER
-- ĐỀ TÀI: DỰ ÁN KHOA HỌC DỮ LIỆU BÁO ĐIỆN TỬ VNEXPRESS (ADY201m)
-- ====================================================================

-- 1. Tạo Database ADY201m nếu chưa tồn tại
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'ADY201m')
BEGIN
    CREATE DATABASE ADY201m;
    PRINT N'[+] Đã tạo Database ADY201m thành công trên Microsoft SQL Server.';
END
ELSE
BEGIN
    PRINT N'[*] Database ADY201m đã tồn tại sẵn sàng.';
END
GO

USE ADY201m;
GO

-- 2. Tạo bảng duy nhất VnExpress_Articles (16 cột phân tích toàn diện)
IF OBJECT_ID(N'dbo.VnExpress_Articles', N'U') IS NOT NULL
BEGIN
    DROP TABLE dbo.VnExpress_Articles;
    PRINT N'[*] Đã xóa bảng cũ để tái thiết lập schema chuẩn 16 cột.';
END
GO

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
GO

-- 3. Tạo các chỉ mục (Indexes) hỗ trợ tối ưu hóa truy vấn
CREATE INDEX IX_Articles_Category ON dbo.VnExpress_Articles(category);
CREATE INDEX IX_Articles_Author ON dbo.VnExpress_Articles(author);
CREATE INDEX IX_Articles_PublishDate ON dbo.VnExpress_Articles(publish_date);
GO

PRINT N'[+] Hoàn tất thiết lập bảng dbo.VnExpress_Articles (16 cột) và Indexes trên Microsoft SQL Server!';
GO
