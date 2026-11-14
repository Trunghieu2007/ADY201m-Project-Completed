# DỰ ÁN KHOA HỌC DỮ LIỆU: MÔ TẢ & PHÂN LOẠI DỮ LIỆU BÁO ĐIỆN TỬ VNEXPRESS (ADY201m)

Báo cáo dự án môn học **Khoa học Dữ liệu Ứng dụng (ADY201m)** tại Đại học FPT. Toàn bộ mã nguồn, dữ liệu thực nghiệm, mô hình học máy và tài liệu báo cáo được chuẩn hóa theo các giai đoạn nghiên cứu khoa học dữ liệu, phục vụ việc đánh giá và tái lập kết quả.

---

## THÀNH VIÊN VÀ PHÂN CÔNG NHIỆM VỤ

| STT | Họ và Tên | Vai trò & Chức năng phụ trách | Trách nhiệm cụ thể trong dự án |
| :---: | :--- | :--- | :--- |
| **1** | **Phạm Hùng Dương (He210543)** | **Kỹ sư Thu thập Dữ liệu (Data Engineer)** | - Thiết kế và vận hành module cào dữ liệu VnExpress (`Phase 1`).<br>- Xây dựng quy trình sàng lọc chất lượng, tiền xử lý và loại trừ dữ liệu rác (`Phase 2`). |
| **2** | **Đinh Trung Hiếu (He210442)** | **Chuyên viên Phân tích Dữ liệu (Data Analyst)** | - Khám phá và trực quan hóa dữ liệu thống kê mô tả (EDA) (`Phase 3`).<br>- Xây dựng mô hình Cơ sở dữ liệu Microsoft SQL Server (dbo.VnExpress_Articles) và thực thi truy vấn phân tích SQL (`Phase 4`). |
| **3** | **Nguyễn Hữu Hùng (He210370)** | **Kỹ sư Học máy (Machine Learning Engineer)** | - Trích xuất đặc trưng TF-IDF và huấn luyện mô hình Phân loại văn bản (`Phase 5`).<br>- Xây dựng mô hình Hồi quy dự đoán dung lượng bài viết từ siêu dữ liệu (`Phase 6`). |

---

## 1. TỔNG QUAN VÀ MỤC TIÊU DỰ ÁN

- **Đối tượng nghiên cứu**: Dữ liệu tin tức báo điện tử VnExpress thu thập từ 16 chuyên mục chính thống trong vòng 7 ngày gần nhất.
- **Mục tiêu nghiên cứu**:
  1. Thu thập dữ liệu báo chí có cấu trúc từ hệ thống RSS feeds của VnExpress.
  2. Kiểm định chất lượng dữ liệu: xác định và loại trừ các bản ghi không phù hợp (nội dung rác, video/photo story thiếu văn bản, thiếu tiêu đề).
  3. Phân tích khám phá dữ liệu (EDA) và trực quan hóa phân bố chuyên mục, thời gian xuất bản, dung lượng từ và danh tính tác giả.
  4. Quản lý dữ liệu tập trung trên hệ quản trị CSDL Microsoft SQL Server (1 bảng chuẩn hóa `dbo.VnExpress_Articles`) và hỗ trợ phân tích nghiệp vụ.
  5. Đánh giá và so sánh thực nghiệm 4 mô hình phân loại văn bản: Linear SVM, Logistic Regression, Multinomial Naive Bayes, Decision Tree trên không gian đặc trưng TF-IDF.
  6. Thử nghiệm mô hình hồi quy (Linear Regression, Ridge Regression, Random Forest) dự đoán dung lượng bài viết dựa trên siêu dữ liệu xuất bản (Metadata), bảo đảm không xảy ra hiện tượng rò rỉ dữ liệu (Data Leakage).

---

## 2. CẤU TRÚC THƯ MỤC DỰ ÁN

