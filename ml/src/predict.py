from __future__ import annotations

from uuid import uuid4
import hashlib

import joblib
import pandas as pd

from ml.src.ml_utils import MODEL_DIR, get_psycopg2_connection, load_customer_features


def risk_label(probability: float, thresholds: dict | None = None) -> str:
    thresholds = thresholds or {"high_risk": 0.70, "medium_risk": 0.40}

    if probability >= thresholds.get("high_risk", 0.70):
        return "high_risk"
    if probability >= thresholds.get("medium_risk", 0.40):
        return "medium_risk"
    return "low_risk"


def clv_label(value: float, thresholds: dict | None = None) -> str:
    thresholds = thresholds or {"high_value": 10000, "medium_value": 3000}

    if value >= thresholds.get("high_value", 10000):
        return "high_value"
    if value >= thresholds.get("medium_value", 3000):
        return "medium_value"
    return "low_value"


def feature_hash(customer_id: str, model_name: str, model_version: str) -> str:
    raw = f"{customer_id}|{model_name}|{model_version}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def save_predictions(churn_df, clv_df, segments_df, metadata: dict):
    conn = get_psycopg2_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM analytics.ml_predictions;")
        cur.execute("DELETE FROM analytics.customer_segments;")

        churn_version = metadata["churn_model_version"]
        clv_version = metadata["clv_model_version"]
        segmentation_version = metadata["segmentation_model_version"]

        for _, row in churn_df.iterrows():
            customer_id = row["customer_id"]
            model_name = "churn_model"

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
                    churn_version,
                    float(row["churn_probability"]),
                    row["churn_risk"],
                    feature_hash(customer_id, model_name, churn_version),
                ),
            )

        for _, row in clv_df.iterrows():
            customer_id = row["customer_id"]
            model_name = "clv_model"

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
                    clv_version,
                    float(row["predicted_clv"]),
                    row["clv_band"],
                    feature_hash(customer_id, model_name, clv_version),
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
                    row["segment_description"],
                    segmentation_version,
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

    churn_model = churn_artifact["model"]
    clv_model = clv_artifact["model"]
    seg_model = seg_artifact["model"]
    scaler = seg_artifact["scaler"]

    churn_features = churn_artifact["features"]
    clv_features = clv_artifact["features"]
    seg_features = seg_artifact["features"]

    churn_thresholds = churn_artifact.get("risk_thresholds", {
        "high_risk": 0.70,
        "medium_risk": 0.40,
    })
    clv_thresholds = clv_artifact.get("clv_band_thresholds", {
        "high_value": 10000,
        "medium_value": 3000,
    })

    segment_labels = seg_artifact["segment_labels"]
    segment_descriptions = seg_artifact.get("segment_descriptions", {})

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
    churn_df["churn_risk"] = churn_df["churn_probability"].apply(
        lambda value: risk_label(value, churn_thresholds)
    )

    clv_df = pd.DataFrame({
        "customer_id": df["customer_id"],
        "predicted_clv": clv_preds,
    })
    clv_df["clv_band"] = clv_df["predicted_clv"].apply(
        lambda value: clv_label(value, clv_thresholds)
    )

    segments_df = pd.DataFrame({
        "customer_id": df["customer_id"],
        "segment_id": seg_preds,
    })
    segments_df["segment_label"] = segments_df["segment_id"].apply(
        lambda value: segment_labels[int(value)]
    )
    segments_df["segment_description"] = segments_df["segment_id"].apply(
        lambda value: segment_descriptions.get(int(value), f"Customer segment {int(value)}")
    )

    metadata = {
        "churn_model_version": churn_artifact.get("model_version", "v2_realism"),
        "clv_model_version": clv_artifact.get("model_version", "v2_realism"),
        "segmentation_model_version": seg_artifact.get("model_version", "v2_realism"),
    }

    save_predictions(churn_df, clv_df, segments_df, metadata)

    print(f"Inserted predictions for {len(df)} customers")
    print(f"Inserted {len(churn_df) + len(clv_df)} ML prediction rows")
    print(f"Inserted {len(segments_df)} customer segment rows")
    print(f"Churn model version: {metadata['churn_model_version']}")
    print(f"CLV model version: {metadata['clv_model_version']}")
    print(f"Segmentation model version: {metadata['segmentation_model_version']}")


if __name__ == "__main__":
    main()
