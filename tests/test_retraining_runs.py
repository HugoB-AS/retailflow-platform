import json
from pathlib import Path


def test_retraining_runs_report_exists_and_is_valid_json():
    report_path = Path("ml/reports/retraining_runs.json")

    assert report_path.exists()

    data = json.loads(report_path.read_text(encoding="utf-8"))

    assert data["project"] == "RetailFlow"
    assert data["registry_type"] == "ml_retraining_runs"
    assert isinstance(data["runs"], list)
    assert len(data["runs"]) >= 1


def test_latest_retraining_run_contains_expected_sections():
    data = json.loads(Path("ml/reports/retraining_runs.json").read_text(encoding="utf-8"))
    latest_run = data["runs"][-1]

    assert "run_id" in latest_run
    assert "models" in latest_run
    assert "monitoring" in latest_run
    assert "reports" in latest_run
    assert latest_run["status"] in {"success", "warning_missing_files"}


def test_latest_retraining_run_tracks_expected_models():
    data = json.loads(Path("ml/reports/retraining_runs.json").read_text(encoding="utf-8"))
    latest_run = data["runs"][-1]

    expected_models = {"churn", "clv", "segmentation"}

    assert expected_models.issubset(set(latest_run["models"].keys()))
