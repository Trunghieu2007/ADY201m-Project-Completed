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

def run_classification_pipeline():
    """Huấn luyện và so sánh đa mô hình phân loại văn bản (Category Classification)."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "Phase 1 - Data crawl & Post process + Quick report", "vnexpress_data.json")
    out_dir = os.path.join(base_dir, "Train model")
    os.makedirs(out_dir, exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    cat_counts = df["category"].value_counts()
    valid_categories = cat_counts[cat_counts >= 10].index.tolist()
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

    cm = confusion_matrix(y_test, y_pred_best, labels=best_model.classes_)
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=best_model.classes_, yticklabels=best_model.classes_)
    plt.title(f"Confusion Matrix - Best Model: {best_model_name} (Acc: {metrics_summary[best_model_name]['accuracy']*100:.1f}%)",
              fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Dự đoán (Predicted Category)", fontsize=11)
    plt.ylabel("Thực tế (Actual Category)", fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    cm_path = os.path.join(out_dir, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=200)
    plt.close()

    plt.figure(figsize=(10, 5))
    df_metrics = pd.DataFrame(metrics_summary).T[["accuracy", "f1_macro", "f1_weighted"]]
    ax = df_metrics.plot(kind="bar", figsize=(10, 5), colormap="viridis", edgecolor="black")
    plt.title("So sánh hiệu năng giữa các thuật toán Phân loại Văn bản", fontsize=13, fontweight="bold", pad=12)
    plt.ylabel("Điểm số", fontsize=11)
    plt.xticks(rotation=15, ha="right")
    plt.ylim(0, 1.05)
    plt.legend(["Accuracy", "Macro F1", "Weighted F1"], loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "model_comparison_bar.png"), dpi=200)
    plt.close()

    joblib.dump(best_model, os.path.join(out_dir, "category_classifier_model.joblib"))
    joblib.dump(vectorizer, os.path.join(out_dir, "tfidf_vectorizer.joblib"))

    results_payload = {
        "dataset_size": len(df_filtered),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "num_classes": len(best_model.classes_),
        "classes": list(best_model.classes_),
        "models_evaluation": metrics_summary,
        "best_model": best_model_name,
        "detailed_classification_report": classification_report(y_test, y_pred_best, output_dict=True, zero_division=0)
    }

    metrics_json_path = os.path.join(out_dir, "classification_metrics.json")
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(results_payload, f, ensure_ascii=False, indent=2)

    print("[+] Hoàn tất huấn luyện 4 mô hình phân loại:")
    for m_name, res in metrics_summary.items():
        print(f"    - {m_name}: Accuracy={res['accuracy']:.4f}, Weighted F1={res['f1_weighted']:.4f}")
    print(f"[+] Mô hình tốt nhất được chọn: {best_model_name}")
    return results_payload

if __name__ == "__main__":
    run_classification_pipeline()
