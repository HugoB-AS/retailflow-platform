from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.src.ml_utils import (
    MODEL_DIR,
    extract_feature_importance,
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
    "session_count_30d",
    "pages_viewed_30d",
    "support_tickets_count",
    "avg_rating_given",
    "discount_usage_rate",
]

MODEL_VERSION = "v2_realism"


def build_clv_target(df: pd.DataFrame) -> pd.Series:
    """
    Creates a realistic synthetic CLV target.

    Previous target was too deterministic and easy for RandomForest to learn.
    This version preserves business logic but injects controlled uncertainty.
    """
    rng = np.random.default_rng(42)

    recency_factor = np.clip(1 - (df["days_since_last_order"].fillna(0) / 420), 0.10, 1.15)

    loyalty_factor = df["loyalty_status"].map({
        "new": 0.75,
        "bronze": 0.90,
        "silver": 1.00,
        "gold": 1.20,
        "platinum": 1.45,
    }).fillna(1.0)

    engagement_factor = np.clip(
        1
        + (df["session_count_30d"].fillna(0) / 35)
        + (df["pages_viewed_30d"].fillna(0) / 180)
        - (df["cart_abandon_rate"].fillna(0) * 0.55),
        0.45,
        1.75,
    )

    penalty_factor = np.clip(
        1
        - (df["return_rate"].fillna(0) * 0.75)
        - (df["support_tickets_count"].fillna(0) * 0.025),
        0.45,
        1.05,
    )

    deterministic_clv = (
        df["total_spent"].fillna(0) * 0.38 * recency_factor * loyalty_factor
        + df["avg_order_value"].fillna(0) * engagement_factor * 1.8
    ) * penalty_factor

    noise_multiplier = rng.normal(loc=1.0, scale=0.22, size=len(df))
    additive_noise = rng.normal(
        loc=0.0,
        scale=max(float(df["avg_order_value"].fillna(0).std()), 100.0),
        size=len(df),
    )

    clv = deterministic_clv * noise_multiplier + additive_noise

    return pd.Series(np.clip(clv, 0, None).round(2), index=df.index, name="synthetic_clv")


def get_candidate_models() -> dict:
    return {
        "linear_regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("model", LinearRegression()),
            ]
        ),
        "random_forest": RandomForestRegressor(
            n_estimators=160,
            max_depth=7,
            min_samples_leaf=8,
            random_state=42,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingRegressor(
            n_estimators=160,
            learning_rate=0.05,
            max_depth=3,
            random_state=42,
        ),
    }


def benchmark_models(models: dict, X: pd.DataFrame, y: pd.Series) -> dict:
    cv = KFold(n_splits=5, shuffle=True, random_state=42)

    scoring = {
        "mae": "neg_mean_absolute_error",
        "mse": "neg_mean_squared_error",
        "r2": "r2",
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

        mae_values = -scores["test_mae"]
        mse_values = -scores["test_mse"]
        r2_values = scores["test_r2"]

        results[model_name] = {
            "mae_mean": float(np.mean(mae_values)),
            "mae_std": float(np.std(mae_values)),
            "rmse_mean": float(np.sqrt(np.mean(mse_values))),
            "r2_mean": float(np.mean(r2_values)),
            "r2_std": float(np.std(r2_values)),
        }

    return results


def evaluate_regression(y_true, preds) -> dict:
    return {
        "mae": float(mean_absolute_error(y_true, preds)),
        "rmse": float(mean_squared_error(y_true, preds) ** 0.5),
        "r2": float(r2_score(y_true, preds)),
    }


def main():
    df = load_customer_features()
    df[FEATURES] = df[FEATURES].fillna(0)

    y = build_clv_target(df)
    X = df[FEATURES]

    models = get_candidate_models()
    benchmark = benchmark_models(models, X, y)

    best_model_name = min(
        benchmark,
        key=lambda name: benchmark[name]["mae_mean"],
    )
    best_model_template = models[best_model_name]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
    )

    holdout_model = clone(best_model_template)
    holdout_model.fit(X_train, y_train)
    holdout_preds = holdout_model.predict(X_test)
    holdout_metrics = evaluate_regression(y_test, holdout_preds)

    final_model = clone(best_model_template)
    final_model.fit(X, y)

    feature_importance = extract_feature_importance(final_model, FEATURES)

    target_summary = {
        "mean": float(y.mean()),
        "median": float(y.median()),
        "min": float(y.min()),
        "max": float(y.max()),
        "std": float(y.std()),
    }

    report = {
        "generated_at": now_utc_iso(),
        "model_name": "clv_model",
        "model_version": MODEL_VERSION,
        "task_type": "regression",
        "dataset_rows": int(len(df)),
        "features": FEATURES,
        "target_strategy": "synthetic CLV formula with controlled business noise",
        "target_summary": target_summary,
        "candidate_models": list(models.keys()),
        "cross_validation": {
            "folds": 5,
            "strategy": "KFold",
            "selection_metric": "lowest_mae_mean",
            "results": benchmark,
        },
        "selected_model": best_model_name,
        "holdout_metrics": holdout_metrics,
        "feature_importance": feature_importance,
        "clv_band_thresholds": {
            "high_value": 10000,
            "medium_value": 3000,
            "low_value": 0,
        },
    }

    text_lines = [
        f"Rows: {len(df)}",
        f"Selected model: {best_model_name}",
        "",
        "Target summary:",
        f"- mean: {target_summary['mean']:.2f}",
        f"- median: {target_summary['median']:.2f}",
        f"- std: {target_summary['std']:.2f}",
        "",
        "Cross-validation results:",
    ]

    for model_name, metrics in benchmark.items():
        text_lines.append(
            f"- {model_name}: MAE={metrics['mae_mean']:.2f} "
            f"(std={metrics['mae_std']:.2f}), RMSE={metrics['rmse_mean']:.2f}, "
            f"R2={metrics['r2_mean']:.4f}"
        )

    text_lines.extend([
        "",
        "Holdout metrics:",
        f"- MAE: {holdout_metrics['mae']:.2f}",
        f"- RMSE: {holdout_metrics['rmse']:.2f}",
        f"- R2: {holdout_metrics['r2']:.4f}",
        "",
        "Top feature importance:",
    ])

    for row in feature_importance[:10]:
        text_lines.append(
            f"- {row['feature']}: {row['normalized_importance']:.4f}"
        )

    write_report(
        base_name="clv_model_report",
        title="CLV Model Report",
        report=report,
        text_lines=text_lines,
    )

    artifact = {
        "model": final_model,
        "base_model_name": best_model_name,
        "features": FEATURES,
        "model_name": "clv_model",
        "model_version": MODEL_VERSION,
        "feature_importance": feature_importance,
        "report_path": "ml/reports/clv_model_report.json",
        "clv_band_thresholds": {
            "high_value": 10000,
            "medium_value": 3000,
        },
    }

    safe_joblib_dump(artifact, MODEL_DIR / "clv_model.joblib")

    print("CLV model report")
    print(f"Selected model: {best_model_name}")
    print(f"Holdout MAE: {holdout_metrics['mae']:.2f}")
    print(f"Holdout RMSE: {holdout_metrics['rmse']:.2f}")
    print(f"Holdout R2: {holdout_metrics['r2']:.4f}")
    print("Saved ml/models/clv_model.joblib")
    print("Saved ml/reports/clv_model_report.json")
    print("Saved ml/reports/clv_model_report.txt")


if __name__ == "__main__":
    main()
