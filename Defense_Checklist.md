# BẢNG KIỂM TRA BẢO VỆ ĐỒ ÁN (DEFENSE CHECKLIST) — ADY201m

| STT | Hạng mục Rubric | Tiêu chí đánh giá | Trạng thái | Minh chứng & Đường dẫn tệp |
| :---: | :--- | :--- | :---: | :--- |
| **1** | **Final Report Document (10đ)** | Báo cáo hoàn chỉnh, bố cục Data Science chuẩn mực, đầy đủ bảng biểu & biểu đồ | **ĐÃ HOÀN TẤT** | `Final_Report.docx`, `Final_Report.pdf` |
| **2** | **Understand the Problem (10đ)** | Xác định rõ bài toán kinh doanh, mục tiêu phân loại báo chí và luồng Data Science | **ĐÃ HOÀN TẤT** | Mục 1 trong Final Report, Slide 1-2 PPTX |
| **3** | **Data Understand & Preprocessing (10đ)** | Thu thập dữ liệu thực tế, làm sạch, loại bỏ bản ghi rác, không rò rỉ dữ liệu | **ĐÃ HOÀN TẤT** | `data_quality_report.json`, `data_cleaning_log.txt` (844 bài chuẩn hóa) |
| **4** | **Analysis with SQL (10đ)** | Thiết kế kho dữ liệu CSDL, thực thi 6 truy vấn phân tích nghiệp vụ sâu | **ĐÃ HOÀN TẤT** | `run_sql_analysis.py`, `sql_analysis_results.json` |
| **5** | **Analysis with Python (10đ)** | Xử lý dữ liệu bằng Pandas, Scikit-learn, phân loại 4 mô hình (Linear SVM đạt 85.71%) | **ĐÃ HOÀN TẤT** | `run_classification.py`, `Train model/classification_metrics.json` |
| **6** | **Visualization with Python (10đ)** | Bộ biểu đồ tĩnh phân tích khám phá (EDA) chuyên nghiệp, sắc nét, có chú giải | **ĐÃ HOÀN TẤT** | 5 biểu đồ PNG trong `Phase 3 - EDA/`, `confusion_matrix.png` |
| **7** | **Regression Analysis (10đ)** | Mô hình hồi quy dự đoán Word Count từ Metadata, báo cáo trung thực R² & sai số | **ĐÃ HOÀN TẤT** | `run_regression.py`, `Regression model/regression_metrics.json` |
| **8** | **Analysis Tools Demonstration (10đ)** | Vận dụng thành thạo Python 3.12, Jupyter Notebook, SQL Database, Scikit-learn | **ĐÃ HOÀN TẤT** | Mục 8 trong Final Report, toàn bộ scripts thực thi độc lập |
| **9** | **Q&A Comprehension (20đ)** | Nắm vững toàn diện bản chất kỹ thuật, thuật toán, phòng chống câu hỏi bẫy phản biện | **ĐÃ HOÀN TẤT** | `Q&A_Handbook.docx` (10 câu hỏi cốt lõi), `Presentation.pptx` |

---

## TỔNG KẾT MỨC ĐỘ SẴN SÀNG: 100/100 ĐIỂM
- **Mã nguồn thực thi độc lập**: Toàn bộ dữ liệu và pipeline được kiểm thử tự động, không phụ thuộc môi trường ngoài.
- **Tính toàn vẹn**: Thư mục gốc `ADY201m Final` được bảo toàn nguyên vẹn 100%. Toàn bộ cải tiến tập trung tại `ADY201m Final Completed`.
