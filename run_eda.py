import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    """Tải tập dữ liệu đã làm sạch."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "Phase 1 - Data crawl & Post process + Quick report", "vnexpress_data.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df["published_at"] = pd.to_datetime(df["published_at"])
    df["word_count"] = df["content"].fillna("").apply(lambda x: len(str(x).split()))
    df["hour"] = df["published_at"].dt.hour
    df["day_of_week"] = df["published_at"].dt.day_name()
    return df

def plot_eda_charts():
    """Tạo bộ biểu đồ phân tích khám phá dữ liệu (EDA) chuẩn mực."""
    plt.rcParams["font.family"] = "sans-serif"
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    
    df = load_data()
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Phase 3 - EDA")
    os.makedirs(out_dir, exist_ok=True)

    # 1. Phân bố bài viết theo chuyên mục
    plt.figure(figsize=(10, 6))
    cat_counts = df["category"].value_counts()
    ax = cat_counts.plot(kind="bar", color="#2b5c8f", edgecolor="black")
    plt.title("Phân bố số lượng bài viết theo Chuyên mục", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Chuyên mục", fontsize=11)
    plt.ylabel("Số lượng bài viết", fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    for p in ax.patches:
        ax.annotate(str(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha="center", va="bottom", fontsize=8, xytext=(0, 2), textcoords="offset points")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "bieu_do_1_chuyen_muc.png"), dpi=200)
    plt.close()

    # 2. Hoạt động xuất bản theo khung giờ trong ngày
    plt.figure(figsize=(10, 5))
    hour_counts = df["hour"].value_counts().sort_index()
    ax = hour_counts.plot(kind="line", marker="o", color="#d95f02", linewidth=2.5, markersize=6)
    plt.title("Tần suất xuất bản bài viết theo Khung giờ trong ngày (0h - 23h)", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Giờ trong ngày", fontsize=11)
    plt.ylabel("Số lượng bài viết xuất bản", fontsize=11)
    plt.xticks(range(0, 24))
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "bieu_do_2_phan_bo_gio.png"), dpi=200)
    plt.close()

    # 3. Phân bố độ dài bài viết (Word Count Distribution)
    plt.figure(figsize=(10, 5))
    sns.histplot(df["word_count"], kde=True, bins=35, color="#1b9e77", edgecolor="black")
    mean_wc = df["word_count"].mean()
    median_wc = df["word_count"].median()
    plt.axvline(mean_wc, color="red", linestyle="--", label=f"Trung bình: {mean_wc:.1f} từ")
    plt.axvline(median_wc, color="blue", linestyle=":", label=f"Trung vị: {median_wc:.1f} từ")
    plt.title("Phân bố độ dài bài viết (Số từ trong nội dung)", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Số từ", fontsize=11)
    plt.ylabel("Tần suất", fontsize=11)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "bieu_do_3_phan_bo_tu.png"), dpi=200)
    plt.close()

    # 4. Độ dài bài viết trung bình theo chuyên mục
    plt.figure(figsize=(11, 6))
    avg_len = df.groupby("category")["word_count"].mean().sort_values(ascending=False)
    ax = avg_len.plot(kind="barh", color="#7570b3", edgecolor="black")
    plt.title("Độ dài bài viết trung bình theo Chuyên mục", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Số từ trung bình", fontsize=11)
    plt.ylabel("Chuyên mục", fontsize=11)
    for p in ax.patches:
        ax.annotate(f"{p.get_width():.0f}", (p.get_width(), p.get_y() + p.get_height() / 2.),
                    ha="left", va="center", fontsize=8, xytext=(3, 0), textcoords="offset points")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "bieu_do_4_do_dai_chuyen_muc.png"), dpi=200)
    plt.close()

    # 5. Phân bố bài viết theo ngày trong tuần
    plt.figure(figsize=(9, 5))
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_counts = df["day_of_week"].value_counts().reindex(day_order).dropna()
    day_counts.plot(kind="bar", color="#e7298a", edgecolor="black")
    plt.title("Số lượng bài viết xuất bản theo các ngày trong tuần", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Thứ trong tuần", fontsize=11)
    plt.ylabel("Số lượng bài viết", fontsize=11)
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "bieu_do_5_ngay_trong_tuan.png"), dpi=200)
    plt.close()

    print("[+] Đã xuất đầy đủ 5 biểu đồ EDA chất lượng cao vào Phase 3 - EDA/")

if __name__ == "__main__":
    plot_eda_charts()
