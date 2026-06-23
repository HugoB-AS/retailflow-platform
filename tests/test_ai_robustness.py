from fastapi.testclient import TestClient

from api.app.main import app
from ml.src.predict import clv_label, feature_hash, risk_label


client = TestClient(app)


def test_risk_label_boundaries():
    assert risk_label(0.0) == "low_risk"
    assert risk_label(0.3999) == "low_risk"
    assert risk_label(0.40) == "medium_risk"
    assert risk_label(0.6999) == "medium_risk"
    assert risk_label(0.70) == "high_risk"
    assert risk_label(1.0) == "high_risk"


def test_risk_label_with_custom_thresholds():
    thresholds = {
        "high_risk": 0.80,
        "medium_risk": 0.50,
    }

    assert risk_label(0.49, thresholds) == "low_risk"
    assert risk_label(0.50, thresholds) == "medium_risk"
    assert risk_label(0.80, thresholds) == "high_risk"


def test_clv_label_boundaries():
    assert clv_label(-100.0) == "low_value"
    assert clv_label(0.0) == "low_value"
    assert clv_label(2999.99) == "low_value"
    assert clv_label(3000.0) == "medium_value"
    assert clv_label(9999.99) == "medium_value"
    assert clv_label(10000.0) == "high_value"


def test_clv_label_with_custom_thresholds():
    thresholds = {
        "high_value": 5000,
        "medium_value": 1000,
    }

    assert clv_label(999.99, thresholds) == "low_value"
    assert clv_label(1000.0, thresholds) == "medium_value"
    assert clv_label(5000.0, thresholds) == "high_value"


def test_feature_hash_is_deterministic_and_unique():
    first_hash = feature_hash("cust_000001", "churn_model", "v2_realism")
    second_hash = feature_hash("cust_000001", "churn_model", "v2_realism")
    different_customer_hash = feature_hash("cust_000002", "churn_model", "v2_realism")

    assert first_hash == second_hash
    assert first_hash != different_customer_hash
    assert len(first_hash) == 64


def test_ai_model_reports_endpoint_is_available():
    response = client.get("/ai/model-reports")

    assert response.status_code == 200

    payload = response.json()

    assert "reports" in payload
    assert "model_summary" in payload["reports"]
    assert "churn" in payload["reports"]
    assert "clv" in payload["reports"]
    assert "segmentation" in payload["reports"]
    assert "drift" in payload["reports"]


def test_ai_model_report_endpoint_returns_allowed_report():
    response = client.get("/ai/model-report/model_summary")

    assert response.status_code == 200

    payload = response.json()

    assert payload["project"] == "RetailFlow"
    assert payload["summary_type"] == "ml_model_summary"


def test_ai_model_report_endpoint_rejects_unknown_report():
    response = client.get("/ai/model-report/unknown_report")

    assert response.status_code == 404
    assert response.json()["detail"] == "Unknown model report"


def test_ai_model_report_endpoint_rejects_path_traversal_like_input():
    response = client.get("/ai/model-report/..%2F..%2FREADME")

    assert response.status_code in {404, 422}


# TODO:
# When a dedicated PostgreSQL test database is available, add robustness tests for
# DB-backed AI endpoints:
# - /ai/churn-top
# - /ai/clv-top
# - /ai/segments
# - /ai/customers
# - /ai/customer/{customer_id}
# - /ai/summary
