import os
import sys
import time
import subprocess

def log_step(phase_num, phase_name):
    """Ghi nhật ký bước thực thi."""
    print("\n" + "=" * 70)
    print(f" GIAI ĐOẠN {phase_num}: {phase_name.upper()}")
    print("=" * 70)

def run_script(script_path, description):
    """Chạy một file script python và kiểm tra mã thoát."""
    print(f"[*] Đang thực thi: {description} ({script_path})...")
    start_t = time.time()
    res = subprocess.run([sys.executable, script_path], capture_output=False, text=True)
    if res.returncode != 0:
        print(f"\n[!] LỖI TẠI BƯỚC: {description} (Exit code: {res.returncode})")
        sys.exit(res.returncode)
    elapsed = round(time.time() - start_t, 2)
    print(f"[+] Thành công trong {elapsed} giây.\n")

def main():
    """Điểm nhập duy nhất thực thi toàn bộ pipeline đồ án từ đầu đến cuối."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    total_start = time.time()

    print("=" * 70)
    print(" CHƯƠNG TRÌNH THỰC THI TOÀN DIỆN DỰ ÁN KHOA HỌC DỮ LIỆU ADY201m")
    print("=" * 70)

    # Giai đoạn 1: Thu thập dữ liệu
    log_step(1, "Thu thập Dữ liệu Tươi từ VnExpress (Data Collection)")
    script_p1 = os.path.join(base_dir, "Phase 1 - Data Collection", "crawl_vnexpress.py")
    raw_json = os.path.join(base_dir, "data", "raw", "vnexpress_raw.json")
    if not os.path.exists(raw_json):
        run_script(script_p1, "Cào dữ liệu tươi VnExpress")
    else:
        print(f"[*] Đã tồn tại tập dữ liệu thô: {raw_json}")
        print("    (Nếu muốn cào mới hoàn toàn, hãy xóa file vnexpress_raw.json hoặc chạy riêng script crawl_vnexpress.py)")

    # Giai đoạn 2: Tiền xử lý & Kiểm định chất lượng
    log_step(2, "Tiền xử lý và Kiểm định Chất lượng Dữ liệu (Preprocessing & Data Quality)")
    script_p2 = os.path.join(base_dir, "Phase 2 - Data Preprocessing & Quality", "clean_and_validate.py")
    run_script(script_p2, "Làm sạch và kiểm định chất lượng dữ liệu")

    # Giai đoạn 3: Phân tích Khám phá Dữ liệu (EDA)
    log_step(3, "Phân tích Khám phá Dữ liệu Trực quan (Exploratory Data Analysis)")
    script_p3 = os.path.join(base_dir, "Phase 3 - Exploratory Data Analysis", "run_eda.py")
    run_script(script_p3, "Xuất bản 5 biểu đồ EDA trực quan")

    # Giai đoạn 4: Phân tích CSDL SQL
    log_step(4, "Phân tích Dữ liệu bằng Hệ CSDL SQL (SQL Analysis)")
    script_p4 = os.path.join(base_dir, "Phase 4 - SQL Analysis", "run_sql_analysis.py")
    run_script(script_p4, "Thực thi 6 câu truy vấn CSDL SQL")

    # Giai đoạn 5: Mô hình Phân loại Văn bản
    log_step(5, "Huấn luyện & Đánh giá Mô hình Phân loại Văn bản (Classification Modeling)")
    script_p5 = os.path.join(base_dir, "Phase 5 - Classification Modeling", "train_classifier.py")
    run_script(script_p5, "So sánh 4 mô hình phân loại (Linear SVM, Logistic, Naive Bayes, Decision Tree)")

    # Giai đoạn 6: Mô hình Hồi quy
    log_step(6, "Huấn luyện & Đánh giá Mô hình Hồi quy (Regression Modeling)")
    script_p6 = os.path.join(base_dir, "Phase 6 - Regression Modeling", "train_regression.py")
    run_script(script_p6, "Hồi quy dự đoán dung lượng bài viết từ siêu dữ liệu")

    # Giai đoạn 7: Xuất tài liệu Báo cáo & Slide
    log_step(7, "Xuất bản Hồ sơ Báo cáo Khoa học (Documentation & Reports)")
    script_p7 = os.path.join(base_dir, "Phase 7 - Documentation & Reports", "build_reports.py")
    run_script(script_p7, "Tạo Final_Report.docx, Final_Report.pdf, Presentation.pptx và Q&A_Handbook.docx")

    total_elapsed = round(time.time() - total_start, 2)
    print("=" * 70)
    print(f" TẤT CẢ CÁC GIAI ĐOẠN ĐÃ HOÀN TẤT THÀNH CÔNG TRONG {total_elapsed} GIÂY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
