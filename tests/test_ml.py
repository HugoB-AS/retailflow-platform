import json
from pathlib import Path


def test_model_summary_report_exists_and_is_valid_json():
    report_path = Path("ml/reports/model_summary.json")

    assert report_path.exists()

    data = json.loads(report_path.read_text(encoding="utf-8"))

    assert isinstance(data, dict)
    assert len(data) > 0


def test_core_model_reports_exist():
    expected_reports = [
        "ml/reports/churn_model_report.json",
        "ml/reports/clv_model_report.json",
        "ml/reports/segmentation_model_report.json",
        "ml/reports/drift_report.json",
    ]

    for report in expected_reports:
        assert Path(report).exists()
