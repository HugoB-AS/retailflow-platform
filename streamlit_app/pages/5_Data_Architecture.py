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
    architecture_overview,
    technical_evidence,
    academic_mapping,
    tool_links,
    footer_note,
)


API_URL = os.getenv("API_URL", "http://fastapi:8000")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://grafana:3000")

st.set_page_config(
    page_title="RetailFlow Data Architecture",
    page_icon="🏗️",
    layout="wide",
)

load_css()


def safe_get_json(url: str, timeout: int = 5):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def safe_ready(url: str, timeout: int = 5):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception:
        return None


st.title("🏗️ Data Architecture")
block_badges(["Bloc 2", "Bloc 3", "Bloc 4"])

st.markdown(
    """
    Cette page présente l'architecture de données RetailFlow : services Docker,
    stockage PostgreSQL, API serving, orchestration, streaming, monitoring et exploitation.
    """
)

section_title("Architecture status")

api_health = safe_get_json(f"{API_URL}/health")
prometheus_ready = safe_ready(f"{PROMETHEUS_URL}/-/ready")
grafana_health = safe_get_json(f"{GRAFANA_URL}/api/health")

c1, c2, c3, c4 = st.columns(4)

with c1:
    api_status = "healthy" if api_health and api_health.get("status") == "ok" else "unknown"
    st.metric("FastAPI", api_status)

with c2:
    db_status = "connected" if api_health and api_health.get("database") == "connected" else "unknown"
    st.metric("PostgreSQL", db_status)

with c3:
    st.metric("Prometheus", "ready" if prometheus_ready else "unknown")

with c4:
    grafana_status = grafana_health.get("database", "unknown") if grafana_health else "unknown"
    st.metric("Grafana", grafana_status)

section_title("End-to-end platform architecture")

architecture_overview()

st.markdown(
    """
    L'architecture relie les événements clients à des usages analytiques et IA :
    ingestion temps réel, stockage, entraînement ML, API serving, application Streamlit
    et supervision opérationnelle.
    """
)

section_title("Core services")

services = [
    {
        "Service": "PostgreSQL",
        "Role": "Base principale RetailFlow",
        "Port": "5432",
        "Evidence": "Schemas raw, core, analytics, governance",
    },
    {
        "Service": "Redpanda",
        "Role": "Streaming Kafka-compatible",
        "Port": "9092 / 9644",
        "Evidence": "Topic retailflow_events",
    },
    {
        "Service": "FastAPI",
        "Role": "API métier, IA, gouvernance, qualité et métriques",
        "Port": "8000",
        "Evidence": "/health, /metrics, /docs",
    },
    {
        "Service": "Streamlit",
        "Role": "Interface de démonstration et d'analyse",
        "Port": "8501",
        "Evidence": "Pages RetailFlow",
    },
    {
        "Service": "Airflow",
        "Role": "Orchestration batch et MLOps",
        "Port": "8080",
        "Evidence": "DAGs daily_data_quality, ml_retraining, retention_cleanup",
    },
    {
        "Service": "Prometheus",
        "Role": "Collecte métriques et règles d'alerte",
        "Port": "9090",
        "Evidence": "Targets FastAPI et PostgreSQL exporter",
    },
    {
        "Service": "Grafana",
        "Role": "Dashboards d'observabilité",
        "Port": "3000",
        "Evidence": "RetailFlow API Overview, RetailFlow Platform Overview",
    },
    {
        "Service": "postgres_exporter",
        "Role": "Métriques PostgreSQL pour Prometheus",
        "Port": "9187",
        "Evidence": "pg_up, pg_stat_activity_count, pg_database_size_bytes",
    },
]

st.dataframe(pd.DataFrame(services), use_container_width=True, hide_index=True)

section_title("Data zones and schemas")

zones = [
    {
        "Schema / Zone": "raw",
        "Purpose": "Stockage des événements bruts",
        "Examples": "raw.events",
    },
    {
        "Schema / Zone": "core",
        "Purpose": "Données métier structurées",
        "Examples": "core.customers, core.orders, core.products",
    },
    {
        "Schema / Zone": "analytics",
        "Purpose": "Features clients, prédictions et agrégats",
        "Examples": "analytics.customer_features, analytics.customer_predictions",
    },
    {
        "Schema / Zone": "governance",
        "Purpose": "Qualité, consentement, rétention et audit",
        "Examples": "governance.dead_letter_events, governance.retention_actions_log",
    },
    {
        "Schema / Zone": "ml/reports",
        "Purpose": "Rapports ML, drift, registry et retraining",
        "Examples": "model_summary.json, drift_report.json, retraining_runs.json",
    },
]

st.dataframe(pd.DataFrame(zones), use_container_width=True, hide_index=True)

section_title("Reliability and operations")

o1, o2, o3, o4 = st.columns(4)

with o1:
    proof_card(
        "Healthchecks",
        "Les services principaux exposent des indicateurs santé ou des healthchecks Docker pour vérifier leur disponibilité.",
    )

with o2:
    proof_card(
        "Backup / restore",
        "Des scripts de sauvegarde et de restauration PostgreSQL sont versionnés afin de sécuriser la reprise des données.",
    )

with o3:
    proof_card(
        "Readonly access",
        "Un rôle retailflow_readonly applique le principe du moindre privilège pour les accès en lecture.",
    )

with o4:
    proof_card(
        "Monitoring",
        "Prometheus et Grafana fournissent une supervision de la plateforme, des services et des métriques opérationnelles.",
    )

section_title("Architecture tools")

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

section_title("What this page demonstrates")

d1, d2, d3 = st.columns(3)

with d1:
    info_card(
        "Architecture cohérente",
        "Chaque service a un rôle clair dans le cycle de vie de la donnée.",
    )

with d2:
    info_card(
        "Déploiement effectif",
        "La stack est déployée localement via Docker Compose avec des services accessibles.",
    )

with d3:
    info_card(
        "Observabilité intégrée",
        "La supervision est intégrée à l'architecture et non ajoutée après coup.",
    )

academic_mapping(
    [
        {
            "Bloc": "Bloc 2",
            "Section": "Core services / Data zones",
            "Preuve": "Architecture de données complète, modulaire et documentée.",
        },
        {
            "Bloc": "Bloc 2",
            "Section": "Reliability and operations",
            "Preuve": "Healthchecks, backup/restore, readonly role et monitoring.",
        },
        {
            "Bloc": "Bloc 3",
            "Section": "End-to-end platform architecture",
            "Preuve": "Flux temps réel Redpanda → Consumer → PostgreSQL.",
        },
        {
            "Bloc": "Bloc 4",
            "Section": "FastAPI / ML / Monitoring",
            "Preuve": "Compatibilité entre la solution IA, l'API serving et l'infrastructure.",
        },
    ]
)

technical_evidence(
    {
        "Main files": [
            "`docker-compose.yml`",
            "`database/init/`",
            "`scripts/postgres_backup.sh`",
            "`scripts/postgres_restore.sh`",
            "`monitoring/prometheus/prometheus.yml`",
            "`monitoring/grafana/dashboards/`",
        ],
        "Runtime endpoints": [
            "`GET /health`",
            "`GET /metrics`",
            "`Prometheus /api/v1/targets`",
            "`Grafana /api/search`",
        ],
        "Tools": [
            "Docker Compose",
            "PostgreSQL",
            "FastAPI",
            "Streamlit",
            "Airflow",
            "Prometheus",
            "Grafana",
        ],
    }
)

footer_note()
