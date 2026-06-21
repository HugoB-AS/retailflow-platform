import os
import requests
import streamlit as st

from components import (
    load_css,
    hero,
    section_title,
    info_card,
    proof_card,
    block_badges,
    architecture_overview,
    technical_evidence,
    academic_mapping,
    tool_links,
    footer_note,
)


API_URL = os.getenv("API_URL", "http://fastapi:8000")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
AIRFLOW_URL = os.getenv("AIRFLOW_URL", "http://airflow-webserver:8080")
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://grafana:3000")

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
block_badges(["Bloc 1", "Bloc 2", "Bloc 3", "Bloc 4"])

section_title("RetailFlow en une phrase")

st.markdown(
    """
    **RetailFlow transforme des événements clients e-commerce en décisions métier actionnables
    grâce à une plateforme data/IA gouvernée, observable et industrialisée.**

    La plateforme est pensée comme un démonstrateur de retail intelligence : elle relie
    parcours client, pipelines temps réel, gouvernance, qualité, MLOps, API serving,
    CI/CD et observabilité dans une architecture cohérente.
    """
)

section_title("Problem statement")

st.markdown(
    """
    **Research question**

    *Comment concevoir une plateforme data moderne pour le e-commerce combinant pipelines temps réel,
    intelligence artificielle et observabilité afin d’améliorer la prise de décision métier ?*

    RetailFlow simule l'utilisation d'une plateforme de retail intelligence par une entreprise
    e-commerce multi-catégories.
    """
)

section_title("Platform status")

api_health = safe_get_json(f"{API_URL}/health")
ai_summary = safe_get_json(f"{API_URL}/ai/summary")
airflow_health = safe_get_json(f"{AIRFLOW_URL}/health")
grafana_health = safe_get_json(f"{GRAFANA_URL}/api/health")

try:
    prom_response = requests.get(f"{PROMETHEUS_URL}/-/ready", timeout=3)
    prom_ready = prom_response.status_code == 200
except Exception:
    prom_ready = None

col1, col2, col3, col4, col5 = st.columns(5)

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

with col5:
    grafana_ok = None
    if grafana_health:
        grafana_ok = grafana_health.get("database") == "ok"
    status_badge("Grafana", grafana_ok)

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

section_title("Tool access")

tool_links(
    [
        {"label": "FastAPI Docs", "url": "http://127.0.0.1:8000/docs"},
        {"label": "Streamlit", "url": "http://127.0.0.1:8501"},
        {"label": "Airflow", "url": "http://127.0.0.1:8080"},
        {"label": "Prometheus", "url": "http://127.0.0.1:9090"},
        {"label": "Grafana", "url": "http://127.0.0.1:3000"},
        {"label": "pgAdmin", "url": "http://127.0.0.1:5050"},
    ]
)

section_title("Architecture overview")

architecture_overview()

st.markdown(
    """
    Cette architecture illustre un flux end-to-end : les événements clients sont streamés,
    contrôlés, stockés, orchestrés, utilisés pour entraîner des modèles ML, exposés par API,
    puis visualisés dans Streamlit et Grafana.
    """
)

section_title("Academic block mapping overview")

b1, b2 = st.columns(2)

with b1:
    info_card(
        "Bloc 1 — Data Governance",
        "Consentements, politiques de rétention, anonymisation, auditabilité, RGPD, risques data et parties prenantes.",
    )

with b2:
    info_card(
        "Bloc 2 — Data Architecture",
        "Docker Compose, PostgreSQL, Redpanda, FastAPI, Streamlit, Airflow, Prometheus, Grafana et documentation d'exploitation.",
    )

b3, b4 = st.columns(2)

with b3:
    info_card(
        "Bloc 3 — Real-time Data Pipelines",
        "Ingestion événementielle, validation, dead letters, data quality, Airflow et monitoring pipeline.",
    )

with b4:
    info_card(
        "Bloc 4 — AI / MLOps",
        "Churn prediction, CLV, segmentation, API serving, retraining, model registry, drift monitoring et CI/CD.",
    )

section_title("Business capabilities")

c1, c2, c3 = st.columns(3)

with c1:
    info_card(
        "Customer journey simulation",
        "Simuler discovery, product view, cart, checkout et purchase events depuis une vue client.",
    )

with c2:
    info_card(
        "Customer intelligence",
        "Identifier churn risk, CLV, segments métier et recommandations actionnables.",
    )

with c3:
    info_card(
        "Operational readiness",
        "Surveiller santé plateforme, latence API, PostgreSQL, alerting rules, CI/CD et drift ML.",
    )

