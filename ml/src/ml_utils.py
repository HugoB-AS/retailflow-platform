from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import joblib
import numpy as np
import pandas as pd
import psycopg2

from ml.src.db import DATABASE_URL

MODEL_DIR = Path("ml/models")
REPORT_DIR = Path("ml/reports")

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_psycopg2_connection():
    database_url = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")
    parsed = urlparse(database_url)

    return psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        dbname=parsed.path.lstrip("/"),
        user=parsed.username,
        password=parsed.password,
    )


def load_customer_features() -> pd.DataFrame:
    query = "SELECT * FROM analytics.customer_features"

    conn = get_psycopg2_connection()
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def sigmoid(values):
    return 1 / (1 + np.exp(-values))


def make_json_safe(value: Any):
    if isinstance(value, dict):
        return {str(k): make_json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [make_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [make_json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return make_json_safe(value.tolist())
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def safe_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    path.write_text(content, encoding="utf-8")


def safe_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    path.write_text(
        json.dumps(make_json_safe(payload), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def safe_joblib_dump(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    joblib.dump(payload, path)


def write_report(base_name: str, title: str, report: dict, text_lines: list[str]) -> None:
    json_path = REPORT_DIR / f"{base_name}.json"
    txt_path = REPORT_DIR / f"{base_name}.txt"

    safe_write_json(json_path, report)

    body = [title, "=" * len(title), ""]
    body.extend(text_lines)
    body.append("")
    body.append(f"Generated at: {report.get('generated_at')}")
    safe_write_text(txt_path, "\n".join(body))


def extract_feature_importance(model, features: list[str]) -> list[dict]:
    estimator = model

    if hasattr(model, "named_steps"):
        estimator = model.named_steps.get("model", model)

    importances = None

    if hasattr(estimator, "feature_importances_"):
        importances = estimator.feature_importances_
    elif hasattr(estimator, "coef_"):
        coef = estimator.coef_
        importances = np.abs(coef[0] if len(coef.shape) > 1 else coef)

    if importances is None:
        return []

    rows = []
    total = float(np.sum(np.abs(importances))) or 1.0

    for feature, value in zip(features, importances):
        rows.append({
            "feature": feature,
            "importance": float(value),
            "normalized_importance": float(abs(value) / total),
        })

    return sorted(rows, key=lambda row: row["normalized_importance"], reverse=True)


def summarize_numeric_dict(values: dict) -> list[str]:
    lines = []
    for key, value in values.items():
        lines.append(f"- {key}: {value}")
    return lines
