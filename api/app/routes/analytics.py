from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.app.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/top-customers")
def top_customers(limit: int = 10, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            customer_id,
            total_orders,
            total_spent,
            avg_order_value,
            loyalty_status,
            preferred_category
        FROM analytics.customer_features
        ORDER BY total_spent DESC
        LIMIT :limit
    """)

    result = db.execute(query, {"limit": limit}).mappings().all()

    return [dict(row) for row in result]


@router.get("/churn-candidates")
def churn_candidates(limit: int = 10, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            customer_id,
            total_orders,
            total_spent,
            days_since_last_order,
            return_rate,
            cart_abandon_rate,
            support_tickets_count,
            avg_rating_given
        FROM analytics.customer_features
        WHERE
            days_since_last_order > 90
            OR cart_abandon_rate > 0.80
            OR support_tickets_count >= 3
        ORDER BY days_since_last_order DESC
        LIMIT :limit
    """)

    result = db.execute(query, {"limit": limit}).mappings().all()

    return [dict(row) for row in result]
