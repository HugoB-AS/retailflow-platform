from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "ml" / "reports"
MODELS_DIR = PROJECT_ROOT / "ml" / "models"
MODEL_REGISTRY_PATH = PROJECT_ROOT / "ml" / "model_registry.json"
# Append-only lightweight run history used as evidence for retraining
# traceability. The file keeps the latest runs to avoid uncontrolled growth.
RETRAINING_RUNS_PATH = REPORTS_DIR / "retraining_runs.json"


MODEL_ARTIFACTS = {
    "churn": MODELS_DIR / "churn_model.joblib",
    "clv": MODELS_DIR / "clv_model.joblib",
    "segmentation": MODELS_DIR / "segmentation_model.joblib",
}


def utc_now_iso() -> str:
    """Return a timezone-aware UTC timestamp serialized as ISO 8601."""

    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any = None) -> Any:
    """Read JSON if available, otherwise return a safe default."""

    if not path.exists():
        return default

    return json.loads(path.read_text(encoding="utf-8"))


def relative_path(path: Path) -> str:
    """Return repository-relative paths for portable run history entries."""

    return str(path.relative_to(PROJECT_ROOT))


def file_metadata(path: Path) -> dict[str, Any]:
    """Collect existence, size and modification timestamp for audit evidence."""

    if not path.exists():
        return {
            "path": relative_path(path),
            "exists": False,
            "size_bytes": None,
            "modified_at": None,
        }

    stat = path.stat()

    return {
        "path": relative_path(path),
        "exists": True,
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
    }


def build_run_payload() -> dict[str, Any]:
    """""Build one retraining run record.

    When executed by Airflow, AIRFLOW_CTX_* variables are captured. When executed
    manually, the script still produces a valid run record for local validation.
    """
    model_summary = read_json(REPORTS_DIR / "model_summary.json", default={})
    model_registry = read_json(MODEL_REGISTRY_PATH, default={})
    drift_report = read_json(REPORTS_DIR / "drift_report.json", default={})

    airflow_dag_id = os.getenv("AIRFLOW_CTX_DAG_ID")
    airflow_run_id = os.getenv("AIRFLOW_CTX_DAG_RUN_ID")
    airflow_task_id = os.getenv("AIRFLOW_CTX_TASK_ID")

    generated_at = utc_now_iso()
    run_id = airflow_run_id or f"manual_retraining_{generated_at.replace(':', '').replace('-', '').replace('+00:00', 'Z')}"

    models = {}

    for model_name, artifact_path in MODEL_ARTIFACTS.items():
        registry_model = model_registry.get("models", {}).get(model_name, {})
        summary_model = model_summary.get(model_name, {})

        models[model_name] = {
            "model_version": registry_model.get("model_version") or summary_model.get("model_version"),
            "selected_model": registry_model.get("selected_model") or summary_model.get("selected_model"),
            "task_type": registry_model.get("task_type"),
            "artifact": file_metadata(artifact_path),
            "main_metrics": registry_model.get("main_metrics", {}),
            "status": registry_model.get("status", "unknown"),
        }

    drift_summary = {
        "available": model_summary.get("drift", {}).get("available"),
        "drift_detected": model_summary.get("drift", {}).get("drift_detected"),
        "drifted_features_count": model_summary.get("drift", {}).get("drifted_features_count"),
        "threshold": model_summary.get("drift", {}).get("threshold"),
        "status": model_registry.get("monitoring", {}).get("drift", {}).get("status"),
        "report_path": "ml/reports/drift_report.json",
    }

    required_reports = [
        REPORTS_DIR / "churn_model_report.json",
        REPORTS_DIR / "clv_model_report.json",
        REPORTS_DIR / "segmentation_model_report.json",
        REPORTS_DIR / "drift_report.json",
        REPORTS_DIR / "model_summary.json",
        MODEL_REGISTRY_PATH,
    ]

    required_artifacts = list(MODEL_ARTIFACTS.values())

    missing_files = [
        relative_path(path)
        for path in required_reports + required_artifacts
        if not path.exists()
    ]

    return {
        "run_id": run_id,
        "logged_at": generated_at,
        "trigger": "airflow" if airflow_dag_id else "manual",
        "airflow_context": {
            "dag_id": airflow_dag_id,
            "dag_run_id": airflow_run_id,
            "task_id": airflow_task_id,
        },
        "pipeline": {
            "name": "ml_retraining",
            "steps": [
                "train_churn_model",
                "train_segmentation_model",
                "train_clv_model",
                "refresh_ml_predictions",
                "evaluate_lightweight_drift",
                "generate_model_registry",
                "log_retraining_run",
            ],
        },
        "models": models,
        "monitoring": {
            "drift": drift_summary,
        },
        "reports": {
            "model_summary": file_metadata(REPORTS_DIR / "model_summary.json"),
            "model_registry": file_metadata(MODEL_REGISTRY_PATH),
            "drift_report": file_metadata(REPORTS_DIR / "drift_report.json"),
        },
        "missing_files": missing_files,
        "status": "success" if not missing_files else "warning_missing_files",
    }


def load_run_history() -> dict[str, Any]:
    """Load the existing retraining history or initialize a new one."""

    if not RETRAINING_RUNS_PATH.exists():
        return {
            "project": "RetailFlow",
            "registry_type": "ml_retraining_runs",
            "created_at": utc_now_iso(),
            "last_updated_at": None,
            "runs": [],
        }

    return read_json(RETRAINING_RUNS_PATH, default={
        "project": "RetailFlow",
        "registry_type": "ml_retraining_runs",
        "runs": [],
    })


def write_run_history(history: dict[str, Any]) -> None:
    """Persist the retraining history as formatted JSON."""

    RETRAINING_RUNS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RETRAINING_RUNS_PATH.write_text(
        json.dumps(history, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    """Append a new retraining run to ml/reports/retraining_runs.json."""

    history = load_run_history()
    run_payload = build_run_payload()

    existing_runs = history.get("runs", [])
    existing_runs.append(run_payload)

    history["project"] = "RetailFlow"
    history["registry_type"] = "ml_retraining_runs"
    history["last_updated_at"] = utc_now_iso()
    history["runs"] = existing_runs[-20:]

    write_run_history(history)

    print(f"Retraining run logged to {relative_path(RETRAINING_RUNS_PATH)}")
    print(f"Run id: {run_payload['run_id']}")
    print(f"Status: {run_payload['status']}")


if __name__ == "__main__":
    main()
