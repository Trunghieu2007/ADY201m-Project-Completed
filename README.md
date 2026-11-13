# DỰ ÁN KHOA HỌC DỮ LIỆU BÁO ĐIỆN TỬ VNEXPRESS — ADY201m (BẢN HOÀN CHỈNH)

Dự án hoàn thành toàn diện các yêu cầu học thuật theo chuẩn Rubric môn học **Khoa học Dữ liệu Ứng dụng (ADY201m)** tại Đại học FPT.

---

## 1. CẤU TRÚC THƯ MỤC DỰ ÁN

```text
ADY201m Final Completed/
├── Final_Report.docx                 # Báo cáo tổng kết đồ án khoa học định dạng Word
├── Final_Report.pdf                  # Báo cáo tổng kết đồ án khoa học định dạng PDF
├── Presentation.pptx                 # Bộ slide thuyết trình bảo vệ đồ án chuẩn mực
├── Q&A_Handbook.docx                 # Cẩm nang câu hỏi - đáp vấn đáp bảo vệ đồ án
├── Defense_Checklist.md              # Bảng đối soát 100% tiêu chí Rubric môn học
├── data_quality_report.json          # Báo cáo thống kê kiểm định chất lượng dữ liệu
├── data_cleaning_log.txt             # Nhật ký chi tiết quy trình sàng lọc và làm sạch
├── sql_analysis_results.json         # Kết quả thực thi 6 câu truy vấn phân tích SQL
├── generate_data_quality.py          # Script kiểm tra chất lượng dữ liệu
├── run_eda.py                        # Script xuất 5 biểu đồ EDA chất lượng cao
├── run_sql_analysis.py               # Script khởi tạo CSDL và chạy phân tích SQL
├── run_classification.py             # Script huấn luyện & so sánh 4 mô hình phân loại
├── run_regression.py                 # Script huấn luyện & đánh giá mô hình hồi quy
├── Phase 1 - Data crawl.../          # Bộ dữ liệu thô và tập dữ liệu chuẩn hóa (844 bài)
├── Phase 2 - Import data to SQL/     # Cơ sở dữ liệu SQL & câu lệnh truy vấn mẫu
├── Phase 3 - EDA/                    # 5 biểu đồ phân tích khám phá dữ liệu trực quan
├── Train model/                      # Mô hình phân loại tối ưu (Linear SVM 85.71%) & TF-IDF
└── Regression model/                 # Mô hình hồi quy dự đoán Word Count & biểu đồ sai số
```

---

## 2. HƯỚNG DẪN THỰC THI TOÀN BỘ PIPELINE

Dự án được thiết kế độc lập, có thể tái lập kết quả dễ dàng bằng Python 3.12:

```bash
# 1. Kiểm tra và xuất báo cáo chất lượng dữ liệu:
python generate_data_quality.py

# 2. Sinh toàn bộ biểu đồ phân tích khám phá dữ liệu (EDA):
python run_eda.py

# 3. Khởi tạo cơ sở dữ liệu và thực thi phân tích SQL:
python run_sql_analysis.py

# 4. Huấn luyện và đánh giá 4 mô hình Phân loại văn bản:
python run_classification.py

# 5. Huấn luyện và đánh giá mô hình Hồi quy dự đoán dung lượng bài:
python run_regression.py
```

---

## 3. TỔNG HỢP KẾT QUẢ THỰC NGHIỆM

### A. Kiểm định Dữ liệu (Data Quality)
- **Tổng số bài thô**: 859 bài.
- **Tổng số bài chuẩn sau lọc**: 844 bài thuộc 19 chuyên mục.
- **Tỷ lệ Missing values & Duplicates**: 0% (Toàn vẹn tuyệt đối).
- **Độ dài bài viết**: Ngắn nhất 59 từ, dài nhất 3,084 từ, trung bình 759.2 từ.

### B. Hiệu năng Mô hình Phân loại Thể loại Tin tức (Classification)
| Thuật toán | Accuracy | Precision | Recall | Macro F1 | Weighted F1 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Linear SVM (Mô hình chọn)** | **85.71%** | **85.34%** | **85.71%** | **83.69%** | **84.54%** |
| Logistic Regression | 83.33% | 83.65% | 83.33% | 80.20% | 81.45% |
| Multinomial Naive Bayes | 81.55% | 81.82% | 81.55% | 78.47% | 79.99% |
| Decision Tree | 62.50% | 63.85% | 62.50% | 62.15% | 62.42% |

### C. Hiệu năng Mô hình Hồi quy Dung lượng Bài viết (Regression)
- **Mục tiêu**: Dự đoán `word_count` dựa trên Metadata (giờ xuất bản, ngày trong tuần, cuối tuần, số từ tóm tắt, tiêu đề, thể loại).
- **Ridge Regression**: MAE = 271.92 từ, RMSE = 377.69 từ, $R^2$ = 0.1316.
- **Nhận định khoa học**: Kết quả phản ánh trung thực bản chất dữ liệu báo chí (không có quan hệ tuyến tính chặt chẽ giữa siêu dữ liệu và độ dài sự kiện). Không bị Data Leakage.
