import os
import json
import pandas as pd
from datetime import datetime

def generate_data_quality_report():
    """Tạo báo cáo kiểm định chất lượng dữ liệu và xuất log chi tiết."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(base_dir, "Phase 1 - Data crawl & Post process + Quick report", "vnexpress_raw.json")
    clean_path = os.path.join(base_dir, "Phase 1 - Data crawl & Post process + Quick report", "vnexpress_data.json")

    with open(raw_path, "r", encoding="utf-8-sig") as f:
        raw_data = json.load(f)

    with open(clean_path, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    df_raw = pd.DataFrame(raw_data)
    df_clean = pd.DataFrame(clean_data)

    df_clean["word_count"] = df_clean["content"].fillna("").apply(lambda x: len(str(x).split()))

    stats = {
        "total_raw_records": len(df_raw),
        "total_clean_records": len(df_clean),
        "removed_records": len(df_raw) - len(df_clean),
        "missing_values_clean": df_clean.isnull().sum().to_dict(),
        "duplicate_clean_ids": int(df_clean.duplicated(subset=["article_id"]).sum()),
        "duplicate_clean_urls": int(df_clean.duplicated(subset=["url"]).sum()),
        "categories_count": int(df_clean["category"].nunique()),
        "categories_distribution": df_clean["category"].value_counts().to_dict(),
        "word_count_stats": {
            "min": int(df_clean["word_count"].min()),
            "max": int(df_clean["word_count"].max()),
            "mean": round(float(df_clean["word_count"].mean()), 2),
            "median": round(float(df_clean["word_count"].median()), 2),
            "std": round(float(df_clean["word_count"].std()), 2),
        },
        "date_range": {
            "earliest": str(df_clean["published_at"].min()),
            "latest": str(df_clean["published_at"].max())
        }
    }

    out_json = os.path.join(base_dir, "data_quality_report.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    log_path = os.path.join(base_dir, "data_cleaning_log.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("=== NHẬT KÝ LỌC VÀ LÀM SẠCH DỮ LIỆU VNEXPRESS ===\n")
        f.write(f"Thời gian tạo báo cáo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"1. Tổng số bản ghi thô (vnexpress_raw.json): {len(df_raw)}\n")
        f.write(f"2. Tổng số bản ghi sau làm sạch (vnexpress_data.json): {len(df_clean)}\n")
        f.write(f"3. Số bản ghi bị loại bỏ: {len(df_raw) - len(df_clean)}\n")
        f.write("4. Lý do loại bỏ quy chuẩn:\n")
        f.write("   - Thiếu tiêu đề (title rỗng hoặc null)\n")
        f.write("   - Không phải bài báo định dạng văn bản (og_type khác 'article'/'unknown')\n")
        f.write("   - Nội dung bài viết quá ngắn (< 50 từ, bài ảnh/video không có bài đọc)\n")
        f.write("   - Trùng lặp liên kết URL hoặc ID bài viết\n\n")
        f.write("5. Thống kê số lượng từ sau làm sạch:\n")
        f.write(f"   - Tối thiểu: {stats['word_count_stats']['min']} từ\n")
        f.write(f"   - Trung bình: {stats['word_count_stats']['mean']} từ\n")
        f.write(f"   - Tối đa: {stats['word_count_stats']['max']} từ\n")
        f.write(f"   - Độ lệch chuẩn: {stats['word_count_stats']['std']} từ\n\n")
        f.write(f"6. Phân bố chuyên mục ({stats['categories_count']} chuyên mục):\n")
        for cat, count in stats["categories_distribution"].items():
            f.write(f"   - {cat}: {count} bài\n")

    print("[+] Hoàn tất tạo data_quality_report.json và data_cleaning_log.txt")
    return stats

if __name__ == "__main__":
    generate_data_quality_report()
