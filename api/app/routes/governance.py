from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.app.database import get_db

router = APIRouter(prefix="/governance", tags=["governance"])


@router.get("/summary")
def governance_summary(db: Session = Depends(get_db)):
    consent_query = text("""
        SELECT
            COUNT(*) AS customers_count,
            SUM(CASE WHEN marketing_consent THEN 1 ELSE 0 END) AS marketing_consent_count,
            SUM(CASE WHEN analytics_consent THEN 1 ELSE 0 END) AS analytics_consent_count,
            SUM(CASE WHEN personalization_consent THEN 1 ELSE 0 END) AS personalization_consent_count,
            SUM(CASE WHEN is_anonymized THEN 1 ELSE 0 END) AS anonymized_customers_count
        FROM core.customers
    """)

    policies_query = text("""
        SELECT COUNT(*) AS retention_policies_count
        FROM governance.data_retention_policies
    """)

    actions_query = text("""
        SELECT
            COUNT(*) AS retention_actions_count,
            SUM(CASE WHEN action_status = 'success' THEN 1 ELSE 0 END) AS successful_actions_count
        FROM governance.retention_actions_log
    """)

    consent = db.execute(consent_query).mappings().first()
    policies = db.execute(policies_query).mappings().first()
    actions = db.execute(actions_query).mappings().first()

    return {
        "consent": dict(consent) if consent else {},
        "retention": dict(policies) if policies else {},
        "actions": dict(actions) if actions else {},
    }


@router.get("/retention-policies")
def retention_policies(db: Session = Depends(get_db)):
    query = text("""
        SELECT
            policy_id,
            data_domain,
            table_name,
            data_category,
            retention_days,
            retention_trigger,
            retention_action,
            legal_basis,
            owner_role,
            description
        FROM governance.data_retention_policies
        ORDER BY policy_id
    """)
    return [dict(row) for row in db.execute(query).mappings().all()]


@router.get("/retention-actions")
def retention_actions(limit: int = 50, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            action_id,
            policy_id,
            table_name,
            record_id,
            action_type,
            action_status,
            executed_at,
            executed_by,
            details
        FROM governance.retention_actions_log
        ORDER BY executed_at DESC
        LIMIT :limit
    """)
    return [dict(row) for row in db.execute(query, {"limit": limit}).mappings().all()]


@router.get("/customer-consents")
def customer_consents(limit: int = 50, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            customer_id,
            country,
            city,
            marketing_consent,
            analytics_consent,
            personalization_consent,
            account_status,
            is_anonymized,
            anonymized_at,
            created_at,
            updated_at
        FROM core.customers
        ORDER BY customer_id
        LIMIT :limit
    """)
    return [dict(row) for row in db.execute(query, {"limit": limit}).mappings().all()]
