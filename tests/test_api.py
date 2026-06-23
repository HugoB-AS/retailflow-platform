from fastapi.testclient import TestClient

from api.app.main import app


def test_openapi_schema_is_available():
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json().get("info", {}).get("title") == "RetailFlow API"
