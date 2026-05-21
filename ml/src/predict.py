from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4
import hashlib

import joblib
import pandas as pd
import psycopg2

from ml.src.db import DATABASE_URL

MODEL_DIR = Path("ml/models")


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
    conn = get_psycopg2_connection()
    try:
        return pd.read_sql_query(
            "SELECT * FROM analytics.customer_features",
            conn,
        )
    finally:
        conn.close()


def risk_label(probability: float) -> str:
    if probability >= 0.70:
        return "high_risk"
    if probability >= 0.40:
        return "medium_risk"
    return "low_risk"


def clv_label(value: float) -> str:
    if value >= 10000:
        return "high_value"
    if value >= 3000:
        return "medium_value"
    return "low_value"


def feature_hash(customer_id: str, model_name: str, model_version: str) -> str:
    raw = f"{customer_id}|{model_name}|{model_version}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def save_predictions(churn_df, clv_df, segments_df):
    conn = get_psycopg2_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM analytics.ml_predictions;")
        cur.execute("DELETE FROM analytics.customer_segments;")

        for _, row in churn_df.iterrows():
            customer_id = row["customer_id"]
            model_name = "churn_model"
            model_version = "v1"

            cur.execute(
                """
                INSERT INTO analytics.ml_predictions (
                    prediction_id,
                    customer_id,
                    model_name,
                    model_version,
                    prediction_value,
                    prediction_label,
                    prediction_timestamp,
                    input_features_hash,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, CURRENT_TIMESTAMP);
                """,
                (
                    f"pred_{uuid4().hex[:12]}",
                    customer_id,
                    model_name,
                    model_version,
                    float(row["churn_probability"]),
                    row["churn_risk"],
                    feature_hash(customer_id, model_name, model_version),
                ),
            )

        for _, row in clv_df.iterrows():
            customer_id = row["customer_id"]
            model_name = "clv_model"
            model_version = "v1"

            cur.execute(
                """
                INSERT INTO analytics.ml_predictions (
                    prediction_id,
                    customer_id,
                    model_name,
                    model_version,
                    prediction_value,
                    prediction_label,
                    prediction_timestamp,
                    input_features_hash,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, CURRENT_TIMESTAMP);
                """,
                (
                    f"pred_{uuid4().hex[:12]}",
                    customer_id,
                    model_name,
                    model_version,
                    float(row["predicted_clv"]),
                    row["clv_band"],
                    feature_hash(customer_id, model_name, model_version),
                ),
            )

        for _, row in segments_df.iterrows():
            cur.execute(
                """
                INSERT INTO analytics.customer_segments (
                    customer_id,
                    segment_id,
                    segment_label,
                    segment_description,
                    model_version,
                    assigned_at
                )
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
                """,
                (
                    row["customer_id"],
                    int(row["segment_id"]),
                    row["segment_label"],
                    f"Customer assigned to {row['segment_label']} by segmentation_model v1.",
                    "v1",
                ),
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()


def main():
    df = load_customer_features()

    churn_artifact = joblib.load(MODEL_DIR / "churn_model.joblib")
    clv_artifact = joblib.load(MODEL_DIR / "clv_model.joblib")
    seg_artifact = joblib.load(MODEL_DIR / "segmentation_model.joblib")

    churn_features = churn_artifact["features"]
    clv_features = clv_artifact["features"]
    seg_features = seg_artifact["features"]

    churn_model = churn_artifact["model"]
    clv_model = clv_artifact["model"]
    seg_model = seg_artifact["model"]
    scaler = seg_artifact["scaler"]
    segment_labels = seg_artifact["segment_labels"]

    churn_X = df[churn_features].fillna(0)
    clv_X = df[clv_features].fillna(0)
    seg_X = df[seg_features].fillna(0)

    churn_proba = churn_model.predict_proba(churn_X)[:, 1]
    clv_preds = clv_model.predict(clv_X)
    seg_preds = seg_model.predict(scaler.transform(seg_X))

    churn_df = pd.DataFrame({
        "customer_id": df["customer_id"],
        "churn_probability": churn_proba,
    })
    churn_df["churn_risk"] = churn_df["churn_probability"].apply(risk_label)

    clv_df = pd.DataFrame({
        "customer_id": df["customer_id"],
        "predicted_clv": clv_preds,
    })
    clv_df["clv_band"] = clv_df["predicted_clv"].apply(clv_label)

    segments_df = pd.DataFrame({
        "customer_id": df["customer_id"],
        "segment_id": seg_preds,
        "segment_label": [segment_labels[int(s)] for s in seg_preds],
    })

    save_predictions(churn_df, clv_df, segments_df)

    print(f"Inserted predictions for {len(df)} customers")
    print(f"Inserted {len(churn_df) + len(clv_df)} ML prediction rows")
    print(f"Inserted {len(segments_df)} customer segment rows")


if __name__ == "__main__":
    main()
