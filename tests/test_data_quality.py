from pipeline.consumer.validators import validate_event


class FakeResult:
    def first(self):
        return (1,)


class FakeConnection:
    def execute(self, *args, **kwargs):
        return FakeResult()


def test_validate_event_accepts_valid_event():
    event = {
        "event_id": "evt_test_001",
        "event_type": "product_view",
        "customer_id": "cust_000001",
        "product_id": "prod_000001",
        "event_timestamp": "2025-01-01T10:00:00",
    }

    errors = validate_event(event, FakeConnection())

    assert errors == []


def test_validate_event_rejects_missing_event_type():
    event = {
        "event_id": "evt_test_002",
        "customer_id": "cust_000001",
        "event_timestamp": "2025-01-01T10:00:00",
    }

    errors = validate_event(event, FakeConnection())

    assert any(error["rule_id"] == "R002" for error in errors)