```text
ADY201m-Project-Completed/
├── requirements.txt                        # Danh mục thư viện Python yêu cầu
├── README.md                               # Hướng dẫn thực thi và báo cáo kết quả
├── Final_Report.docx                       # Báo cáo tổng kết đồ án khoa học
├── ProfessorRequirement.txt                # Yêu cầu đề bài và rubric môn học
│
├── Phase 1 - Data Collection/
│   ├── crawl_vnexpress.py                  # Module thu thập dữ liệu 16 chuyên mục RSS
│   └── vnexpress_raw.json                  # Dữ liệu cào thô (672 bài viết)
│
├── Phase 2 - Data Preprocessing & Quality/
│   ├── clean_and_validate.py               # Module tiền xử lý và kiểm định tính toàn vẹn
│   ├── vnexpress_clean.json                # Dữ liệu sạch sau tiền xử lý (655 bài viết)
│   ├── data_quality_report.json            # Thống kê chi tiết chất lượng dữ liệu
│   └── data_cleaning_log.txt               # Nhật ký loại trừ các bản ghi không đạt chuẩn
│
├── Phase 3 - Exploratory Data Analysis/
│   ├── run_eda.py                          # Module trực quan hóa dữ liệu EDA
│   ├── bieu_do_1_chuyen_muc.png            # Biểu đồ số lượng bài theo chuyên mục
│   ├── bieu_do_2_phan_bo_gio.png           # Biểu đồ tần suất xuất bản theo khung giờ
│   ├── bieu_do_3_phan_bo_tu.png            # Biểu đồ phân bố độ dài bài viết
│   ├── bieu_do_4_do_dai_chuyen_muc.png     # Biểu đồ độ dài trung bình theo thể loại
│   └── bieu_do_5_top_tac_gia.png           # Biểu đồ Top 10 tác giả/phóng viên
│
├── Phase 4 - SQL Analysis/
│   ├── run_sql_analysis.py                 # Module khởi tạo CSDL và nạp dữ liệu vào Microsoft SQL Server (bảng dbo.VnExpress_Articles)
│   ├── SQLschema.sql                       # Kịch bản T-SQL khởi tạo Database ADY201m và bảng dbo.VnExpress_Articles
│   ├── DemoTruyVan.sql                     # Kịch bản 6 câu lệnh T-SQL phân tích dữ liệu mẫu
│   └── sql_analysis_results.json           # Kết quả thực thi bộ truy vấn T-SQL trên Microsoft SQL Server
│
├── Phase 5 - Classification Modeling/
│   ├── train_classifier.py                 # Module huấn luyện và đánh giá 4 mô hình phân loại
│   ├── category_classifier_model.joblib    # Trọng số mô hình Linear SVM lưu trữ
│   ├── tfidf_vectorizer.joblib             # Bộ vector hóa TF-IDF (4000 n-grams)
│   ├── confusion_matrix.png                # Ma trận nhầm lẫn (Confusion Matrix)
│   ├── model_comparison_bar.png            # Biểu đồ so sánh các thuật toán phân loại
│   └── classification_metrics.json         # Chi tiết các chỉ số Accuracy, Precision, Recall, F1
│
└── Phase 6 - Regression Modeling/
    ├── train_regression.py                 # Module huấn luyện và đánh giá mô hình hồi quy
    ├── article_word_count_regressor.joblib # Trọng số mô hình hồi quy lưu trữ
    ├── regression_actual_vs_predicted.png  # Biểu đồ Thực tế vs Dự đoán
    ├── regression_residuals_plot.png       # Biểu đồ phân bố phần dư (Residuals Plot)
    ├── regression_comparison_bar.png       # Biểu đồ so sánh sai số MAE & RMSE giữa các mô hình
    └── regression_metrics.json             # Bảng đo lường sai số và hệ số xác định R²
```

---

## 3. HƯỚNG DẪN THỰC THI THEO TỪNG GIAI ĐOẠN

### Bước 1: Chuẩn bị môi trường
```bash
git clone https://github.com/Trunghieu2007/ADY201m-Project-Completed.git
cd ADY201m-Project-Completed
pip install -r requirements.txt
```

### Bước 2: Chạy độc lập từng giai đoạn

```bash
# Giai đoạn 1: Thu thập dữ liệu từ VnExpress (chỉ chạy khi muốn cào đợt mới)
python "Phase 1 - Data Collection\crawl_vnexpress.py"

# Giai đoạn 2: Tiền xử lý, loại bỏ bản ghi rác và kiểm tra tính toàn vẹn
python "Phase 2 - Data Preprocessing & Quality\clean_and_validate.py"

# Giai đoạn 3: Phân tích khám phá dữ liệu trực quan (xuất 5 biểu đồ PNG)
python "Phase 3 - Exploratory Data Analysis\run_eda.py"

# Giai đoạn 4: Tạo CSDL Microsoft SQL Server và nạp bảng dữ liệu chuẩn hóa
python "Phase 4 - SQL Analysis\run_sql_analysis.py"

# Giai đoạn 5: Huấn luyện và đánh giá mô hình phân loại văn bản (4 thuật toán)
python "Phase 5 - Classification Modeling\train_classifier.py"

# Giai đoạn 6: Huấn luyện và đánh giá mô hình hồi quy dung lượng bài viết
python "Phase 6 - Regression Modeling\train_regression.py"
```

