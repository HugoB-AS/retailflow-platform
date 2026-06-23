from __future__ import annotations

import json
import os
from functools import lru_cache

from confluent_kafka import Producer


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
EVENT_TOPIC = os.getenv("EVENT_TOPIC", "retailflow_events")


@lru_cache(maxsize=1)
def get_producer() -> Producer:
    """Create the Kafka producer only when an event is actually published.

    The FastAPI app imports routes during tests and startup. Creating a Kafka
    producer at import time causes noisy connection attempts when Redpanda is
    not available, even for tests that do not publish events.

    Lazy initialization keeps the production behavior unchanged while making
    unit tests and CI cleaner.
    """
    return Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})


def publish_event(event: dict) -> None:
    """Publish one event to the RetailFlow real-time topic."""
    producer = get_producer()

    producer.produce(
        EVENT_TOPIC,
        key=event.get("event_id"),
        value=json.dumps(event).encode("utf-8"),
    )
    producer.flush()
