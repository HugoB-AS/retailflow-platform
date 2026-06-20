import json
from pathlib import Path


def test_model_registry_exists_and_is_valid_json():
    registry_path = Path("ml/model_registry.json")

    assert registry_path.exists()

    registry = json.loads(registry_path.read_text(encoding="utf-8"))

    assert registry["project"] == "RetailFlow"
    assert registry["registry_type"] == "ml_model_registry"
    assert "models" in registry


def test_model_registry_contains_expected_models():
    registry = json.loads(Path("ml/model_registry.json").read_text(encoding="utf-8"))

    expected_models = {"churn", "clv", "segmentation"}

    assert expected_models.issubset(set(registry["models"].keys()))


def test_model_registry_artifacts_are_available():
    registry = json.loads(Path("ml/model_registry.json").read_text(encoding="utf-8"))

    for model_name in ["churn", "clv", "segmentation"]:
        model = registry["models"][model_name]

        assert model["artifact_exists"] is True
        assert Path(model["artifact_path"]).exists()
        assert model["status"] == "active"


def test_model_registry_contains_monitoring_information():
    registry = json.loads(Path("ml/model_registry.json").read_text(encoding="utf-8"))

    assert "monitoring" in registry
    assert "drift" in registry["monitoring"]
    assert "status" in registry["monitoring"]["drift"]
