import os
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

def train_and_evaluate_classifiers(clean_path=None, output_dir=None):
    """Huấn luyện và so sánh đa mô hình phân loại thể loại bài báo (Category Classification)."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if clean_path is None:
        clean_path = os.path.join(base_dir, "data", "processed", "vnexpress_clean.json")
    if output_dir is None:
        output_dir = os.path.join(base_dir, "Phase 5 - Classification Modeling")
    os.makedirs(output_dir, exist_ok=True)

    with open(clean_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    total_clean_samples = len(df)
    cat_counts = df["category"].value_counts()
    
    # Chỉ giữ các chuyên mục có tối thiểu 10 bài viết để đảm bảo tính phân tầng (Stratified Split)
    valid_categories = cat_counts[cat_counts >= 10].index.tolist()
    excluded_categories = cat_counts[cat_counts < 10].to_dict()
    df_filtered = df[df["category"].isin(valid_categories)].copy()

    df_filtered["text_feature"] = (
        df_filtered["title"].fillna("") + " " + 
        df_filtered["description"].fillna("") + " " + 
        df_filtered["content"].fillna("")
    )

    X = df_filtered["text_feature"]
    y = df_filtered["category"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    vectorizer = TfidfVectorizer(max_features=4000, ngram_range=(1, 2), min_df=2)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    models = {
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.1),
        "Decision Tree": DecisionTreeClassifier(max_depth=30, random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=1000, C=1.0, random_state=42),
        "Linear SVM": LinearSVC(C=1.0, random_state=42, dual="auto")
    }

    metrics_summary = {}
    fitted_models = {}

    for name, model in models.items():
        model.fit(X_train_vec, y_train)
        y_pred = model.predict(X_test_vec)
        fitted_models[name] = model

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)
        f1_weighted = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        metrics_summary[name] = {
            "accuracy": round(float(acc), 4),
            "precision_weighted": round(float(prec), 4),
            "recall_weighted": round(float(rec), 4),
            "f1_macro": round(float(f1_macro), 4),
            "f1_weighted": round(float(f1_weighted), 4),
        }

    best_model_name = max(metrics_summary, key=lambda k: metrics_summary[k]["f1_weighted"])
    best_model = fitted_models[best_model_name]
    y_pred_best = best_model.predict(X_test_vec)

    # 1. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred_best, labels=best_model.classes_)
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=best_model.classes_, yticklabels=best_model.classes_)
    plt.title(f"Confusion Matrix - Best Classifier: {best_model_name} (Accuracy: {metrics_summary[best_model_name]['accuracy']*100:.1f}%)",
              fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Dự đoán (Predicted Category)", fontsize=11)
    plt.ylabel("Thực tế (Actual Category)", fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    cm_path = os.path.join(output_dir, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=200)
    plt.close()

    # 2. Bar Chart Model Comparison
    plt.figure(figsize=(10, 5))
    df_metrics = pd.DataFrame(metrics_summary).T[["accuracy", "f1_macro", "f1_weighted"]]
    ax = df_metrics.plot(kind="bar", figsize=(10, 5), colormap="viridis", edgecolor="black")
    plt.title("So sánh hiệu năng giữa 4 thuật toán Phân loại Văn bản", fontsize=13, fontweight="bold", pad=12)
    plt.ylabel("Điểm số", fontsize=11)
    plt.xticks(rotation=15, ha="right")
    plt.ylim(0, 1.05)
    plt.legend(["Accuracy", "Macro F1", "Weighted F1"], loc="lower right")
    plt.tight_layout()
    bar_path = os.path.join(output_dir, "model_comparison_bar.png")
    plt.savefig(bar_path, dpi=200)
    plt.close()

    joblib.dump(best_model, os.path.join(output_dir, "category_classifier_model.joblib"))
    joblib.dump(vectorizer, os.path.join(output_dir, "tfidf_vectorizer.joblib"))

    results_payload = {
        "dataset_total_clean_samples": total_clean_samples,
        "modeling_samples_used": len(df_filtered),
        "excluded_sparse_categories": excluded_categories,
        "train_samples_count": len(X_train),
        "test_samples_count": len(X_test),
        "num_classes": len(best_model.classes_),
        "classes": list(best_model.classes_),
        "models_evaluation": metrics_summary,
        "best_model": best_model_name,
        "detailed_classification_report": classification_report(y_test, y_pred_best, output_dict=True, zero_division=0)
    }

    out_metrics_json = os.path.join(output_dir, "classification_metrics.json")
    with open(out_metrics_json, "w", encoding="utf-8") as f:
        json.dump(results_payload, f, ensure_ascii=False, indent=2)

    print("[+] HOÀN TẤT HUẤN LUYỆN VÀ ĐÁNH GIÁ MÔ HÌNH PHÂN LOẠI:")
    for m_name, res in metrics_summary.items():
        print(f"    - {m_name}: Accuracy = {res['accuracy']:.4f}, Weighted F1 = {res['f1_weighted']:.4f}")
    print(f"    - Mô hình tốt nhất: {best_model_name}")
    print(f"    - Tệp chỉ số đánh giá: {out_metrics_json}")
    return results_payload

if __name__ == "__main__":
    train_and_evaluate_classifiers()
