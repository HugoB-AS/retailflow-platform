from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.src.ml_utils import (
    MODEL_DIR,
    extract_feature_importance,
    load_customer_features,
    now_utc_iso,
    safe_joblib_dump,
    sigmoid,
    write_report,
)

FEATURES = [
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

MODEL_VERSION = "v2_realism"


def build_churn_label(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """
    Creates a more realistic synthetic churn target.

    Previous version used hard deterministic rules, which made ROC AUC = 1.0.
    This version keeps business logic but adds probabilistic uncertainty.
    """
    rng = np.random.default_rng(42)

    recency = np.clip(df["days_since_last_order"].fillna(0) / 365, 0, 2.5)
    cart_abandon = df["cart_abandon_rate"].fillna(0).clip(0, 1)
    return_rate = df["return_rate"].fillna(0).clip(0, 1)
    tickets = df["support_tickets_count"].fillna(0).clip(0, 10)
    orders = df["total_orders"].fillna(0).clip(0, 40)
    discount = df["discount_usage_rate"].fillna(0).clip(0, 1)
    pages = df["pages_viewed_30d"].fillna(0).clip(0, 200)

    engagement_penalty = np.where(pages < 8, 0.30, 0.0)
    random_noise = rng.normal(loc=0.0, scale=0.75, size=len(df))

    risk_score = (
        -2.10
        + 1.25 * recency
        + 0.95 * cart_abandon
        + 1.05 * return_rate
        + 0.18 * tickets
        - 0.035 * orders
        + 0.25 * discount
        + engagement_penalty
        + random_noise
    )

    churn_probability = pd.Series(
        np.clip(sigmoid(risk_score), 0.03, 0.92),
        index=df.index,
        name="synthetic_churn_probability",
    )

    churn_label = pd.Series(
        rng.binomial(1, churn_probability),
        index=df.index,
        name="synthetic_churn_label",
    )

    return churn_label, churn_probability


def get_candidate_models() -> dict:
    return {
        "logistic_regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                        random_state=42,
                    ),
                ),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=160,
            max_depth=7,
            min_samples_leaf=8,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=140,
            learning_rate=0.05,
            max_depth=3,
            random_state=42,
        ),
    }


def evaluate_classification(y_true, probabilities, threshold: float = 0.5) -> dict:
    predictions = (probabilities >= threshold).astype(int)

    return {
        "accuracy": accuracy_score(y_true, predictions),
        "precision": precision_score(y_true, predictions, zero_division=0),
        "recall": recall_score(y_true, predictions, zero_division=0),
        "f1": f1_score(y_true, predictions, zero_division=0),
        "roc_auc": roc_auc_score(y_true, probabilities),
        "brier_score": brier_score_loss(y_true, probabilities),
        "confusion_matrix": confusion_matrix(y_true, predictions).tolist(),
        "classification_report": classification_report(
            y_true,
            predictions,
            output_dict=True,
            zero_division=0,
        ),
    }


def benchmark_models(models: dict, X: pd.DataFrame, y: pd.Series) -> dict:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    scoring = {
        "roc_auc": "roc_auc",
        "f1": "f1",
        "precision": "precision",
        "recall": "recall",
        "accuracy": "accuracy",
    }

    results = {}

    for model_name, model in models.items():
        scores = cross_validate(
            model,
            X,
            y,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            error_score="raise",
        )

        results[model_name] = {
            "roc_auc_mean": float(np.mean(scores["test_roc_auc"])),
            "roc_auc_std": float(np.std(scores["test_roc_auc"])),
            "f1_mean": float(np.mean(scores["test_f1"])),
            "precision_mean": float(np.mean(scores["test_precision"])),
            "recall_mean": float(np.mean(scores["test_recall"])),
            "accuracy_mean": float(np.mean(scores["test_accuracy"])),
        }

    return results


