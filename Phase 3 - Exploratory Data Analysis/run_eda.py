import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(clean_path=None):
    """Nạp tập dữ liệu bài viết sạch và tạo các biến phái sinh cho EDA."""
    if clean_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        clean_path = os.path.join(base_dir, "data", "processed", "vnexpress_clean.json")
    with open(clean_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df["published_at"] = pd.to_datetime(df["published_at"])
    df["hour"] = df["published_at"].dt.hour
    df["day_of_week"] = df["published_at"].dt.day_name()
    return df

def generate_eda_visualizations(clean_path=None, output_dir=None):
    """Xuất bản bộ 5 biểu đồ EDA phân tích dữ liệu trực quan chất lượng cao."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if output_dir is None:
        output_dir = os.path.join(base_dir, "Phase 3 - Exploratory Data Analysis")
    os.makedirs(output_dir, exist_ok=True)

    plt.rcParams["font.family"] = "sans-serif"
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    df = load_data(clean_path)

    # 1. Phân bố bài viết theo chuyên mục
    plt.figure(figsize=(10, 6))
    cat_counts = df["category"].value_counts()
    ax = cat_counts.plot(kind="bar", color="#2b5c8f", edgecolor="black")
    plt.title("Phân bố số lượng bài viết theo Chuyên mục (Đợt dữ liệu tươi)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Chuyên mục", fontsize=11)
    plt.ylabel("Số lượng bài viết", fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    for p in ax.patches:
        ax.annotate(str(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha="center", va="bottom", fontsize=8, xytext=(0, 2), textcoords="offset points")
    plt.tight_layout()
    chart1_path = os.path.join(output_dir, "bieu_do_1_chuyen_muc.png")
    plt.savefig(chart1_path, dpi=200)
    plt.close()

    # 2. Hoạt động xuất bản theo khung giờ trong ngày
    plt.figure(figsize=(10, 5))
    hour_counts = df["hour"].value_counts().sort_index()
    ax = hour_counts.plot(kind="line", marker="o", color="#d95f02", linewidth=2.5, markersize=6)
    plt.title("Tần suất xuất bản bài viết theo Khung giờ trong ngày (0h - 23h)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Khung giờ trong ngày", fontsize=11)
    plt.ylabel("Số lượng bài viết xuất bản", fontsize=11)
    plt.xticks(range(0, 24))
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    chart2_path = os.path.join(output_dir, "bieu_do_2_phan_bo_gio.png")
    plt.savefig(chart2_path, dpi=200)
    plt.close()

    # 3. Phân bố độ dài bài viết (Word Count Distribution)
    plt.figure(figsize=(10, 5))
    sns.histplot(df["word_count"], kde=True, bins=35, color="#1b9e77", edgecolor="black")
    mean_wc = df["word_count"].mean()
    median_wc = df["word_count"].median()
    plt.axvline(mean_wc, color="red", linestyle="--", label=f"Trung bình: {mean_wc:.1f} từ")
    plt.axvline(median_wc, color="blue", linestyle=":", label=f"Trung vị: {median_wc:.1f} từ")
    plt.title("Phân bố độ dài bài viết (Số từ trong thân bài)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Số từ (Word count)", fontsize=11)
    plt.ylabel("Số lượng bài viết", fontsize=11)
    plt.legend(fontsize=10)
    plt.tight_layout()
    chart3_path = os.path.join(output_dir, "bieu_do_3_phan_bo_tu.png")
    plt.savefig(chart3_path, dpi=200)
    plt.close()

    # 4. Độ dài bài viết trung bình theo chuyên mục
    plt.figure(figsize=(11, 6))
    avg_len = df.groupby("category")["word_count"].mean().sort_values(ascending=False)
    ax = avg_len.plot(kind="barh", color="#7570b3", edgecolor="black")
    plt.title("Độ dài bài viết trung bình theo Chuyên mục (Từ dài nhất đến ngắn nhất)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Số từ trung bình", fontsize=11)
    plt.ylabel("Chuyên mục", fontsize=11)
    for p in ax.patches:
        ax.annotate(f"{p.get_width():.0f}", (p.get_width(), p.get_y() + p.get_height() / 2.),
                    ha="left", va="center", fontsize=8, xytext=(3, 0), textcoords="offset points")
    plt.tight_layout()
    chart4_path = os.path.join(output_dir, "bieu_do_4_do_dai_chuyen_muc.png")
    plt.savefig(chart4_path, dpi=200)
    plt.close()

    # 5. Phân bố tác giả thực tế (Top Authors Distribution)
    plt.figure(figsize=(10, 5))
    top_authors = df[df["author"] != "VnExpress"]["author"].value_counts().head(10)
    if len(top_authors) > 0:
        ax = top_authors.plot(kind="bar", color="#e7298a", edgecolor="black")
        plt.title("Top 10 Tác giả / Phóng viên có nhiều bài viết nhất (Ngoại trừ tòa soạn)", fontsize=13, fontweight="bold", pad=12)
        plt.xlabel("Tác giả / Bút danh phóng viên", fontsize=11)
        plt.ylabel("Số lượng bài viết", fontsize=11)
        plt.xticks(rotation=35, ha="right", fontsize=9)
        for p in ax.patches:
            ax.annotate(str(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha="center", va="bottom", fontsize=8, xytext=(0, 2), textcoords="offset points")
    plt.tight_layout()
    chart5_path = os.path.join(output_dir, "bieu_do_5_top_tac_gia.png")
    plt.savefig(chart5_path, dpi=200)
    plt.close()

    print(f"[+] HOÀN TẤT XUẤT 5 BIỂU ĐỒ EDA TẠI: {output_dir}")
    return output_dir

if __name__ == "__main__":
    generate_eda_visualizations()
