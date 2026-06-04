import os
import requests
import streamlit as st

from components import (
    load_css,
    hero,
    section_title,
    info_card,
    architecture_overview,
    footer_note,
)


API_URL = os.getenv("API_URL", "http://fastapi:8000")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
AIRFLOW_URL = os.getenv("AIRFLOW_URL", "http://airflow-webserver:8080")

st.set_page_config(
    page_title="RetailFlow Platform Overview",
    page_icon="🔷",
    layout="wide",
)

load_css()


def safe_get_json(url: str, timeout: int = 3):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def status_badge(label: str, ok: bool | None):
    if ok is True:
        css = "rf-status-green"
        text = "healthy"
    elif ok is False:
        css = "rf-status-red"
        text = "down"
    else:
        css = "rf-status-amber"
        text = "unknown"

    st.markdown(
        f'<span class="rf-status {css}">● {label}: {text}</span>',
        unsafe_allow_html=True,
    )


hero()

section_title("Problem statement")

st.markdown(
    """
    **Research question**  
    *Comment concevoir une plateforme data moderne pour le e-commerce combinant pipelines temps réel,
    intelligence artificielle et observabilité afin d’améliorer la prise de décision métier ?*

    RetailFlow est une plateforme de retail intelligence qui transforme des événements clients
    en données exploitables pour la décision métier, le pilotage opérationnel et le monitoring ML.
    """
)

section_title("Platform status")

api_health = safe_get_json(f"{API_URL}/health")
ai_summary = safe_get_json(f"{API_URL}/ai/summary")
airflow_health = safe_get_json(f"{AIRFLOW_URL}/health")

try:
    prom_response = requests.get(f"{PROMETHEUS_URL}/-/ready", timeout=3)
    prom_ready = prom_response.status_code == 200
except Exception:
    prom_ready = None

col1, col2, col3, col4 = st.columns(4)

with col1:
    status_badge("FastAPI", bool(api_health and api_health.get("status") == "ok"))

with col2:
    status_badge("PostgreSQL", bool(api_health and api_health.get("database") == "connected"))

with col3:
    scheduler_ok = None
    if airflow_health:
        scheduler_ok = airflow_health.get("scheduler", {}).get("status") == "healthy"
    status_badge("Airflow", scheduler_ok)

with col4:
    status_badge("Prometheus", prom_ready)

if ai_summary:
    freshness = ai_summary.get("prediction_freshness", {}) or {}

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Predicted customers", freshness.get("predicted_customers", 0))

    with k2:
        st.metric("Prediction rows", freshness.get("prediction_rows", 0))

    with k3:
        churn_high = 0
        for row in ai_summary.get("predictions_by_model", []):
            if row.get("model_name") == "churn_model" and row.get("prediction_label") == "high_risk":
                churn_high = row.get("predictions_count", 0)
        st.metric("High churn risk", churn_high)

    with k4:
        st.metric("Customer segments", len(ai_summary.get("segments", [])))

section_title("Architecture overview")

architecture_overview()

st.markdown(
    """
    Cette architecture illustre un flux end-to-end : les événements clients sont streamés,
    contrôlés, stockés, orchestrés, utilisés pour entraîner des modèles ML, exposés par API,
    puis visualisés dans Streamlit et Grafana.
    """
)

section_title("Academic block mapping")

b1, b2 = st.columns(2)

with b1:
    info_card(
        "Bloc 1 — Data Governance",
        "Consentements, politiques de rétention, anonymisation, auditabilité, RGPD et gestion des risques data.",
    )

with b2:
    info_card(
        "Bloc 2 — Data Architecture",
        "Architecture Docker, PostgreSQL, FastAPI, Streamlit, Prometheus, Grafana et PostgreSQL exporter.",
    )

b3, b4 = st.columns(2)

with b3:
    info_card(
        "Bloc 3 — Real-time Data Pipelines",
        "Redpanda, consumer Python, ingestion événementielle, dead letters, data quality et orchestration Airflow.",
    )

with b4:
    info_card(
        "Bloc 4 — AI / MLOps",
        "Churn prediction, CLV, segmentation, retraining Airflow, API serving, drift monitoring et rapports ML.",
    )

section_title("Business capabilities")

c1, c2, c3 = st.columns(3)

with c1:
    info_card(
        "Customer journey simulation",
        "Simulate product discovery, product details, cart and checkout events from the customer point of view.",
    )

with c2:
    info_card(
        "Customer intelligence",
        "Identify churn candidates, high-value customers, business segments and actionable recommendations.",
    )

with c3:
    info_card(
        "Operational readiness",
        "Monitor platform health, API latency, PostgreSQL status, alerting rules and ML drift signals.",
    )

section_title("Airflow orchestration")

a1, a2, a3, a4 = st.columns(4)

with a1:
    info_card(
        "daily_sales_aggregation",
        "Builds daily business aggregates for analytics usage.",
    )

with a2:
    info_card(
        "daily_data_quality",
        "Runs data quality checks and supports monitoring of pipeline reliability.",
    )

with a3:
    info_card(
        "ml_retraining",
        "Retrains ML models, refreshes predictions and produces monitoring reports.",
    )

with a4:
    info_card(
        "retention_cleanup",
        "Applies retention and anonymization logic for governance compliance.",
    )

section_title("Live demo flow")

st.markdown(
    """
    1. **Platform Overview** — explique la problématique, l’architecture et le mapping aux blocs.  
    2. **Customer View** — simule un parcours e-commerce et génére des événements.  
    3. **Customer Intelligence** — montre churn, CLV, segmentation et recommandations métier.  
    4. **Data Governance** — explique consentement, rétention, anonymisation et audit.  
    5. **Data Quality** — montre les erreurs rejetées, règles qualité et dead-letter events.  
    6. **AI Monitoring** — présente métriques ML, feature importance, cross-validation et drift.  
    7. **Observability** — Prometheus/Grafana et montre la supervision plateforme.
    """
)

with st.expander("Positioning note for the jury"):
    st.markdown(
        """
        RetailFlow n’est pas seulement un dashboard : c’est une plateforme data complète.
        Elle combine architecture, pipelines temps réel, gouvernance, MLOps, API serving,
        monitoring et observability dans un scénario retail avec la logique d’architecture 
        et d’industrialisation proche d’une plateforme startup moderne.
        """
    )

footer_note()
