from pathlib import Path
from urllib.parse import urlparse

import joblib
import pandas as pd
import psycopg2
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

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
    "support_tickets_count",
    "discount_usage_rate",
]


SEGMENT_LABELS = {
    0: "segment_0",
    1: "segment_1",
    2: "segment_2",
    3: "segment_3",
    4: "segment_4",
}


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


def main():
    df = load_customer_features()
    X = df[FEATURES].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = KMeans(n_clusters=5, random_state=42, n_init=10)
    clusters = model.fit_predict(X_scaled)

    score = silhouette_score(X_scaled, clusters)

    print("Segmentation model")
    print(f"Silhouette score: {score:.4f}")

    segment_summary = df.assign(cluster=clusters).groupby("cluster")[FEATURES].mean().round(2)
    print(segment_summary)

    artifact = {
        "model": model,
        "scaler": scaler,
        "features": FEATURES,
        "segment_labels": SEGMENT_LABELS,
        "model_name": "segmentation_model",
        "model_version": "v1",
    }

    joblib.dump(artifact, MODEL_DIR / "segmentation_model.joblib")
    print("Saved ml/models/segmentation_model.joblib")


if __name__ == "__main__":
    main()
