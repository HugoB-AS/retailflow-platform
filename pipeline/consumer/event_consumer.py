import json
import os
import signal
from datetime import datetime

from confluent_kafka import Consumer
from sqlalchemy import create_engine, text

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
EVENT_TOPIC = os.getenv("EVENT_TOPIC", "retailflow_events")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://retailflow:retailflow@postgres:5432/retailflow_db",
)

running = True


def handle_shutdown(signum, frame):
    global running
    running = False


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

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


def parse_datetime(value: str | None):
    if not value:
        return datetime.utcnow()
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


def insert_event(event: dict) -> None:
    event_timestamp = parse_datetime(event.get("event_timestamp"))
    created_at = parse_datetime(event.get("created_at"))

    with engine.begin() as conn:
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


def main():
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
            insert_event(event)
            print(f"Inserted event {event.get('event_id')} type={event.get('event_type')}")
        except Exception as exc:
            print(f"Failed to process message: {exc}")

    consumer.close()
    print("Consumer stopped")


if __name__ == "__main__":
    main()
