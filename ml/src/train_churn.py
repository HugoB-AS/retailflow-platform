from pathlib import Path
from urllib.parse import urlparse

import joblib
import pandas as pd
import psycopg2
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split

from ml.src.db import DATABASE_URL

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


def get_psycopg2_connection():
    database_url = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")
    parsed = urlparse(database_url)

    return psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        dbname=parsed.path.lstrip("/"),
        user=parsed.username,
        password=parsed.password,
    )


def load_customer_features() -> pd.DataFrame:
    query = "SELECT * FROM analytics.customer_features"

    conn = get_psycopg2_connection()
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def build_churn_label(df: pd.DataFrame) -> pd.Series:
    return (
        (
            (df["days_since_last_order"] > 120)
            & (df["total_orders"] >= 2)
        )
        | (df["cart_abandon_rate"] > 0.90)
        | (
            (df["support_tickets_count"] >= 2)
            & (df["avg_rating_given"] <= 3)
        )
    ).astype(int)


def main():
    df = load_customer_features()

    df[FEATURES] = df[FEATURES].fillna(0)
    y = build_churn_label(df)
    X = df[FEATURES]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=8,
        random_state=42,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]

    print("Churn model report")
    print(classification_report(y_test, preds))
    print(f"ROC AUC: {roc_auc_score(y_test, proba):.4f}")

    artifact = {
        "model": model,
        "features": FEATURES,
        "model_name": "churn_model",
        "model_version": "v1",
    }

    joblib.dump(artifact, MODEL_DIR / "churn_model.joblib")
    print("Saved ml/models/churn_model.joblib")


if __name__ == "__main__":
    main()
