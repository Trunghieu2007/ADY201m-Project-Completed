-- ====================================================================
-- BỘ 6 CÂU TRUY VẤN PHÂN TÍCH NGHIỆP VỤ TRÊN MICROSOFT SQL SERVER
-- BẢNG DUY NHẤT: dbo.VnExpress_Articles
-- ====================================================================

USE ADY201m;
GO

-- ====================================================================
-- PHẦN 0: CÁC CÂU LỆNH KIỂM TRA TÍNH ĐÚNG ĐẮN VÀ TOÀN VẸN CỦA DỮ LIỆU
-- ====================================================================

-- 0.1. Kiểm tra tổng số bản ghi :
SELECT COUNT(*) AS [Tổng số bài báo lưu trữ] 
FROM dbo.VnExpress_Articles;
GO

-- 0.2. Kiểm tra trùng lặp ID bài viết (kỳ vọng: 0 dòng - hoàn toàn không trùng lặp):
SELECT article_id, COUNT(*) AS [Số lần trùng lặp]
FROM dbo.VnExpress_Articles
GROUP BY article_id
HAVING COUNT(*) > 1;
GO

-- 0.3. Kiểm tra trường bị thiếu hoặc rỗng (kỳ vọng: 0 dòng - 100% dữ liệu sạch):
SELECT article_id, title, author, category
FROM dbo.VnExpress_Articles
WHERE title IS NULL OR title = '' 
   OR content IS NULL OR content = ''
   OR author IS NULL OR author = '';
GO

-- 0.4. Thống kê tổng quan dữ liệu lưu trữ :
SELECT 
    COUNT(*) AS total_articles,
    COUNT(DISTINCT category) AS total_categories,
    COUNT(DISTINCT author) AS total_authors,
    MIN(publish_date) AS earliest_date,
    MAX(publish_date) AS latest_date
FROM dbo.VnExpress_Articles;

-- ====================================================================
-- PHẦN 1: BỘ 6 CÂU TRUY VẤN PHÂN TÍCH NGHIỆP VỤ (Q1 -> Q6)
-- ====================================================================

-- Q1. Tổng số lượng bài viết đã được làm sạch và lưu trữ trong CSDL?
SELECT COUNT(*) AS total_articles 
FROM dbo.VnExpress_Articles;
GO

-- Q2. Thống kê số lượng bài viết và tỷ lệ phần trăm theo từng Chuyên mục?
SELECT 
    category, 
    COUNT(*) AS article_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dbo.VnExpress_Articles), 2) AS percentage
FROM dbo.VnExpress_Articles
GROUP BY category
ORDER BY article_count DESC;
GO

-- Q3. Đo lường độ dài bài viết trung bình, tối thiểu, tối đa và độ dài tiêu đề theo từng Chuyên mục?
SELECT 
    category, 
    COUNT(*) AS total_articles,
    ROUND(AVG(CAST(word_count AS FLOAT)), 1) AS avg_words,
    MIN(word_count) AS min_words,
    MAX(word_count) AS max_words,
    ROUND(AVG(CAST(title_length AS FLOAT)), 1) AS avg_title_words
FROM dbo.VnExpress_Articles
GROUP BY category
ORDER BY avg_words DESC;
GO

-- Q4. Top 10 bài viết có dung lượng từ lớn nhất kèm tác giả và chuyên mục?
SELECT TOP 10 
    article_id, 
    category, 
    title, 
    word_count, 
    author,
    published_at
FROM dbo.VnExpress_Articles
ORDER BY word_count DESC;
GO

-- Q5. Phân tích xu hướng xuất bản giữa Ngày trong tuần (Thứ 2 - Thứ 6) và Ngày cuối tuần (Thứ 7, Chủ nhật)?
SELECT 
    CASE WHEN is_weekend = 1 THEN N'Cuối tuần (T7, CN)' ELSE N'Ngày trong tuần (T2-T6)' END AS period_type,
    COUNT(*) AS total_articles,
    ROUND(AVG(CAST(word_count AS FLOAT)), 1) AS avg_words_per_article
FROM dbo.VnExpress_Articles
GROUP BY is_weekend
ORDER BY is_weekend ASC;
GO

-- Q6. Top 10 Tác giả / Phóng viên có nhiều bài viết nhất (ngoại trừ nhãn tòa soạn chung VnExpress)?
SELECT TOP 10 
    author,
    COUNT(*) AS total_published,
    ROUND(AVG(CAST(word_count AS FLOAT)), 1) AS avg_words
FROM dbo.VnExpress_Articles
WHERE author != N'VnExpress' AND author != ''
GROUP BY author
ORDER BY total_published DESC;
GO
