from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ml.src.ml_utils import (
    REPORT_DIR,
    load_customer_features,
    now_utc_iso,
    safe_write_json,
    write_report,
)

DRIFT_THRESHOLD = 0.20

DRIFT_FEATURES = [
    "total_orders",
    "total_spent",
    "avg_order_value",
    "days_since_last_order",
    "return_rate",
    "cart_abandon_rate",
    "session_count_30d",
    "pages_viewed_30d",
    "support_tickets_count",
    "avg_rating_given",
    "discount_usage_rate",
]


def simulate_current_dataset(reference_df: pd.DataFrame) -> pd.DataFrame:
    """
    Lightweight ML drift simulation.

    This is not a full production drift monitor.
    It creates a controlled current dataset to demonstrate how drift would be detected.
    """
    rng = np.random.default_rng(42)
    current = reference_df.copy()

    drift_plan = {
        "avg_order_value": 1.25,
        "days_since_last_order": 1.30,
        "cart_abandon_rate": 1.12,
        "return_rate": 1.15,
        "discount_usage_rate": 1.20,
    }

    for feature, multiplier in drift_plan.items():
        if feature in current.columns:
            noise = rng.normal(loc=1.0, scale=0.04, size=len(current))
            current[feature] = current[feature].fillna(0) * multiplier * noise

    for bounded_feature in ["cart_abandon_rate", "return_rate", "discount_usage_rate"]:
        if bounded_feature in current.columns:
            current[bounded_feature] = current[bounded_feature].clip(0, 1)

    return current


def calculate_drift(reference_df: pd.DataFrame, current_df: pd.DataFrame) -> list[dict]:
    rows = []

    for feature in DRIFT_FEATURES:
        if feature not in reference_df.columns or feature not in current_df.columns:
            continue

        ref = reference_df[feature].fillna(0).astype(float)
        cur = current_df[feature].fillna(0).astype(float)

        ref_mean = float(ref.mean())
        cur_mean = float(cur.mean())
        ref_std = float(ref.std())
        cur_std = float(cur.std())

        denominator = abs(ref_mean) if abs(ref_mean) > 1e-9 else 1.0
        relative_mean_change = (cur_mean - ref_mean) / denominator

        rows.append({
            "feature": feature,
            "reference_mean": ref_mean,
            "current_mean": cur_mean,
            "reference_std": ref_std,
            "current_std": cur_std,
            "relative_mean_change": float(relative_mean_change),
            "absolute_relative_mean_change": float(abs(relative_mean_change)),
            "drift_detected": bool(abs(relative_mean_change) >= DRIFT_THRESHOLD),
            "threshold": DRIFT_THRESHOLD,
        })

    return sorted(
        rows,
        key=lambda row: row["absolute_relative_mean_change"],
        reverse=True,
    )


def load_optional_report(path: Path):
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def build_model_summary(drift_report: dict) -> dict:
    churn_report = load_optional_report(REPORT_DIR / "churn_model_report.json")
    clv_report = load_optional_report(REPORT_DIR / "clv_model_report.json")
    segmentation_report = load_optional_report(REPORT_DIR / "segmentation_model_report.json")

    summary = {
        "generated_at": now_utc_iso(),
        "project": "RetailFlow",
        "summary_type": "ml_model_summary",
        "churn": {
            "available": churn_report is not None,
        },
        "clv": {
            "available": clv_report is not None,
        },
        "segmentation": {
            "available": segmentation_report is not None,
        },
        "drift": {
            "available": True,
            "drift_detected": drift_report["overall"]["drift_detected"],
            "drifted_features_count": drift_report["overall"]["drifted_features_count"],
            "threshold": drift_report["overall"]["threshold"],
        },
    }

    if churn_report:
        summary["churn"].update({
            "model_version": churn_report.get("model_version"),
            "selected_model": churn_report.get("selected_model"),
            "roc_auc": churn_report.get("holdout_calibrated_metrics", {}).get("roc_auc"),
            "f1": churn_report.get("holdout_calibrated_metrics", {}).get("f1"),
            "positive_rate": churn_report.get("class_distribution", {}).get("positive_rate"),
        })

    if clv_report:
        summary["clv"].update({
            "model_version": clv_report.get("model_version"),
            "selected_model": clv_report.get("selected_model"),
            "mae": clv_report.get("holdout_metrics", {}).get("mae"),
            "rmse": clv_report.get("holdout_metrics", {}).get("rmse"),
            "r2": clv_report.get("holdout_metrics", {}).get("r2"),
        })

    if segmentation_report:
        summary["segmentation"].update({
            "model_version": segmentation_report.get("model_version"),
            "selected_k": segmentation_report.get("selected_k"),
            "selection_metric": segmentation_report.get("selection_metric"),
        })

    return summary


def main():
    reference_df = load_customer_features()
    current_df = simulate_current_dataset(reference_df)

    drift_rows = calculate_drift(reference_df, current_df)
    drifted_features = [row for row in drift_rows if row["drift_detected"]]

    report = {
        "generated_at": now_utc_iso(),
        "report_name": "lightweight_ml_drift_report",
        "method": "synthetic current dataset simulation with relative mean-change threshold",
        "threshold": DRIFT_THRESHOLD,
        "reference_rows": int(len(reference_df)),
        "current_rows": int(len(current_df)),
        "features": DRIFT_FEATURES,
        "overall": {
            "drift_detected": bool(len(drifted_features) > 0),
            "drifted_features_count": int(len(drifted_features)),
            "threshold": DRIFT_THRESHOLD,
        },
        "feature_drift": drift_rows,
        "production_note": (
            "This is a lightweight demonstration. In production, current datasets should "
            "come from real periodic snapshots and trigger alerts or retraining when drift is detected."
        ),
    }

    text_lines = [
        f"Reference rows: {len(reference_df)}",
        f"Current rows: {len(current_df)}",
        f"Threshold: {DRIFT_THRESHOLD:.0%}",
        f"Drift detected: {report['overall']['drift_detected']}",
        f"Drifted features: {len(drifted_features)}",
        "",
        "Feature drift:",
    ]

    for row in drift_rows:
        flag = "DRIFT" if row["drift_detected"] else "OK"
        text_lines.append(
            f"- {row['feature']}: {row['relative_mean_change']:.2%} [{flag}]"
        )

    write_report(
        base_name="drift_report",
        title="Lightweight ML Drift Report",
        report=report,
        text_lines=text_lines,
    )

    model_summary = build_model_summary(report)
    safe_write_json(REPORT_DIR / "model_summary.json", model_summary)

    print("Lightweight ML drift report")
    print(f"Drift detected: {report['overall']['drift_detected']}")
    print(f"Drifted features: {len(drifted_features)}")
    print("Saved ml/reports/drift_report.json")
    print("Saved ml/reports/drift_report.txt")
    print("Saved ml/reports/model_summary.json")


if __name__ == "__main__":
    main()