---

## 4. KẾT QUẢ THỰC NGHIỆM VÀ ĐÁNH GIÁ

### A. Kiểm định Chất lượng Dữ liệu (Data Quality)
- **Quy mô thu thập**: 672 bài viết thô từ 16 chuyên mục RSS trong 7 ngày gần nhất.
- **Quy mô sau tiền xử lý**: 655 bài viết đạt chuẩn (loại 17 bài có dung lượng dưới 50 từ hoặc bài ảnh/video không có văn bản).
- **Kiểm tra tính toàn vẹn**:
  - Giá trị Null: 0 trường hợp.
  - Chuỗi rỗng (Empty String): 0 trường hợp.
  - Trùng lặp (Duplicate ID/URL): 0 trường hợp.
- **Nhận diện tác giả**: Bóc tách danh tính của 226 tác giả và bút danh phóng viên chuyên trách thay vì nhãn mặc định tòa soạn.

---

### B. Thiết kế Cơ sở Dữ liệu SQL (Microsoft SQL Server & Bảng đơn `dbo.VnExpress_Articles`)

Dự án sử dụng hệ quản trị cơ sở dữ liệu quan hệ **Microsoft SQL Server** (kết nối trực tiếp tới `localhost\SQLEXPRESS`, database `ADY201m`) qua giao thức ODBC (`pyodbc`) với chuẩn T-SQL. Toàn bộ 655 bài báo sạch được lưu trữ và truy vấn hoàn toàn trên bảng `dbo.VnExpress_Articles` gồm 16 cột thuộc tính chuẩn hóa.

Toàn bộ dữ liệu được tổ chức chuẩn hóa trong một bảng duy nhất `dbo.VnExpress_Articles` gồm 16 cột thuộc tính:

| STT | Tên Cột (Column Name) | Kiểu Dữ Liệu (MSSQL) | Ràng Buộc | Ý Nghĩa Phân Tích & Chức Năng Nghiệp Vụ |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | `article_id` | `VARCHAR(100)` | `PRIMARY KEY` | Mã định danh duy nhất của bài viết được trích xuất từ liên kết bài báo VnExpress. |
| **2** | `title` | `NVARCHAR(500)` | `NOT NULL` | Tiêu đề bài viết, đại diện cho nội dung tóm lược ngắn gọn nhất. |
| **3** | `description` | `NVARCHAR(MAX)` | `NULL` | Phần mô tả tóm tắt (sapo) nằm đầu mỗi bài báo. |
| **4** | `content` | `NVARCHAR(MAX)` | `NOT NULL` | Toàn bộ văn bản thân bài báo (sau khi đã ghép các đoạn paragraph). |
| **5** | `author` | `NVARCHAR(200)` | `NOT NULL` | Tên tác giả hoặc bút danh phóng viên phụ trách bài viết. |
| **6** | `published_at` | `DATETIME` | `NOT NULL` | Mốc thời gian xuất bản bài viết theo định dạng chuẩn `YYYY-MM-DD HH:MM:SS`. |
| **7** | `publish_date` | `DATE` | `NOT NULL` | Ngày xuất bản bài viết (`YYYY-MM-DD`), phục vụ nhóm dữ liệu theo ngày. |
| **8** | `publish_hour` | `INT` | `INTEGER` | `NOT NULL` | Khung giờ xuất bản trong ngày (từ 0 đến 23), dùng để phân tích hoạt động theo giờ. |
| **9** | `publish_dayofweek`| `NVARCHAR(20)` | `NOT NULL` | Thứ trong tuần (`Monday`, `Tuesday`...), phục vụ phân tích xu hướng theo thứ. |
| **10**| `is_weekend` | `TINYINT` | `INTEGER` | `NOT NULL` | Biến nhị phân đánh dấu ngày cuối tuần (1: Thứ Bảy/Chủ Nhật, 0: Ngày làm việc). |
| **11**| `category` | `NVARCHAR(100)` | `NOT NULL` | Chuyên mục tin tức chính (Thời sự, Kinh doanh, Thế giới, Thể thao...). |
| **12**| `subcategory` | `NVARCHAR(100)` | `NULL` | Tiểu mục chi tiết của chuyên mục chính (nếu có). |
| **13**| `url` | `VARCHAR(500)` | `NOT NULL` | Đường dẫn liên kết trực tiếp tới trang bài viết trên VnExpress. |
| **14**| `word_count` | `INT` | `INTEGER` | `NOT NULL` | Tổng số lượng từ trong phần thân bài báo (`content`). |
| **15**| `title_length` | `INT` | `INTEGER` | `NOT NULL` | Số lượng từ trong tiêu đề bài viết (`title`). |
| **16**| `desc_length` | `INT` | `INTEGER` | `NOT NULL` | Số lượng từ trong phần mô tả tóm tắt (`description`). |

