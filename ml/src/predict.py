from pathlib import Path
from uuid import uuid4

import joblib
import pandas as pd
from sqlalchemy import text

from ml.src.db import engine

MODEL_DIR = Path("ml/models")


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


def clear_previous_predictions():
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM analytics.ml_predictions"))
        conn.execute(text("DELETE FROM analytics.customer_segments"))


def insert_prediction(conn, customer_id, model_name, model_version, prediction_value, prediction_label):
    conn.execute(
        text("""
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
            VALUES (
                :prediction_id,
                :customer_id,
                :model_name,
                :model_version,
                :prediction_value,
                :prediction_label,
                CURRENT_TIMESTAMP,
                :input_features_hash,
                CURRENT_TIMESTAMP
            )
        """),
        {
            "prediction_id": f"pred_{uuid4().hex[:12]}",
            "customer_id": customer_id,
            "model_name": model_name,
            "model_version": model_version,
            "prediction_value": float(prediction_value),
            "prediction_label": prediction_label,
            "input_features_hash": f"hash_{customer_id}_{model_name}_{model_version}",
        },
    )


def insert_segment(conn, customer_id, segment_id, segment_label, model_version):
    conn.execute(
        text("""
            INSERT INTO analytics.customer_segments (
                customer_id,
                segment_id,
                segment_label,
                segment_description,
                model_version,
                assigned_at
            )
            VALUES (
                :customer_id,
                :segment_id,
                :segment_label,
                :segment_description,
                :model_version,
                CURRENT_TIMESTAMP
            )
        """),
        {
            "customer_id": customer_id,
            "segment_id": int(segment_id),
            "segment_label": segment_label,
            "segment_description": f"Customer segment {segment_label} inferred from behavioral and transactional features.",
            "model_version": model_version,
        },
    )


def main():
    df = pd.read_sql("SELECT * FROM analytics.customer_features", engine)

    churn_artifact = joblib.load(MODEL_DIR / "churn_model.joblib")
    segment_artifact = joblib.load(MODEL_DIR / "segmentation_model.joblib")
    clv_artifact = joblib.load(MODEL_DIR / "clv_model.joblib")

    clear_previous_predictions()

    churn_features = churn_artifact["features"]
    segment_features = segment_artifact["features"]
    clv_features = clv_artifact["features"]

    churn_model = churn_artifact["model"]
    segment_model = segment_artifact["model"]
    segment_scaler = segment_artifact["scaler"]
    clv_model = clv_artifact["model"]

    X_churn = df[churn_features].fillna(0)
    X_segment = df[segment_features].fillna(0)
    X_clv = df[clv_features].fillna(0)

    churn_probabilities = churn_model.predict_proba(X_churn)[:, 1]
    segment_ids = segment_model.predict(segment_scaler.transform(X_segment))
    clv_values = clv_model.predict(X_clv)

    with engine.begin() as conn:
        for idx, row in df.iterrows():
            customer_id = row["customer_id"]

            churn_probability = float(churn_probabilities[idx])
            predicted_clv = float(clv_values[idx])
            segment_id = int(segment_ids[idx])
            segment_label = f"segment_{segment_id}"

            insert_prediction(
                conn,
                customer_id,
                "churn_model",
                "v1",
                churn_probability,
                risk_label(churn_probability),
            )

            insert_prediction(
                conn,
                customer_id,
                "clv_model",
                "v1",
                predicted_clv,
                clv_label(predicted_clv),
            )

            insert_segment(
                conn,
                customer_id,
                segment_id,
                segment_label,
                "v1",
            )

    print(f"Inserted predictions for {len(df)} customers")
    print(f"Inserted {len(df) * 2} ML prediction rows")
    print(f"Inserted {len(df)} customer segment rows")


if __name__ == "__main__":
    main()
