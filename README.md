# HỆ THỐNG PHÂN TÍCH & HỌC MÁY TRÊN DỮ LIỆU BÁO ĐIỆN TỬ VNEXPRESS (ADY201m)

Dự án hoàn chỉnh đạt chuẩn Rubric môn học **Khoa học Dữ liệu Ứng dụng (ADY201m)** tại Đại học FPT. Toàn bộ mã nguồn, dữ liệu tươi, mô hình học máy và tài liệu báo cáo được chuẩn hóa theo quy trình khoa học dữ liệu khép kín, có thể chạy lại từ đầu đến cuối chỉ với một lệnh duy nhất.

---

## 1. TỔNG QUAN VÀ MỤC TIÊU DỰ ÁN

- **Bối cảnh thực tế**: Khai phá tin tức báo điện tử VnExpress – trang tin trực tuyến số 1 Việt Nam.
- **Mục tiêu học thuật**:
  1. Thu thập dữ liệu tươi tự động từ 16 chuyên mục RSS trong phạm vi 7 ngày gần nhất.
  2. Kiểm định chất lượng toàn diện (Strict Data Quality): loại bỏ hoàn toàn bài rác/media, 0% missing values, 0% empty strings, 0% trùng lặp, nhận diện tác giả thực tế.
  3. Khám phá trực quan (EDA) với bộ biểu đồ độ phân giải cao và phân tích nghiệp vụ sâu.
  4. Lưu trữ kho dữ liệu quan hệ và thực thi 6 câu truy vấn SQL quản trị nội dung.
  5. Phân loại chuyên mục tự động bằng TF-IDF kết hợp đa mô hình học máy (Linear SVM, Logistic Regression, Naive Bayes, Decision Tree).
  6. Xây dựng mô hình hồi quy dự đoán độ dài bài viết dựa trên siêu dữ liệu (Metadata), phòng chống rò rỉ dữ liệu (No Data Leakage).
  7. Xuất bản toàn bộ hồ sơ nghiệm thu: Báo cáo Word/PDF, Slide thuyết trình PPTX, Cẩm nang hỏi đáp bảo vệ (Q&A Handbook).

---

## 2. CẤU TRÚC THƯ MỤC CHUẨN HÓA THEO GIAI ĐOẠN

```text
ADY201m-Project-Completed/
├── run_all_pipeline.py                     # Entry point duy nhất chạy toàn bộ 7 giai đoạn
├── requirements.txt                        # Danh mục thư viện Python yêu cầu
├── README.md                               # Tài liệu hướng dẫn và báo cáo kết quả
├── Defense_Checklist.md                   # Bảng kiểm tra 100/100 điểm Rubric
│
├── Phase 1 - Data Collection/
│   ├── crawl_vnexpress.py                  # Script cào đa luồng 16 chuyên mục RSS
│   └── vnexpress_raw.json                  # [ĐẦU RA GIAI ĐOẠN 1] Dữ liệu cào thô (672 bài)
│
├── Phase 2 - Data Preprocessing & Quality/
│   ├── clean_and_validate.py               # Làm sạch, kiểm định rỗng/khuyết/trùng lặp
│   ├── vnexpress_clean.json                # [ĐẦU RA GIAI ĐOẠN 2] Dữ liệu đã làm sạch & chuẩn hóa
│   ├── data_quality_report.json            # Thống kê chi tiết chất lượng dữ liệu
│   └── data_cleaning_log.txt               # Nhật ký loại bỏ bản ghi
│
├── Phase 3 - Exploratory Data Analysis/
│   ├── run_eda.py                          # Sinh 5 biểu đồ trực quan hóa dữ liệu
│   ├── bieu_do_1_chuyen_muc.png            # Phân bố số lượng bài theo chuyên mục
│   ├── bieu_do_2_phan_bo_gio.png           # Phân bố theo khung giờ xuất bản
│   ├── bieu_do_3_phan_bo_tu.png            # Phân bố độ dài bài viết (Histogram/KDE)
│   ├── bieu_do_4_do_dai_chuyen_muc.png     # Độ dài trung bình theo chuyên mục
│   └── bieu_do_5_top_tac_gia.png           # Top 10 phóng viên tích cực nhất
│
├── Phase 4 - SQL Analysis/
│   ├── run_sql_analysis.py                 # Khởi tạo CSDL SQLite & chạy 6 truy vấn
│   ├── vnexpress_analysis.db               # Cơ sở dữ liệu quan hệ SQLite
│   └── sql_analysis_results.json           # Kết quả thực thi 6 câu truy vấn SQL
│
├── Phase 5 - Classification Modeling/
│   ├── train_classifier.py                 # Huấn luyện & đánh giá 4 mô hình phân loại
│   ├── category_classifier_model.joblib    # Mô hình tối ưu lưu trữ (Linear SVM)
│   ├── tfidf_vectorizer.joblib             # Bộ vector hóa TF-IDF (4000 n-grams)
│   ├── confusion_matrix.png                # Ma trận nhầm lẫn
│   ├── model_comparison_bar.png            # Đồ thị so sánh các thuật toán
│   └── classification_metrics.json         # Chỉ số đo lường chi tiết
│
├── Phase 6 - Regression Modeling/
│   ├── train_regression.py                 # Hồi quy dự đoán dung lượng bài (word count)
│   ├── article_word_count_regressor.joblib # Mô hình hồi quy lưu trữ
│   ├── regression_actual_vs_predicted.png  # Đồ thị Thực tế vs Dự đoán
│   ├── regression_residuals_plot.png       # Đồ thị phần dư (Residuals)
│   ├── regression_comparison_bar.png       # So sánh sai số các mô hình
│   └── regression_metrics.json             # Bảng đo lường MAE, RMSE, R²
│
├── Phase 7 - Documentation & Reports/
│   ├── build_reports.py                    # Script tự động tạo DOCX, PPTX và PDF
│   ├── Final_Report.docx                   # Báo cáo tổng kết 14 mục chuẩn học thuật
│   ├── Final_Report.pdf                    # Bản xuất PDF chính thức
│   ├── Presentation.pptx                   # Bộ slide thuyết trình bảo vệ đồ án
│   └── Q&A_Handbook.docx                   # Cẩm nang 10 câu hỏi đáp phản biện
│
├── Final_Report.docx                       # File báo cáo tại thư mục gốc
├── Final_Report.pdf                        # File PDF tại thư mục gốc
├── Presentation.pptx                       # File slide tại thư mục gốc
└── Q&A_Handbook.docx                       # File Q&A tại thư mục gốc
```

