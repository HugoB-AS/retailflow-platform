from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.app.database import get_db

router = APIRouter(prefix="/events", tags=["events"])


class EventCreate(BaseModel):
    customer_id: str | None = None
    session_id: str | None = None
    event_type: str = Field(..., examples=["product_view", "add_to_cart", "checkout_started", "purchase"])
    product_id: str | None = None
    device_type: str | None = "desktop"
    browser: str | None = "Streamlit"
    country: str | None = "France"
    page_url: str | None = None
    referrer: str | None = "streamlit"
    sales_channel: str | None = "web"
    raw_payload: dict[str, Any] | None = None


@router.post("")
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    event_id = f"evt_live_{uuid4().hex[:12]}"
    event_timestamp = datetime.utcnow()

    payload = event.raw_payload or {}
    payload.update(
        {
            "event_id": event_id,
            "event_type": event.event_type,
            "source": "streamlit_storefront",
            "created_by": "retailflow_demo",
        }
    )

    query = text("""
        INSERT INTO raw.events (
            event_id,
            customer_id,
            session_id,
            event_type,
            product_id,
            event_timestamp,
            device_type,
            browser,
            country,
            page_url,
            referrer,
            sales_channel,
            raw_payload,
            created_at
        )
        VALUES (
            :event_id,
            :customer_id,
            :session_id,
            :event_type,
            :product_id,
            :event_timestamp,
            :device_type,
            :browser,
            :country,
            :page_url,
            :referrer,
            :sales_channel,
            CAST(:raw_payload AS JSONB),
            :created_at
        )
    """)

    db.execute(
        query,
        {
            "event_id": event_id,
            "customer_id": event.customer_id,
            "session_id": event.session_id,
            "event_type": event.event_type,
            "product_id": event.product_id,
            "event_timestamp": event_timestamp,
            "device_type": event.device_type,
            "browser": event.browser,
            "country": event.country,
            "page_url": event.page_url,
            "referrer": event.referrer,
            "sales_channel": event.sales_channel,
            "raw_payload": __import__("json").dumps(payload),
            "created_at": event_timestamp,
        },
    )
    db.commit()

    return {
        "status": "created",
        "event_id": event_id,
        "event_type": event.event_type,
    }


@router.get("/recent")
def recent_events(limit: int = 20, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            event_id,
            customer_id,
            session_id,
            event_type,
            product_id,
            event_timestamp,
            sales_channel
        FROM raw.events
        ORDER BY event_timestamp DESC
        LIMIT :limit
    """)

    result = db.execute(query, {"limit": limit}).mappings().all()
    return [dict(row) for row in result]
