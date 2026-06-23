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


def test_model_registry_tracks_expected_artifact_paths():
    registry = json.loads(Path("ml/model_registry.json").read_text(encoding="utf-8"))

    expected_artifacts = {
        "churn": "ml/models/churn_model.joblib",
        "clv": "ml/models/clv_model.joblib",
        "segmentation": "ml/models/segmentation_model.joblib",
    }

    for model_name, expected_path in expected_artifacts.items():
        model = registry["models"][model_name]

        assert model["artifact_path"] == expected_path
        assert "artifact_exists" in model
        assert model["status"] in {"active", "missing_artifact"}


def test_model_registry_contains_monitoring_information():
    registry = json.loads(Path("ml/model_registry.json").read_text(encoding="utf-8"))

    assert "monitoring" in registry
    assert "drift" in registry["monitoring"]
    assert "status" in registry["monitoring"]["drift"]