section_title("Live demo flow")

demo_steps = [
    {
        "Step": 1,
        "Page": "Platform Overview",
        "Purpose": "Comprendre le contexte RetailFlow, la stack et l'état live.",
    },
    {
        "Step": 2,
        "Page": "Customer View",
        "Purpose": "Générer un parcours client et des événements temps réel.",
    },
    {
        "Step": 3,
        "Page": "Customer Intelligence",
        "Purpose": "Transformer les données clients en décisions métier.",
    },
    {
        "Step": 4,
        "Page": "Data Governance",
        "Purpose": "Montrer consentement, rétention, anonymisation, risques et audit.",
    },
    {
        "Step": 5,
        "Page": "Data Architecture",
        "Purpose": "Présenter l'infrastructure, les services, les schemas et l'exploitation.",
    },
    {
        "Step": 6,
        "Page": "Data Quality",
        "Purpose": "Montrer validation, dead letters et qualité pipeline.",
    },
    {
        "Step": 7,
        "Page": "AI Monitoring",
        "Purpose": "Montrer performance ML, drift, registry et retraining.",
    },
    {
        "Step": 8,
        "Page": "Observability",
        "Purpose": "Montrer Prometheus, Grafana, alert rules et métriques plateforme.",
    },
    {
        "Step": 9,
        "Page": "CI/CD and Operations",
        "Purpose": "Montrer tests, build, security reports et opérations.",
    },
    {
        "Step": 10,
        "Page": "Project Evidence",
        "Purpose": "Retrouver rapidement les preuves par bloc, outil et emplacement.",
    },
]

st.dataframe(demo_steps, use_container_width=True, hide_index=True)

section_title("Project scope and assumptions")

with st.expander("Project scope and assumptions"):
    st.markdown(
        """
        RetailFlow est un démonstrateur académique complet, construit pour représenter
        une plateforme de retail intelligence moderne.

        **Périmètre couvert :**

        - données clients et événements e-commerce ;
        - ingestion temps réel ;
        - stockage PostgreSQL structuré par zones ;
        - gouvernance, consentement, rétention et audit ;
        - contrôle qualité et dead-letter events ;
        - modèles ML churn, CLV et segmentation ;
        - API serving avec FastAPI ;
        - orchestration avec Airflow ;
        - monitoring avec Prometheus et Grafana ;
        - CI/CD avec GitHub Actions.

        **Hypothèse principale :**
        la plateforme est exécutée localement via Docker Compose pour démontrer les concepts
        d'architecture, de data engineering, de gouvernance, de MLOps et d'observabilité
        sans prétendre être un déploiement cloud hautement disponible.
        """
    )

academic_mapping(
    [
        {
            "Bloc": "Bloc 1",
            "Section": "Academic block mapping / Data Governance",
            "Preuve": "Le projet intègre consentement, rétention, auditabilité, risques et responsabilités.",
        },
        {
            "Bloc": "Bloc 2",
            "Section": "Architecture overview / Tool access",
            "Preuve": "L'architecture déployée combine stockage, API, orchestration, monitoring et documentation.",
        },
        {
            "Bloc": "Bloc 3",
            "Section": "Architecture overview / Live demo flow",
            "Preuve": "Le parcours client alimente un pipeline événementiel temps réel.",
        },
        {
            "Bloc": "Bloc 4",
            "Section": "Business capabilities / Platform status",
            "Preuve": "Les prédictions IA, l'API serving, le monitoring et la CI/CD sont intégrés au produit.",
        },
    ]
)

technical_evidence(
    {
        "Runtime endpoints": [
            "`GET /health`",
            "`GET /ai/summary`",
            "`Airflow /health`",
            "`Prometheus /-/ready`",
            "`Grafana /api/health`",
        ],
        "Main Streamlit pages": [
            "`1_Platform_Overview.py`",
            "`2_Customer_View.py`",
            "`3_Customer_Intelligence.py`",
            "`4_Data_Governance.py`",
            "`5_Data_Architecture.py`",
            "`6_Data_Quality.py`",
            "`7_AI_Monitoring.py`",
            "`8_Observability.py`",
            "`9_CI_CD_and_Operations.py`",
            "`10_Project_Evidence.py`",
        ],
        "External tools": [
            "FastAPI",
            "Airflow",
            "pgAdmin",
            "PostgreSQL",
            "Prometheus",
            "Grafana",
            "GitHub Actions",
        ],
    }
)

footer_note()
