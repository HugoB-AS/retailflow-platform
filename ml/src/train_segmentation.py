from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

from ml.src.ml_utils import (
    MODEL_DIR,
    load_customer_features,
    now_utc_iso,
    safe_joblib_dump,
    write_report,
)

FEATURES = [
    "total_orders",
    "total_spent",
    "avg_order_value",
    "days_since_last_order",
    "return_rate",
    "cart_abandon_rate",
    "support_tickets_count",
    "discount_usage_rate",
]

MODEL_VERSION = "v2_realism"


def evaluate_k_values(X_scaled: np.ndarray, k_values=range(3, 8)) -> dict:
    results = {}

    for k in k_values:
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        clusters = model.fit_predict(X_scaled)

        results[str(k)] = {
            "silhouette": float(silhouette_score(X_scaled, clusters)),
            "davies_bouldin": float(davies_bouldin_score(X_scaled, clusters)),
            "calinski_harabasz": float(calinski_harabasz_score(X_scaled, clusters)),
        }

    return results


def choose_best_k(k_results: dict) -> int:
    return int(max(k_results, key=lambda k: k_results[k]["silhouette"]))


def make_unique_label(label: str, used_labels: set[str]) -> str:
    if label not in used_labels:
        used_labels.add(label)
        return label

    suffix = 2
    while f"{label} {suffix}" in used_labels:
        suffix += 1

    final_label = f"{label} {suffix}"
    used_labels.add(final_label)
    return final_label


def assign_business_labels(cluster_summary: pd.DataFrame) -> tuple[dict, dict]:
    labels = {}
    descriptions = {}
    used_labels = set()

    max_spent_cluster = cluster_summary["total_spent"].idxmax()
    max_recency_cluster = cluster_summary["days_since_last_order"].idxmax()
    max_return_cluster = cluster_summary["return_rate"].idxmax()
    max_discount_cluster = cluster_summary["discount_usage_rate"].idxmax()
    min_recency_cluster = cluster_summary["days_since_last_order"].idxmin()

    for cluster_id, row in cluster_summary.iterrows():
        if cluster_id == max_spent_cluster:
            label = "High Value Loyal Customers"
            description = "Customers with the highest spending and strong purchase history."
        elif cluster_id == max_recency_cluster:
            label = "Dormant Low Value Customers"
            description = "Customers with long inactivity and weaker recent engagement."
        elif cluster_id == max_return_cluster:
            label = "Return-Prone Customers"
            description = "Customers with comparatively high return behavior."
        elif cluster_id == max_discount_cluster:
            label = "Promo-Sensitive Browsers"
            description = "Customers influenced by discounts and browsing/cart behavior."
        elif cluster_id == min_recency_cluster:
            label = "Recent Engaged Customers"
            description = "Customers with recent interactions and active behavior."
        else:
            label = "Standard Active Customers"
            description = "Customers with balanced activity and medium business value."

        final_label = make_unique_label(label, used_labels)
        labels[int(cluster_id)] = final_label
        descriptions[int(cluster_id)] = description

    return labels, descriptions


def main():
    df = load_customer_features()
    X = df[FEATURES].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    k_results = evaluate_k_values(X_scaled, k_values=range(3, 8))
    selected_k = choose_best_k(k_results)

    model = KMeans(n_clusters=selected_k, random_state=42, n_init=10)
    clusters = model.fit_predict(X_scaled)

    df_with_clusters = df.assign(cluster=clusters)

    cluster_summary = (
        df_with_clusters
        .groupby("cluster")[FEATURES]
        .mean()
        .round(2)
    )

    cluster_sizes = (
        df_with_clusters["cluster"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    segment_labels, segment_descriptions = assign_business_labels(cluster_summary)

    labeled_summary = []
    for cluster_id, row in cluster_summary.iterrows():
        labeled_summary.append({
            "cluster_id": int(cluster_id),
            "segment_label": segment_labels[int(cluster_id)],
            "segment_description": segment_descriptions[int(cluster_id)],
            "customers_count": int(cluster_sizes[int(cluster_id)]),
            **{feature: float(row[feature]) for feature in FEATURES},
        })

    report = {
        "generated_at": now_utc_iso(),
        "model_name": "segmentation_model",
        "model_version": MODEL_VERSION,
        "task_type": "clustering",
        "dataset_rows": int(len(df)),
        "features": FEATURES,
        "tested_k_values": list(range(3, 8)),
        "k_evaluation": k_results,
        "selected_k": selected_k,
        "selection_metric": "highest_silhouette",
        "segment_labels": segment_labels,
        "segment_descriptions": segment_descriptions,
        "cluster_summary": labeled_summary,
    }

    text_lines = [
        f"Rows: {len(df)}",
        f"Selected k: {selected_k}",
        "",
        "K evaluation:",
    ]

    for k, metrics in k_results.items():
        text_lines.append(
            f"- k={k}: silhouette={metrics['silhouette']:.4f}, "
            f"davies_bouldin={metrics['davies_bouldin']:.4f}, "
            f"calinski_harabasz={metrics['calinski_harabasz']:.2f}"
        )

    text_lines.extend(["", "Segments:"])

    for row in labeled_summary:
        text_lines.append(
            f"- cluster {row['cluster_id']} / {row['segment_label']}: "
            f"{row['customers_count']} customers"
        )

    write_report(
        base_name="segmentation_model_report",
        title="Segmentation Model Report",
        report=report,
        text_lines=text_lines,
    )

    artifact = {
        "model": model,
        "scaler": scaler,
        "features": FEATURES,
        "segment_labels": segment_labels,
        "segment_descriptions": segment_descriptions,
        "selected_k": selected_k,
        "model_name": "segmentation_model",
        "model_version": MODEL_VERSION,
        "report_path": "ml/reports/segmentation_model_report.json",
    }

    safe_joblib_dump(artifact, MODEL_DIR / "segmentation_model.joblib")

    print("Segmentation model")
    print(f"Selected k: {selected_k}")
    print(f"Silhouette score: {k_results[str(selected_k)]['silhouette']:.4f}")
    print(cluster_summary)
    print("Saved ml/models/segmentation_model.joblib")
    print("Saved ml/reports/segmentation_model_report.json")
    print("Saved ml/reports/segmentation_model_report.txt")


if __name__ == "__main__":
    main()