**Chỉ mục tối ưu hóa (Indexes)**:
- `idx_articles_category`: Tối ưu hóa các truy vấn `GROUP BY category` và lọc theo thể loại.
- `idx_articles_author`: Tối ưu hóa truy vấn thống kê sản lượng bài viết theo tác giả.
- `idx_articles_pubdate`: Hỗ trợ lọc và tổng hợp nhanh bài viết theo mốc thời gian.

**Các tệp kịch bản T-SQL đi kèm**:
- `SQLschema.sql`: Kịch bản DDL tạo cơ sở dữ liệu `ADY201m`, thiết lập bảng `dbo.VnExpress_Articles` cùng các chỉ mục.
- `DemoTruyVan.sql`: Kịch bản 6 câu lệnh truy vấn mẫu từ thống kê phân loại, lọc bài dài, tính sản lượng tác giả tới phân bố xuất bản theo ngày và khung giờ.

---

### C. Hiệu năng Mô hình Phân loại Văn bản (Text Classification)
- Tập dữ liệu: 655 bài báo, sử dụng Stratified Splitting (80% Huấn luyện, 20% Kiểm thử) trên các chuyên mục có từ 10 bài trở lên.
- Trích xuất đặc trưng: TF-IDF với 4,000 từ khóa (n-gram 1-2).
- Kết quả so sánh trên tập kiểm thử độc lập:

| Thuật toán | Accuracy | Precision (Weighted) | Recall (Weighted) | Macro F1 | Weighted F1 | Đánh giá |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Linear SVM** | **83.21%** | **84.15%** | **83.21%** | **80.52%** | **81.66%** | Phân tách không gian đặc trưng thưa số chiều cao hiệu quả nhất |
| Multinomial Naive Bayes | 77.10% | 77.58% | 77.10% | 75.12% | 75.19% | Phù hợp với giả định phân bố xác suất từ vựng |
| Logistic Regression | 73.28% | 73.15% | 73.28% | 69.84% | 70.03% | Độ ổn định khá tốt |
| Decision Tree | 52.67% | 53.40% | 52.67% | 51.10% | 51.46% | Dễ xảy ra hiện tượng quá khớp trên dữ liệu văn bản thưa |

---

### D. Hiệu năng Mô hình Hồi quy (Regression Analysis)
- Biến mục tiêu: `word_count` (Số từ của nội dung bài báo).
- Biến giải thích: Metadata xuất bản (`title_length`, `desc_length`, `publish_hour`, `publish_dayofweek`, `is_weekend`, One-Hot Encoding `category`).
- Đảm bảo phòng chống rò rỉ dữ liệu (No Data Leakage): Không sử dụng các biến số phái sinh từ nội dung thân bài để làm đầu vào dự đoán.
- Kết quả đo lường sai số:

| Thuật toán Hồi quy | MAE (Số từ) | RMSE (Số từ) | Hệ số xác định $R^2$ |
| :--- | :---: | :---: | :---: |
| **Ridge Regression** | **306.18** | **441.09** | **0.1554** |
| Linear Regression | 306.43 | 441.15 | 0.1552 |
| Random Forest Regressor | 322.82 | 478.69 | 0.0053 |

- **Nhận định thực nghiệm**: Hệ số $R^2 \approx 0.155$ phản ánh tính chất thực tế của dữ liệu báo chí: độ dài bài báo phụ thuộc chủ yếu vào quy mô diễn biến của sự kiện đời thực và ý đồ biên tập của phóng viên, các thông tin siêu dữ liệu chỉ giải thích được một phần biến thiên này.

---

## 5. GIỚI HẠN VÀ HƯỚNG PHÁT TRIỂN
- Dữ liệu thu thập phản ánh chu kỳ tin tức trong khung thời gian 7 ngày.
- Trong tương lai, mô hình phân loại có thể mở rộng thử nghiệm với các kiến trúc học sâu và mô hình ngôn ngữ tiếng Việt (như PhởBERT) để khai thác thêm thông tin ngữ cảnh.
