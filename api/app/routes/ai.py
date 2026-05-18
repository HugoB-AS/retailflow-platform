from fastapi import APIRouter, Depends
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
            mp.prediction_value AS churn_probability,
            mp.prediction_label AS churn_risk
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
            mp.prediction_value AS predicted_clv,
            mp.prediction_label AS clv_band
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
            COUNT(*) AS customers_count,
            ROUND(AVG(cf.total_orders), 2) AS avg_orders,
            ROUND(AVG(cf.total_spent), 2) AS avg_spent,
            ROUND(AVG(cf.days_since_last_order), 2) AS avg_days_since_last_order,
            ROUND(AVG(cf.return_rate), 4) AS avg_return_rate,
            ROUND(AVG(cf.cart_abandon_rate), 4) AS avg_cart_abandon_rate
        FROM analytics.customer_segments cs
        JOIN analytics.customer_features cf ON cs.customer_id = cf.customer_id
        GROUP BY cs.segment_label
        ORDER BY customers_count DESC
    """)
    return [dict(row) for row in db.execute(query).mappings().all()]
