from pathlib import Path
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.app.database import get_db


router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/churn-top")
def churn_top(limit: int = 20, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            mp.customer_id,
            c.country,
            c.city,
            cf.total_orders,
            cf.total_spent,
            cf.days_since_last_order,
            cf.return_rate,
            cf.cart_abandon_rate,
            cf.support_tickets_count,
            mp.model_version,
            mp.prediction_value AS churn_probability,
            mp.prediction_label AS churn_risk,
            mp.prediction_timestamp
        FROM analytics.ml_predictions mp
        JOIN analytics.customer_features cf ON mp.customer_id = cf.customer_id
        JOIN core.customers c ON mp.customer_id = c.customer_id
        WHERE mp.model_name = 'churn_model'
        ORDER BY mp.prediction_value DESC
        LIMIT :limit
    """)
    return [dict(row) for row in db.execute(query, {"limit": limit}).mappings().all()]


@router.get("/clv-top")
def clv_top(limit: int = 20, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            mp.customer_id,
            c.country,
            c.city,
            cf.total_orders,
            cf.total_spent,
            cf.avg_order_value,
            cf.preferred_category,
            mp.model_version,
            mp.prediction_value AS predicted_clv,
            mp.prediction_label AS clv_band,
            mp.prediction_timestamp
        FROM analytics.ml_predictions mp
        JOIN analytics.customer_features cf ON mp.customer_id = cf.customer_id
        JOIN core.customers c ON mp.customer_id = c.customer_id
        WHERE mp.model_name = 'clv_model'
        ORDER BY mp.prediction_value DESC
        LIMIT :limit
    """)
    return [dict(row) for row in db.execute(query, {"limit": limit}).mappings().all()]


@router.get("/segments")
def segments(db: Session = Depends(get_db)):
    query = text("""
        SELECT
            cs.segment_label,
            MAX(cs.segment_description) AS segment_description,
            MAX(cs.model_version) AS model_version,
            COUNT(*) AS customers_count,
            ROUND(AVG(cf.total_orders), 2) AS avg_orders,
            ROUND(AVG(cf.total_spent), 2) AS avg_spent,
            ROUND(AVG(cf.days_since_last_order), 2) AS avg_days_since_last_order,
            ROUND(AVG(cf.return_rate), 4) AS avg_return_rate,
            ROUND(AVG(cf.cart_abandon_rate), 4) AS avg_cart_abandon_rate,
            ROUND(AVG(cf.discount_usage_rate), 4) AS avg_discount_usage_rate
        FROM analytics.customer_segments cs
        JOIN analytics.customer_features cf ON cs.customer_id = cf.customer_id
        GROUP BY cs.segment_label
        ORDER BY customers_count DESC
    """)
    return [dict(row) for row in db.execute(query).mappings().all()]


@router.get("/customers")
def ai_customers(
    limit: int = 500,
    segment_label: str | None = None,
    analytics_consent_only: bool = True,
    min_orders: int | None = None,
    db: Session = Depends(get_db),
):
    filters = []
    params = {"limit": limit}

    if segment_label:
        filters.append("cs.segment_label = :segment_label")
        params["segment_label"] = segment_label

    if analytics_consent_only:
        filters.append("c.analytics_consent = TRUE")

    if min_orders is not None:
        filters.append("cf.total_orders >= :min_orders")
        params["min_orders"] = min_orders

    where_clause = ""
    if filters:
        where_clause = "WHERE " + " AND ".join(filters)

    query = text(f"""
        SELECT
            c.customer_id,
            c.country,
            c.city,
            c.loyalty_status,
            c.analytics_consent,
            c.marketing_consent,
            c.personalization_consent,
            cf.total_orders,
            cf.total_spent,
            cf.avg_order_value,
            cf.days_since_last_order,
            cf.return_rate,
            cf.cart_abandon_rate,
            churn.prediction_value AS churn_probability,
            churn.prediction_label AS churn_risk,
            clv.prediction_value AS predicted_clv,
            clv.prediction_label AS clv_band,
            cs.segment_label,
            cs.segment_description
        FROM core.customers c
        JOIN analytics.customer_features cf
            ON c.customer_id = cf.customer_id
        LEFT JOIN analytics.customer_segments cs
            ON c.customer_id = cs.customer_id
        LEFT JOIN analytics.ml_predictions churn
            ON c.customer_id = churn.customer_id
            AND churn.model_name = 'churn_model'
        LEFT JOIN analytics.ml_predictions clv
            ON c.customer_id = clv.customer_id
            AND clv.model_name = 'clv_model'
        {where_clause}
        ORDER BY c.customer_id
        LIMIT :limit
    """)

    return [dict(row) for row in db.execute(query, params).mappings().all()]


