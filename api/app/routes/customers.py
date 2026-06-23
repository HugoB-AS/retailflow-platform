from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.app.database import get_db

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            c.customer_id,
            c.first_name,
            c.last_name,
            c.email,
            c.country,
            c.city,
            c.loyalty_status,
            c.account_status,
            f.total_orders,
            f.total_spent,
            f.avg_order_value,
            f.days_since_last_order,
            f.return_rate,
            f.cart_abandon_rate,
            f.support_tickets_count,
            f.avg_rating_given,
            f.preferred_category
        FROM core.customers c
        LEFT JOIN analytics.customer_features f
            ON c.customer_id = f.customer_id
        WHERE c.customer_id = :customer_id
    """)

    result = db.execute(query, {"customer_id": customer_id}).mappings().first()

    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")

    return dict(result)
