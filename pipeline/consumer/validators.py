from __future__ import annotations

from datetime import datetime
from sqlalchemy import text

# Central whitelist for event taxonomy.
# Keeping this list explicit prevents unexpected event types from entering
# raw.events and makes the validation policy easy to explain during the defense.
ALLOWED_EVENT_TYPES = {
    "page_view",
    "catalog_view",
    "product_view",
    "search",
    "add_to_cart",
    "remove_from_cart",
    "checkout_started",
    "purchase",
    "login",
    "logout",
}


def parse_datetime(value: str | None):
    """""Safely parse an event timestamp.

    Returns None instead of raising when the value is missing or malformed, so
    validate_event can convert parsing problems into data quality rule errors.
    """
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


def validate_event(event: dict, conn) -> list[dict]:
    """""Validate a raw event before insertion into PostgreSQL.

    The function returns a list of structured rule violations rather than
    raising exceptions. This makes it possible to store rejected events in a
    dead-letter queue and to log each failed data quality rule.
    """
    errors = []

    event_id = event.get("event_id")
    event_type = event.get("event_type")
    customer_id = event.get("customer_id")
    product_id = event.get("product_id")
    event_timestamp = parse_datetime(event.get("event_timestamp"))

    if not event_id:
        errors.append({
            "rule_id": "R001",
            "rule_name": "event_id_not_null",
            "severity": "high",
            "action": "reject",
            "message": "event_id is required",
        })

    if event_type not in ALLOWED_EVENT_TYPES:
        errors.append({
            "rule_id": "R002",
            "rule_name": "event_type_allowed",
            "severity": "high",
            "action": "reject",
            "message": f"event_type '{event_type}' is not allowed",
        })

    if customer_id:
        exists = conn.execute(
            text("SELECT 1 FROM core.customers WHERE customer_id = :customer_id"),
            {"customer_id": customer_id},
        ).first()
        if not exists:
            errors.append({
                "rule_id": "R003",
                "rule_name": "customer_exists",
                "severity": "high",
                "action": "reject",
                "message": f"customer_id '{customer_id}' does not exist",
            })

    if product_id:
        exists = conn.execute(
            text("SELECT 1 FROM core.products WHERE product_id = :product_id"),
            {"product_id": product_id},
        ).first()
        if not exists:
            errors.append({
                "rule_id": "R004",
                "rule_name": "product_exists",
                "severity": "high",
                "action": "reject",
                "message": f"product_id '{product_id}' does not exist",
            })

    if event_timestamp is None:
        errors.append({
            "rule_id": "R005",
            "rule_name": "timestamp_valid",
            "severity": "high",
            "action": "reject",
            "message": "event_timestamp is missing or invalid",
        })
    else:
        now = datetime.utcnow()
        min_date = datetime(2020, 1, 1)
        if event_timestamp > now:
            errors.append({
                "rule_id": "R005",
                "rule_name": "timestamp_valid",
                "severity": "high",
                "action": "reject",
                "message": "event_timestamp is in the future",
            })
        if event_timestamp < min_date:
            errors.append({
                "rule_id": "R005",
                "rule_name": "timestamp_valid",
                "severity": "high",
                "action": "reject",
                "message": "event_timestamp is before 2020-01-01",
            })

    return errors
