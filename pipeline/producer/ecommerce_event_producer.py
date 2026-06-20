from __future__ import annotations

import json
import os
import random
import time
from datetime import datetime, timezone
from uuid import uuid4

from confluent_kafka import Producer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092")
EVENT_TOPIC = os.getenv("EVENT_TOPIC", "retailflow_events")


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

    event_id = f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}{index}{uuid4().hex[:6]}"

    return {
        "event_id": event_id,
        "customer_id": customer_id,
        "session_id": f"sess_live_{uuid4().hex[:10]}",
        "event_type": event_type,
        "product_id": product_id,
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
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
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def delivery_report(err, msg) -> None:
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Produced event to {msg.topic()} partition={msg.partition()} offset={msg.offset()}")


def main() -> None:
    producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})

    print(f"Producing events to topic={EVENT_TOPIC}, brokers={KAFKA_BOOTSTRAP_SERVERS}")

    for index in range(1, 21):
        event = make_event(index)
        producer.produce(
            EVENT_TOPIC,
            key=event["event_id"],
            value=json.dumps(event),
            callback=delivery_report,
        )
        producer.poll(0)
        print(f"Queued {event['event_id']} type={event['event_type']}")
        time.sleep(0.3)

    producer.flush()
    print("Event production completed.")


if __name__ == "__main__":
    main()
