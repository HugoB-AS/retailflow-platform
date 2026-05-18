import json
import os

from confluent_kafka import Producer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
EVENT_TOPIC = os.getenv("EVENT_TOPIC", "retailflow_events")

producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})


def publish_event(event: dict) -> None:
    producer.produce(
        EVENT_TOPIC,
        key=event.get("event_id"),
        value=json.dumps(event).encode("utf-8"),
    )
    producer.flush()