---

## 3. HƯỚNG DẪN THỰC THI (CHO BẢN CLONE MỚI)

### Bước 1: Clone repository và cài đặt thư viện
```bash
git clone https://github.com/Trunghieu2007/ADY201m-Project-Completed.git
cd ADY201m-Project-Completed
pip install -r requirements.txt
pip install python-docx python-pptx docx2pdf reportlab
```

### Bước 2: Chạy toàn bộ quy trình tự động từ đầu đến cuối
Chỉ cần thực thi một lệnh duy nhất:
```bash
python run_all_pipeline.py
```
*Lệnh này sẽ tuần tự kiểm tra dữ liệu, tiền xử lý, xuất biểu đồ EDA, thực thi SQL, huấn luyện phân loại, huấn luyện hồi quy và tự động biên dịch lại toàn bộ Báo cáo DOCX, Slide PPTX và Báo cáo PDF trong khoảng ~40 giây.*

---

## 4. KẾT QUẢ THỰC NGHIỆM ĐỢT THU THẬP TƯƠI (FRESH BATCH)

### A. Kiểm định Chất lượng Dữ liệu (Data Quality Verification)
- **Tổng số bài cào thô (vnexpress_raw.json)**: 672 bài viết trong 7 ngày gần nhất.
- **Tổng số bài sau làm sạch (vnexpress_clean.json)**: 659 bài viết đạt chuẩn (loại 13 bài media ảnh/video dưới 50 từ).
- **Kiểm định khuyết/rỗng/trùng lặp**:
  - Null Values: **0 bản ghi** ở tất cả các trường.
  - Empty Strings: **0 bản ghi** ở tất cả các trường.
  - Duplicate IDs / URLs: **0 bản ghi**.
- **Đặc trưng độ dài**: Ngắn nhất 51 từ, trung bình 746.2 từ, dài nhất 3,248 từ.
- **Số lượng tác giả nhận diện**: 227 tác giả/bút danh độc nhất.

### B. Hiệu năng Mô hình Phân loại Thể loại Báo chí (Text Classification)
- Mẫu dữ liệu sử dụng: 660 bài thuộc 16 lớp chuyên mục (Stratified Split: 528 bài train, 132 bài test).
- Đặc trưng: TF-IDF 4,000 từ khóa quan trọng, n-gram (1, 2).
- So sánh hiệu năng thực tế trên cùng tập kiểm thử:

| Mô hình Phân loại | Accuracy | Precision | Recall | Macro F1 | Weighted F1 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Linear SVM (Mô hình tốt nhất)** | **84.09%** | **84.97%** | **84.09%** | **82.35%** | **84.03%** |
| Logistic Regression | 76.52% | 76.62% | 76.52% | 74.03% | 75.47% |
| Multinomial Naive Bayes | 76.52% | 76.99% | 76.52% | 74.45% | 75.46% |
| Decision Tree | 46.97% | 49.62% | 46.97% | 47.01% | 47.55% |

### C. Hiệu năng Mô hình Hồi quy Dự đoán Dung lượng Bài viết (Regression)
- Biến mục tiêu: `word_count` (Tính từ nội dung thân bài).
- Biến đầu vào: Metadata (Số từ tiêu đề, Số từ mô tả, Khung giờ xuất bản, Thứ trong tuần, Cuối tuần, One-Hot Encoding chuyên mục). Tuyệt đối **không bị rò rỉ dữ liệu (No Data Leakage)**.
- Kết quả đo lường:
  - **Linear Regression**: MAE = 306.44 từ, RMSE = 452.06 từ, $R^2$ = 0.1606.
  - **Ridge Regression**: MAE = 307.28 từ, RMSE = 452.99 từ, $R^2$ = 0.1572.
  - **Random Forest**: MAE = 314.07 từ, RMSE = 470.74 từ, $R^2$ = 0.0898.
- **Nhận định khoa học**: Hệ số $R^2 \approx 0.16$ phản ánh trung thực bản chất dữ liệu khách quan. Độ dài bài báo thực tế phụ thuộc trực tiếp vào tính thời sự và quy mô sự việc, siêu dữ liệu chỉ giải thích được một phần phương sai. Nhóm báo cáo trung thực giới hạn học thuật thay vì ngụy tạo dữ liệu.

---

## 5. GIỚI HẠN VÀ HƯỚNG PHÁT TRIỂN
- Dữ liệu thu thập theo chu kỳ tuần (7 ngày) phản ánh nhịp độ tin tức tức thời.
- Để nâng cao độ chính xác phân loại ngữ nghĩa tiếng Việt đa tầng, hướng phát triển tương lai có thể tích hợp mô hình ngôn ngữ tiền huấn luyện PhởBERT / Transformer.
