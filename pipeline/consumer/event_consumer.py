import json
import os
import signal
from datetime import datetime
from uuid import uuid4

from confluent_kafka import Consumer
from sqlalchemy import create_engine, text

from pipeline.consumer.validators import validate_event

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
EVENT_TOPIC = os.getenv("EVENT_TOPIC", "retailflow_events")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://retailflow:retailflow@postgres:5432/retailflow_db",
)

# Runtime flag used to stop the Kafka consumer gracefully when Docker or the OS
# sends SIGTERM/SIGINT. This avoids interrupting a database transaction midway.
running = True


def handle_shutdown(signum, frame):
    global running
    running = False


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

# pool_pre_ping=True makes SQLAlchemy verify connections before using them.
# This is useful in Docker environments where PostgreSQL connections can be
# restarted while the consumer process is still alive.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": "retailflow_event_consumer",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    }
)


INSERT_EVENT_SQL = text("""
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
    ON CONFLICT (event_id) DO NOTHING
""")

INSERT_DEAD_LETTER_SQL = text("""
    INSERT INTO governance.dead_letter_events (
        dead_letter_id,
        event_id,
        source_topic,
        event_type,
        error_reason,
        raw_payload,
        created_at,
        severity,
        reprocessed,
        reprocessed_at
    )
    VALUES (
        :dead_letter_id,
        :event_id,
        :source_topic,
        :event_type,
        :error_reason,
        CAST(:raw_payload AS JSONB),
        :created_at,
        :severity,
        FALSE,
        NULL
    )
""")

INSERT_QUALITY_LOG_SQL = text("""
    INSERT INTO governance.data_quality_logs (
        check_id,
        rule_id,
        rule_name,
        table_name,
        record_id,
        status,
        severity,
        action,
        error_message,
        checked_at,
        source
    )
    VALUES (
        :check_id,
        :rule_id,
        :rule_name,
        :table_name,
        :record_id,
        :status,
        :severity,
        :action,
        :error_message,
        :checked_at,
        :source
    )
""")


def parse_datetime(value: str | None):
    """""Parse event timestamps into naive UTC-compatible datetimes for PostgreSQL.

    Incoming events may use ISO strings with a trailing Z. PostgreSQL columns in
    this project are stored without timezone, so timezone information is removed
    after parsing.
    """
    if not value:
        return datetime.utcnow()
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


def insert_event(conn, event: dict) -> None:
    """""Insert a valid event into raw.events.

    ON CONFLICT is handled by the SQL statement, making repeated messages
    idempotent when the same event_id is consumed more than once.
    """
    event_timestamp = parse_datetime(event.get("event_timestamp"))
    created_at = parse_datetime(event.get("created_at"))

    conn.execute(
        INSERT_EVENT_SQL,
        {
            "event_id": event.get("event_id"),
            "customer_id": event.get("customer_id"),
            "session_id": event.get("session_id"),
            "event_type": event.get("event_type"),
            "product_id": event.get("product_id"),
            "event_timestamp": event_timestamp,
            "device_type": event.get("device_type"),
            "browser": event.get("browser"),
            "country": event.get("country"),
            "page_url": event.get("page_url"),
            "referrer": event.get("referrer"),
            "sales_channel": event.get("sales_channel"),
            "raw_payload": json.dumps(event.get("raw_payload", {})),
            "created_at": created_at,
        },
    )


def insert_dead_letter(conn, event: dict, errors: list[dict]) -> None:
    """""Store rejected events for auditability and later replay analysis.

    This supports data quality governance: invalid events are not silently lost,
    and the original payload remains available in the dead-letter table.
    """
    error_reason = " | ".join(error["message"] for error in errors)
    severity = "high" if any(error["severity"] == "high" for error in errors) else "medium"

    conn.execute(
        INSERT_DEAD_LETTER_SQL,
        {
            "dead_letter_id": f"dlq_{uuid4().hex[:12]}",
            "event_id": event.get("event_id"),
            "source_topic": EVENT_TOPIC,
            "event_type": event.get("event_type"),
            "error_reason": error_reason,
            "raw_payload": json.dumps(event),
            "created_at": datetime.utcnow(),
            "severity": severity,
        },
    )


def insert_quality_logs(conn, event: dict, errors: list[dict]) -> None:
    """""Write one data quality log per validation error.

    The governance.data_quality_logs table provides rule-level traceability for
    rejected records and can be used later in dashboards or audits.
    """
    for error in errors:
        conn.execute(
            INSERT_QUALITY_LOG_SQL,
            {
                "check_id": f"chk_{uuid4().hex[:12]}",
                "rule_id": error["rule_id"],
                "rule_name": error["rule_name"],
                "table_name": "raw.events",
                "record_id": event.get("event_id"),
                "status": "failed",
                "severity": error["severity"],
                "action": error["action"],
                "error_message": error["message"],
                "checked_at": datetime.utcnow(),
                "source": "event_consumer",
            },
        )


def process_event(event: dict) -> None:
    """""Validate and persist a single Kafka event inside one DB transaction.

    Valid events are inserted into raw.events. Invalid events are redirected to
    dead-letter storage and data quality logs in the same transaction.
    """
    with engine.begin() as conn:
        errors = validate_event(event, conn)

        if errors:
            insert_dead_letter(conn, event, errors)
            insert_quality_logs(conn, event, errors)
            print(f"Rejected event {event.get('event_id')} errors={len(errors)}")
            return

        insert_event(conn, event)
        print(f"Inserted event {event.get('event_id')} type={event.get('event_type')}")


def main():
    """""Run the long-lived Kafka consumer loop.

    The loop polls Redpanda/Kafka, decodes JSON messages, applies validation,
    and persists accepted/rejected records until a shutdown signal is received.
    """
    print(f"Starting consumer on topic={EVENT_TOPIC}, brokers={KAFKA_BOOTSTRAP_SERVERS}")
    consumer.subscribe([EVENT_TOPIC])

    while running:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        try:
            event = json.loads(msg.value().decode("utf-8"))
            process_event(event)
        except Exception as exc:
            print(f"Failed to process message: {exc}")

    consumer.close()
    print("Consumer stopped")


if __name__ == "__main__":
    main()