@router.get("/customer/{customer_id}")
def customer_ai_profile(customer_id: str, db: Session = Depends(get_db)):
    customer_query = text("""
        SELECT
            c.customer_id,
            c.country,
            c.city,
            c.loyalty_status,
            c.account_status,
            c.marketing_consent,
            c.analytics_consent,
            c.personalization_consent,
            c.is_anonymized,
            cf.total_orders,
            cf.total_spent,
            cf.avg_order_value,
            cf.days_since_last_order,
            cf.return_rate,
            cf.cart_abandon_rate,
            cf.session_count_30d,
            cf.pages_viewed_30d,
            cf.support_tickets_count,
            cf.avg_rating_given,
            cf.discount_usage_rate,
            cf.preferred_category
        FROM core.customers c
        JOIN analytics.customer_features cf ON c.customer_id = cf.customer_id
        WHERE c.customer_id = :customer_id
    """)

    customer = db.execute(customer_query, {"customer_id": customer_id}).mappings().first()

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    predictions_query = text("""
        SELECT
            model_name,
            model_version,
            prediction_value,
            prediction_label,
            prediction_timestamp
        FROM analytics.ml_predictions
        WHERE customer_id = :customer_id
        ORDER BY model_name
    """)

    predictions = [
        dict(row)
        for row in db.execute(
            predictions_query,
            {"customer_id": customer_id},
        ).mappings().all()
    ]

    segment_query = text("""
        SELECT
            segment_id,
            segment_label,
            segment_description,
            model_version,
            assigned_at
        FROM analytics.customer_segments
        WHERE customer_id = :customer_id
        LIMIT 1
    """)

    segment = db.execute(segment_query, {"customer_id": customer_id}).mappings().first()

    prediction_map = {row["model_name"]: row for row in predictions}

    return {
        "customer": dict(customer),
        "churn": prediction_map.get("churn_model"),
        "clv": prediction_map.get("clv_model"),
        "segment": dict(segment) if segment else None,
    }


@router.get("/summary")
def ai_summary(db: Session = Depends(get_db)):
    prediction_summary_query = text("""
        SELECT
            model_name,
            model_version,
            prediction_label,
            COUNT(*) AS predictions_count,
            ROUND(AVG(prediction_value), 4) AS avg_prediction_value,
            MIN(prediction_timestamp) AS first_prediction_at,
            MAX(prediction_timestamp) AS last_prediction_at
        FROM analytics.ml_predictions
        GROUP BY model_name, model_version, prediction_label
        ORDER BY model_name, prediction_label
    """)

    segment_summary_query = text("""
        SELECT
            segment_label,
            MAX(segment_description) AS segment_description,
            MAX(model_version) AS model_version,
            COUNT(*) AS customers_count
        FROM analytics.customer_segments
        GROUP BY segment_label
        ORDER BY customers_count DESC
    """)

    freshness_query = text("""
        SELECT
            COUNT(DISTINCT customer_id) AS predicted_customers,
            COUNT(*) AS prediction_rows,
            MAX(prediction_timestamp) AS last_prediction_at
        FROM analytics.ml_predictions
    """)

    predictions = [
        dict(row)
        for row in db.execute(prediction_summary_query).mappings().all()
    ]

    segments_result = [
        dict(row)
        for row in db.execute(segment_summary_query).mappings().all()
    ]

    freshness = db.execute(freshness_query).mappings().first()

    return {
        "prediction_freshness": dict(freshness) if freshness else None,
        "predictions_by_model": predictions,
        "segments": segments_result,
    }


@router.get("/model-reports")
def model_reports():
    return {
        "reports": {
            "model_summary": "ml/reports/model_summary.json",
            "churn": {
                "json": "ml/reports/churn_model_report.json",
                "txt": "ml/reports/churn_model_report.txt",
            },
            "clv": {
                "json": "ml/reports/clv_model_report.json",
                "txt": "ml/reports/clv_model_report.txt",
            },
            "segmentation": {
                "json": "ml/reports/segmentation_model_report.json",
                "txt": "ml/reports/segmentation_model_report.txt",
            },
            "drift": {
                "json": "ml/reports/drift_report.json",
                "txt": "ml/reports/drift_report.txt",
            },
        }
    }


REPORT_DIR = Path("ml/reports")

ALLOWED_REPORTS = {
    "model_summary": REPORT_DIR / "model_summary.json",
    "churn": REPORT_DIR / "churn_model_report.json",
    "clv": REPORT_DIR / "clv_model_report.json",
    "segmentation": REPORT_DIR / "segmentation_model_report.json",
    "drift": REPORT_DIR / "drift_report.json",
}


@router.get("/model-report/{report_name}")
def model_report(report_name: str):
    if report_name not in ALLOWED_REPORTS:
        raise HTTPException(status_code=404, detail="Unknown model report")

    report_path = ALLOWED_REPORTS[report_name]

    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Model report file not found")

    try:
        return json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to read model report: {exc}",
        )
