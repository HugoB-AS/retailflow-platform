import json
import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from components import (
    load_css,
    section_title,
    info_card,
    proof_card,
    block_badges,
    technical_evidence,
    academic_mapping,
    footer_note,
)


API_URL = os.getenv("API_URL", "http://fastapi:8000")

st.set_page_config(
    page_title="RetailFlow AI Monitoring",
    page_icon="🤖",
    layout="wide",
)

load_css()


def api_get(path: str, params=None):
    response = requests.get(f"{API_URL}{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def safe_api_get(path: str, params=None, default=None):
    try:
        return api_get(path, params=params)
    except Exception:
        return default


def find_file(relative_path: str) -> Path | None:
    candidates = [
        Path(relative_path),
        Path("/app") / relative_path,
        Path("/app/streamlit_app") / relative_path,
        Path("/app/streamlit_app").parent / relative_path,
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def read_json_file(relative_path: str, default=None):
    file_path = find_file(relative_path)

    if file_path is None:
        return default

    try:
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return default


def to_dataframe(payload):
    if payload is None:
        return pd.DataFrame()

    if isinstance(payload, list):
        return pd.DataFrame(payload)

    if isinstance(payload, dict):
        for key in ["items", "models", "runs", "reports", "data", "results"]:
            if isinstance(payload.get(key), list):
                return pd.DataFrame(payload[key])

        return pd.DataFrame([payload])

    return pd.DataFrame()


def flatten_registry(registry_payload):
    if not registry_payload:
        return pd.DataFrame()

    if isinstance(registry_payload, list):
        return pd.DataFrame(registry_payload)

    if isinstance(registry_payload, dict):
        if isinstance(registry_payload.get("models"), list):
            return pd.DataFrame(registry_payload["models"])

        rows = []

        for model_name, value in registry_payload.items():
            if isinstance(value, dict):
                row = {"model_name": model_name}
                row.update(value)
                rows.append(row)

        if rows:
            return pd.DataFrame(rows)

        return pd.DataFrame([registry_payload])

    return pd.DataFrame()


def format_status(value) -> str:
    if value in [True, "true", "True", "ok", "healthy", "success"]:
        return "OK"

    if value in [False, "false", "False", "failed", "error"]:
        return "Attention"

    if value in [None, ""]:
        return "N/A"

    return str(value)


def get_analytics_consent_count(governance_summary: dict, ai_summary: dict) -> int:
    consent = governance_summary.get("consent", {}) or {}
    freshness = ai_summary.get("prediction_freshness", {}) or {}

    value = consent.get("analytics_consent_count")

    if value is None:
        value = freshness.get("predicted_customers", 0)

    try:
        return int(value or 0)
    except Exception:
        return 0


def latest_file_modified(relative_path: str) -> str:
    file_path = find_file(relative_path)

    if file_path is None:
        return "Not found"

    try:
        return pd.to_datetime(file_path.stat().st_mtime, unit="s").strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "Unknown"


st.title("🤖 AI Monitoring")
block_badges(["Bloc 4"])

st.markdown(
    """
    Cette page présente le monitoring MLOps de RetailFlow :
    prédictions disponibles, registre de modèles, rapports d'entraînement,
    suivi du drift, retraining et preuves de maintenabilité.
    """
)

try:
    summary = safe_api_get("/ai/summary", default={}) or {}
    governance_summary = safe_api_get("/governance/summary", default={}) or {}

    registry_payload = read_json_file("ml/model_registry.json", default={})
    retraining_payload = read_json_file("ml/reports/retraining_runs.json", default=[])
    model_summary_payload = read_json_file("ml/reports/model_summary.json", default={})
    drift_payload = read_json_file("ml/reports/drift_report.json", default={})

    churn_report = read_json_file("ml/reports/churn_model_report.json", default={})
    clv_report = read_json_file("ml/reports/clv_model_report.json", default={})
    segmentation_report = read_json_file("ml/reports/segmentation_model_report.json", default={})

    df_registry = flatten_registry(registry_payload)
    df_retraining = to_dataframe(retraining_payload)
    df_model_summary = to_dataframe(model_summary_payload)
    df_drift = to_dataframe(drift_payload)

    section_title("AI monitoring overview")

    freshness = summary.get("prediction_freshness", {}) or {}
    analytics_consent_count = get_analytics_consent_count(governance_summary, summary)

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Predicted customers", analytics_consent_count)

    with k2:
        st.metric("Prediction rows", freshness.get("prediction_rows", 0))

    with k3:
        st.metric("Registered models", len(df_registry) if not df_registry.empty else 0)

    with k4:
        st.metric("Retraining runs", len(df_retraining) if not df_retraining.empty else 0)

    section_title("AI use cases")

    u1, u2, u3 = st.columns(3)

    with u1:
        proof_card(
            "Churn prediction",
            "Identifie les clients à risque pour prioriser les campagnes de rétention.",
        )

    with u2:
        proof_card(
            "Customer lifetime value",
            "Estime la valeur future d'un client pour orienter fidélisation, upsell et priorisation.",
        )

    with u3:
        proof_card(
            "Customer segmentation",
            "Regroupe les clients selon leurs comportements pour adapter les actions marketing.",
        )

    section_title("Prediction availability")

    prediction_rows = [
        {
            "Model": "churn_model",
            "Prediction rows": analytics_consent_count,
            "Business usage": "Retention prioritization",
        },
        {
            "Model": "clv_model",
            "Prediction rows": analytics_consent_count,
            "Business usage": "Customer value prioritization",
        },
        {
            "Model": "segmentation_model",
            "Prediction rows": analytics_consent_count,
            "Business usage": "Marketing segmentation",
        },
    ]

    df_prediction_rows = pd.DataFrame(prediction_rows)
    st.dataframe(df_prediction_rows, use_container_width=True, hide_index=True)

    if not df_prediction_rows.empty:
        st.bar_chart(df_prediction_rows.set_index("Model")["Prediction rows"])

    section_title("Model registry")

    st.markdown(
        """
        Le registre de modèles documente les modèles disponibles, leurs versions,
        leurs chemins de sauvegarde et les informations utiles à la reproductibilité.
        """
    )

    if not df_registry.empty:
        st.dataframe(df_registry, use_container_width=True, hide_index=True)
    else:
        st.warning("Model registry not found or empty.")

    with st.expander("Raw model registry"):
        st.json(registry_payload if registry_payload else {"status": "not_found"})

    section_title("Training and retraining evidence")

    if not df_retraining.empty:
        st.dataframe(df_retraining, use_container_width=True, hide_index=True)

        status_col = None
        for candidate in ["status", "run_status", "result"]:
            if candidate in df_retraining.columns:
                status_col = candidate
                break

        if status_col:
            status_counts = df_retraining[status_col].astype(str).value_counts()
            st.subheader("Retraining status distribution")
            st.bar_chart(status_counts)
    else:
        st.info("No retraining run log found yet.")

    with st.expander("Raw retraining runs"):
        st.json(retraining_payload if retraining_payload else {"status": "not_found"})

    section_title("Model reports")

    report_rows = [
        {
            "Report": "Churn model",
            "File": "ml/reports/churn_model_report.json",
            "Last modified": latest_file_modified("ml/reports/churn_model_report.json"),
            "Available": bool(churn_report),
        },
        {
            "Report": "CLV model",
            "File": "ml/reports/clv_model_report.json",
            "Last modified": latest_file_modified("ml/reports/clv_model_report.json"),
            "Available": bool(clv_report),
        },
        {
            "Report": "Segmentation model",
            "File": "ml/reports/segmentation_model_report.json",
            "Last modified": latest_file_modified("ml/reports/segmentation_model_report.json"),
            "Available": bool(segmentation_report),
        },
        {
            "Report": "Model summary",
            "File": "ml/reports/model_summary.json",
            "Last modified": latest_file_modified("ml/reports/model_summary.json"),
            "Available": bool(model_summary_payload),
        },
        {
            "Report": "Drift report",
            "File": "ml/reports/drift_report.json",
            "Last modified": latest_file_modified("ml/reports/drift_report.json"),
            "Available": bool(drift_payload),
        },
    ]

    df_reports = pd.DataFrame(report_rows)
    df_reports["Status"] = df_reports["Available"].apply(format_status)

    st.dataframe(
        df_reports[["Report", "File", "Last modified", "Status"]],
        use_container_width=True,
        hide_index=True,
    )

    r1, r2, r3 = st.columns(3)

    with r1:
        with st.expander("Churn model report"):
            st.json(churn_report if churn_report else {"status": "not_found"})

    with r2:
        with st.expander("CLV model report"):
            st.json(clv_report if clv_report else {"status": "not_found"})

    with r3:
        with st.expander("Segmentation model report"):
            st.json(segmentation_report if segmentation_report else {"status": "not_found"})

    with st.expander("Model summary report"):
        st.json(model_summary_payload if model_summary_payload else {"status": "not_found"})

    section_title("Drift monitoring")

    if drift_payload:
        d1, d2, d3 = st.columns(3)

        if isinstance(drift_payload, dict):
            drift_status = (
                drift_payload.get("status")
                or drift_payload.get("drift_status")
                or drift_payload.get("overall_status")
                or "available"
            )
        else:
            drift_status = "available"

        with d1:
            st.metric("Drift report", format_status(drift_status))

        with d2:
            st.metric("Report file", latest_file_modified("ml/reports/drift_report.json"))

        with d3:
            st.metric("Drift rows", len(df_drift) if not df_drift.empty else 1)

        if not df_drift.empty:
            st.dataframe(df_drift, use_container_width=True, hide_index=True)

        with st.expander("Raw drift report"):
            st.json(drift_payload)
    else:
        st.warning("No drift report found.")

    section_title("MLOps controls")

    controls = [
        {
            "Control": "Model versioning",
            "Purpose": "Identifier les modèles disponibles et leurs artefacts.",
            "Evidence": "`ml/model_registry.json`.",
        },
        {
            "Control": "Reproducible training",
            "Purpose": "Tracer les scripts et rapports utilisés pour entraîner les modèles.",
            "Evidence": "`ml/src/train_*.py` et `ml/reports/*.json`.",
        },
        {
            "Control": "Prediction serving",
            "Purpose": "Exposer les prédictions via une API consommée par l'application.",
            "Evidence": "`GET /ai/customer/{customer_id}` et Customer Intelligence.",
        },
        {
            "Control": "Retraining",
            "Purpose": "Automatiser ou documenter le réentraînement des modèles.",
            "Evidence": "Airflow DAG `ml_retraining.py` et `retraining_runs.json`.",
        },
        {
            "Control": "Drift monitoring",
            "Purpose": "Détecter les écarts entre données d'entraînement et données récentes.",
            "Evidence": "`ml/reports/drift_report.json`.",
        },
        {
            "Control": "Robustness",
            "Purpose": "Tester les comportements limites et éviter les régressions.",
            "Evidence": "Tests ML et GitHub Actions.",
        },
    ]

    st.dataframe(pd.DataFrame(controls), use_container_width=True, hide_index=True)

    section_title("AI operational lifecycle")

    lifecycle = [
        {
            "Step": 1,
            "Phase": "Train",
            "Description": "Entraîner les modèles churn, CLV et segmentation avec les features clients.",
        },
        {
            "Step": 2,
            "Phase": "Evaluate",
            "Description": "Produire des rapports de performance et résumer les métriques clés.",
        },
        {
            "Step": 3,
            "Phase": "Register",
            "Description": "Enregistrer les artefacts et métadonnées dans le model registry.",
        },
        {
            "Step": 4,
            "Phase": "Serve",
            "Description": "Exposer les prédictions via FastAPI pour Streamlit et les usages métier.",
        },
        {
            "Step": 5,
            "Phase": "Monitor",
            "Description": "Surveiller disponibilité, prédictions, drift et cohérence des rapports.",
        },
        {
            "Step": 6,
            "Phase": "Retrain",
            "Description": "Relancer l'entraînement via Airflow ou workflow documenté lorsque nécessaire.",
        },
    ]

    st.dataframe(pd.DataFrame(lifecycle), use_container_width=True, hide_index=True)

    section_title("What this page demonstrates")

    m1, m2, m3 = st.columns(3)

    with m1:
        info_card(
            "AI deployment",
            "Les prédictions sont servies par FastAPI et utilisées dans l'application Streamlit.",
        )

    with m2:
        info_card(
            "Maintainability",
            "Les modèles, rapports, tests et runs de retraining sont documentés.",
        )

    with m3:
        info_card(
            "Monitoring",
            "Le projet expose des preuves de suivi du drift, du retraining et de la disponibilité des prédictions.",
        )

    academic_mapping(
        [
            {
                "Bloc": "Bloc 4",
                "Section": "AI use cases",
                "Preuve": "Cas d'usage IA définis : churn, CLV et segmentation.",
            },
            {
                "Bloc": "Bloc 4",
                "Section": "Prediction availability",
                "Preuve": "Prédictions disponibles et exposées via API.",
            },
            {
                "Bloc": "Bloc 4",
                "Section": "Model registry",
                "Preuve": "Registre de modèles et artefacts pour versioning et reproductibilité.",
            },
            {
                "Bloc": "Bloc 4",
                "Section": "Training and retraining evidence",
                "Preuve": "Runs de réentraînement et preuve d'automatisation MLOps.",
            },
            {
                "Bloc": "Bloc 4",
                "Section": "Drift monitoring",
                "Preuve": "Rapport de drift pour surveiller la dérive des données.",
            },
            {
                "Bloc": "Bloc 4",
                "Section": "MLOps controls",
                "Preuve": "Contrôles de maintenabilité, robustesse, serving, retraining et monitoring.",
            },
        ]
    )

    technical_evidence(
        {
            "FastAPI endpoints": [
                "`GET /ai/summary`",
                "`GET /governance/summary`",
                "`GET /ai/customers`",
                "`GET /ai/customer/{customer_id}`",
                "`GET /ai/churn-top`",
                "`GET /ai/clv-top`",
                "`GET /ai/segments`",
            ],
            "ML reports": [
                "`ml/model_registry.json`",
                "`ml/reports/churn_model_report.json`",
                "`ml/reports/clv_model_report.json`",
                "`ml/reports/segmentation_model_report.json`",
                "`ml/reports/model_summary.json`",
                "`ml/reports/drift_report.json`",
                "`ml/reports/retraining_runs.json`",
            ],
            "Governance link": [
                "`analytics_consent_count` is used as the visible count for AI-authorized predictions.",
            ],
            "MLOps files": [
                "`ml/src/train_churn.py`",
                "`ml/src/train_clv.py`",
                "`ml/src/train_segmentation.py`",
                "`ml/src/predict.py`",
                "`ml/src/generate_model_registry.py`",
                "`ml/src/log_retraining_run.py`",
                "`airflow/dags/ml_retraining.py`",
            ],
            "Tools": [
                "FastAPI",
                "Streamlit",
                "Airflow",
                "PostgreSQL",
                "GitHub Actions",
                "VSCode",
            ],
        }
    )

except Exception as exc:
    st.error(f"Unable to load AI Monitoring data: {exc}")

footer_note()