def main():
    df = load_customer_features()
    df[FEATURES] = df[FEATURES].fillna(0)

    y, synthetic_probability = build_churn_label(df)
    X = df[FEATURES]

    class_counts = y.value_counts().sort_index().to_dict()
    positive_rate = float(y.mean())

    models = get_candidate_models()
    benchmark = benchmark_models(models, X, y)

    best_model_name = max(
        benchmark,
        key=lambda name: benchmark[name]["roc_auc_mean"],
    )
    best_base_model = models[best_model_name]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    uncalibrated_model = clone(best_base_model)
    uncalibrated_model.fit(X_train, y_train)
    uncalibrated_proba = uncalibrated_model.predict_proba(X_test)[:, 1]

    calibrated_model = CalibratedClassifierCV(
        estimator=clone(best_base_model),
        method="sigmoid",
        cv=3,
    )
    calibrated_model.fit(X_train, y_train)
    calibrated_proba = calibrated_model.predict_proba(X_test)[:, 1]

    uncalibrated_metrics = evaluate_classification(y_test, uncalibrated_proba)
    calibrated_metrics = evaluate_classification(y_test, calibrated_proba)

    importance_model = clone(best_base_model)
    importance_model.fit(X, y)
    feature_importance = extract_feature_importance(importance_model, FEATURES)

    report = {
        "generated_at": now_utc_iso(),
        "model_name": "churn_model",
        "model_version": MODEL_VERSION,
        "task_type": "binary_classification",
        "dataset_rows": int(len(df)),
        "features": FEATURES,
        "target_strategy": "probabilistic synthetic churn label with controlled business noise",
        "class_distribution": {
            "counts": {str(k): int(v) for k, v in class_counts.items()},
            "positive_rate": positive_rate,
        },
        "candidate_models": list(models.keys()),
        "cross_validation": {
            "folds": 5,
            "strategy": "StratifiedKFold",
            "results": benchmark,
        },
        "selected_model": best_model_name,
        "holdout_uncalibrated_metrics": uncalibrated_metrics,
        "holdout_calibrated_metrics": calibrated_metrics,
        "probability_calibration": {
            "enabled": True,
            "method": "sigmoid",
            "note": "The deployed churn model uses calibrated probabilities to avoid overconfident 0.99/1.00 outputs.",
        },
        "feature_importance": feature_importance,
        "risk_thresholds": {
            "high_risk": 0.70,
            "medium_risk": 0.40,
            "low_risk": 0.0,
        },
    }

    text_lines = [
        f"Rows: {len(df)}",
        f"Positive churn rate: {positive_rate:.4f}",
        f"Selected model: {best_model_name}",
        "",
        "Cross-validation results:",
    ]

    for model_name, metrics in benchmark.items():
        text_lines.append(
            f"- {model_name}: ROC AUC={metrics['roc_auc_mean']:.4f} "
            f"(std={metrics['roc_auc_std']:.4f}), F1={metrics['f1_mean']:.4f}"
        )

    text_lines.extend([
        "",
        "Holdout calibrated metrics:",
        f"- ROC AUC: {calibrated_metrics['roc_auc']:.4f}",
        f"- F1: {calibrated_metrics['f1']:.4f}",
        f"- Precision: {calibrated_metrics['precision']:.4f}",
        f"- Recall: {calibrated_metrics['recall']:.4f}",
        f"- Brier score: {calibrated_metrics['brier_score']:.4f}",
        "",
        "Top feature importance:",
    ])

    for row in feature_importance[:10]:
        text_lines.append(
            f"- {row['feature']}: {row['normalized_importance']:.4f}"
        )

    write_report(
        base_name="churn_model_report",
        title="Churn Model Report",
        report=report,
        text_lines=text_lines,
    )

    artifact = {
        "model": calibrated_model,
        "base_model_name": best_model_name,
        "features": FEATURES,
        "model_name": "churn_model",
        "model_version": MODEL_VERSION,
        "feature_importance": feature_importance,
        "report_path": "ml/reports/churn_model_report.json",
        "risk_thresholds": {
            "high_risk": 0.70,
            "medium_risk": 0.40,
        },
    }

    safe_joblib_dump(artifact, MODEL_DIR / "churn_model.joblib")

    print("Churn model report")
    print(f"Selected model: {best_model_name}")
    print(f"Positive churn rate: {positive_rate:.4f}")
    print(f"Calibrated ROC AUC: {calibrated_metrics['roc_auc']:.4f}")
    print(f"Calibrated F1: {calibrated_metrics['f1']:.4f}")
    print("Saved ml/models/churn_model.joblib")
    print("Saved ml/reports/churn_model_report.json")
    print("Saved ml/reports/churn_model_report.txt")


if __name__ == "__main__":
    main()
