from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from ml.src.db import engine

MODEL_DIR = Path("ml/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

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


def build_clv_target(df: pd.DataFrame) -> pd.Series:
    recency_factor = np.clip(1 - (df["days_since_last_order"] / 365), 0.1, 1.2)
    loyalty_factor = df["loyalty_status"].map({
        "new": 0.8,
        "bronze": 0.9,
        "silver": 1.0,
        "gold": 1.25,
        "platinum": 1.6,
    }).fillna(1.0)

    engagement_factor = np.clip(
        1 + (df["session_count_30d"] / 20) - df["cart_abandon_rate"],
        0.5,
        1.8,
    )

    penalty_factor = np.clip(
        1 - df["return_rate"] - (df["support_tickets_count"] * 0.03),
        0.4,
        1.0,
    )

    clv = (
        df["total_spent"] * 0.45 * recency_factor * loyalty_factor
        + df["avg_order_value"] * engagement_factor * 2
    ) * penalty_factor

    return clv.clip(lower=0).round(2)


def main():
    df = pd.read_sql("SELECT * FROM analytics.customer_features", engine)

    df[FEATURES] = df[FEATURES].fillna(0)
    y = build_clv_target(df)
    X = df[FEATURES]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
    )

    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=10,
        random_state=42,
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    rmse = mean_squared_error(y_test, preds) ** 0.5
    r2 = r2_score(y_test, preds)

    print("CLV model report")
    print(f"MAE: {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R2: {r2:.4f}")

    artifact = {
        "model": model,
        "features": FEATURES,
        "model_name": "clv_model",
        "model_version": "v1",
    }

    joblib.dump(artifact, MODEL_DIR / "clv_model.joblib")
    print("Saved ml/models/clv_model.joblib")


if __name__ == "__main__":
    main()
