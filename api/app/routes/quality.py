from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.app.database import get_db

router = APIRouter(prefix="/quality", tags=["quality"])


@router.get("/dead-letters")
def dead_letters(limit: int = 20, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            dead_letter_id,
            event_id,
            source_topic,
            event_type,
            severity,
            error_reason,
            created_at,
            reprocessed
        FROM governance.dead_letter_events
        ORDER BY created_at DESC
        LIMIT :limit
    """)

    result = db.execute(query, {"limit": limit}).mappings().all()
    return [dict(row) for row in result]


@router.get("/summary")
def quality_summary(db: Session = Depends(get_db)):
    query = text("""
        SELECT
            rule_id,
            rule_name,
            table_name,
            severity,
            status,
            checks_count,
            last_checked_at
        FROM governance.v_data_quality_summary
        ORDER BY checks_count DESC
    """)

    result = db.execute(query).mappings().all()
    return [dict(row) for row in result]


@router.get("/dead-letter-summary")
def dead_letter_summary(db: Session = Depends(get_db)):
    query = text("""
        SELECT
            event_type,
            severity,
            error_reason,
            events_count,
            last_seen_at
        FROM governance.v_dead_letter_summary
        ORDER BY events_count DESC
    """)

    result = db.execute(query).mappings().all()
    return [dict(row) for row in result]
