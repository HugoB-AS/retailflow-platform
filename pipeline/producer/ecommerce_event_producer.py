from __future__ import annotations

import json
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from confluent_kafka import Producer


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092")
EVENT_TOPIC = os.getenv("EVENT_TOPIC", "retailflow_events")
EVENT_COUNT = int(os.getenv("EVENT_COUNT", "20"))
EVENT_DELAY_SECONDS = float(os.getenv("EVENT_DELAY_SECONDS", "0.3"))

PIPELINE_REPORT_DIR = Path(os.getenv("PIPELINE_REPORT_DIR", "pipeline/reports"))
PIPELINE_METRICS_PATH = PIPELINE_REPORT_DIR / "pipeline_metrics.json"


EVENT_TYPES = [
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
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_event(index: int) -> dict:
    event_type = random.choice(EVENT_TYPES)
    customer_id = f"cust_{random.randint(1, 5000):06d}"
    product_id = None

    if event_type in {
        "catalog_view",
        "product_view",
        "add_to_cart",
        "remove_from_cart",
        "checkout_started",
        "purchase",
    }:
        product_id = f"prod_{random.randint(1, 500):06d}"

    # The raw.events.event_id column is VARCHAR(30), so the identifier must stay short.
    event_id = f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}{index}{uuid4().hex[:6]}"

    return {
        "event_id": event_id,
        "customer_id": customer_id,
        "session_id": f"sess_live_{uuid4().hex[:10]}",
        "event_type": event_type,
        "product_id": product_id,
        "event_timestamp": utc_now_iso(),
        "device_type": random.choice(["desktop", "mobile", "tablet"]),
        "browser": random.choice(["Chrome", "Safari", "Firefox", "Edge"]),
        "country": random.choice(["France", "Belgium", "Germany", "Spain", "Italy"]),
        "page_url": f"/{event_type.replace('_', '-')}",
        "referrer": random.choice(["direct", "google", "newsletter", "instagram", "facebook"]),
        "sales_channel": random.choice(["web", "mobile_app"]),
        "raw_payload": {
            "source": "live_demo_producer",
            "payload_version": "v1",
        },
        "created_at": utc_now_iso(),
    }


def write_pipeline_metrics(metrics: dict) -> None:
    PIPELINE_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    PIPELINE_METRICS_PATH.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})

    delivered_events = 0
    failed_events = 0

    def delivery_report(err, msg) -> None:
        nonlocal delivered_events, failed_events

        if err is not None:
            failed_events += 1
            print(f"Delivery failed: {err}")
        else:
            delivered_events += 1
            print(f"Produced event to {msg.topic()} partition={msg.partition()} offset={msg.offset()}")

    started_at = datetime.now(timezone.utc)
    start_time = time.perf_counter()

    print(f"Producing events to topic={EVENT_TOPIC}, brokers={KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Target event count={EVENT_COUNT}, delay={EVENT_DELAY_SECONDS}s")

    for index in range(1, EVENT_COUNT + 1):
        event = make_event(index)
        producer.produce(
            EVENT_TOPIC,
            key=event["event_id"],
            value=json.dumps(event),
            callback=delivery_report,
        )
        producer.poll(0)
        print(f"Queued {event['event_id']} type={event['event_type']}")
        time.sleep(EVENT_DELAY_SECONDS)

    producer.flush()

    ended_at = datetime.now(timezone.utc)
    duration_seconds = round(time.perf_counter() - start_time, 4)
    events_per_second = round(delivered_events / duration_seconds, 4) if duration_seconds > 0 else 0.0

    metrics = {
        "pipeline_name": "retailflow_realtime_events",
        "component": "ecommerce_event_producer",
        "topic": EVENT_TOPIC,
        "bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS,
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "duration_seconds": duration_seconds,
        "target_event_count": EVENT_COUNT,
        "delivered_event_count": delivered_events,
        "failed_event_count": failed_events,
        "events_per_second": events_per_second,
        "status": "success" if failed_events == 0 and delivered_events == EVENT_COUNT else "partial_failure",
    }

    write_pipeline_metrics(metrics)

    print("Event production completed.")
    print(f"Delivered events: {delivered_events}/{EVENT_COUNT}")
    print(f"Failed events: {failed_events}")
    print(f"Duration seconds: {duration_seconds}")
    print(f"Events per second: {events_per_second}")
    print(f"Metrics written to {PIPELINE_METRICS_PATH}")


if __name__ == "__main__":
    main()
