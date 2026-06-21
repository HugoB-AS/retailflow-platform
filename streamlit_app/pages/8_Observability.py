import os

import pandas as pd
import requests
import streamlit as st

from components import load_css, section_title, info_card, footer_note


API_URL = os.getenv("API_URL", "http://fastapi:8000")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://grafana:3000")
AIRFLOW_URL = os.getenv("AIRFLOW_URL", "http://airflow-webserver:8080")

st.set_page_config(
    page_title="RetailFlow Observability",
    page_icon="📡",
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


def prom_query(query: str):
    data = safe_get_json(f"{PROMETHEUS_URL}/api/v1/query", timeout=5)
    return data


def query_prometheus(expr: str):
    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": expr},
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def first_prom_value(expr: str):
    data = query_prometheus(expr)
    try:
        result = data["data"]["result"]
        if not result:
            return None
        return float(result[0]["value"][1])
    except Exception:
        return None


def status_text(value):
    if value == 1:
        return "UP"
    if value == 0:
        return "DOWN"
    return "UNKNOWN"


def status_metric(label: str, value):
    if value == 1:
        st.metric(label, "UP")
    elif value == 0:
        st.metric(label, "DOWN")
    else:
        st.metric(label, "UNKNOWN")


st.title("📡 Observability")
st.markdown(
    """
    Cette page couvre la supervision opérationnelle de RetailFlow.  
    Elle montre comment la plateforme est monitorée avec Prometheus, Grafana,
    PostgreSQL exporter, FastAPI metrics et les contrôles de santé Airflow.
    """
)

section_title("Platform health")

api_health = safe_get_json(f"{API_URL}/health")
grafana_health = safe_get_json(f"{GRAFANA_URL}/api/health")
airflow_health = safe_get_json(f"{AIRFLOW_URL}/health")

fastapi_up = first_prom_value('up{job="retailflow-fastapi"}')
postgres_up = first_prom_value('pg_up{job="retailflow-postgres"}')
api_requests_min = first_prom_value('sum(rate(http_requests_total[1m])) * 60')
postgres_connections = first_prom_value('sum(pg_stat_activity_count{job="retailflow-postgres"})')

h1, h2, h3, h4 = st.columns(4)

with h1:
    status_metric("FastAPI", fastapi_up)

with h2:
    status_metric("PostgreSQL", postgres_up)

with h3:
    airflow_status = None
    if airflow_health:
        airflow_status = airflow_health.get("scheduler", {}).get("status")
    st.metric("Airflow scheduler", airflow_status or "UNKNOWN")

with h4:
    grafana_status = None
    if grafana_health:
        grafana_status = grafana_health.get("database")
    st.metric("Grafana DB", grafana_status or "UNKNOWN")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("API requests/min", round(api_requests_min or 0, 2))

with m2:
    st.metric("PostgreSQL connections", int(postgres_connections or 0))

with m3:
    st.metric("Prometheus FastAPI", status_text(fastapi_up))

with m4:
    st.metric("Prometheus PostgreSQL", status_text(postgres_up))

section_title("Monitoring stack")

s1, s2, s3 = st.columns(3)

with s1:
    info_card(
        "Prometheus",
        "Collects FastAPI application metrics and PostgreSQL exporter metrics every 15 seconds.",
    )

with s2:
    info_card(
        "Grafana",
        "Visualizes API, database and platform metrics through provisioned dashboards.",
    )

with s3:
    info_card(
        "PostgreSQL exporter",
        "Exposes database health, connection and size metrics in Prometheus format.",
    )

section_title("Prometheus targets")

targets_data = safe_get_json(f"{PROMETHEUS_URL}/api/v1/targets")

if targets_data:
    active_targets = targets_data.get("data", {}).get("activeTargets", [])
    rows = []

    for target in active_targets:
        rows.append(
            {
                "job": target.get("labels", {}).get("job"),
                "instance": target.get("labels", {}).get("instance"),
                "health": target.get("health"),
                "last_scrape": target.get("lastScrape"),
                "scrape_duration": target.get("lastScrapeDuration"),
                "last_error": target.get("lastError"),
            }
        )

    df_targets = pd.DataFrame(rows)
    st.dataframe(df_targets, use_container_width=True, hide_index=True)
else:
    st.warning("Unable to load Prometheus targets.")

section_title("FastAPI observability")

api1, api2 = st.columns(2)

with api1:
    info_card(
        "Application health",
        f"FastAPI health endpoint reports: {api_health if api_health else 'unavailable'}",
    )

with api2:
    info_card(
        "Metrics endpoint",
        "FastAPI exposes Prometheus-compatible metrics through `/metrics`.",
    )

api_status = query_prometheus('sum by (status) (rate(http_requests_total[1m]))')
if api_status and api_status.get("data", {}).get("result"):
    status_rows = []
    for row in api_status["data"]["result"]:
        status_rows.append(
            {
                "status": row.get("metric", {}).get("status"),
                "requests_per_second": float(row.get("value", [0, 0])[1]),
            }
        )

    df_status = pd.DataFrame(status_rows)
    st.subheader("HTTP status codes")
    st.dataframe(df_status, use_container_width=True, hide_index=True)

section_title("PostgreSQL observability")

db_size = first_prom_value('pg_database_size_bytes{job="retailflow-postgres", datname="retailflow_db"}')

db1, db2, db3 = st.columns(3)

with db1:
    st.metric("pg_up", int(postgres_up or 0))

with db2:
    st.metric("Connections", int(postgres_connections or 0))

with db3:
    if db_size:
        st.metric("Database size", f"{db_size / (1024 * 1024):.2f} MB")
    else:
        st.metric("Database size", "N/A")

section_title("Airflow health")

if airflow_health:
    st.json(airflow_health)

    a1, a2, a3 = st.columns(3)

    with a1:
        info_card(
            "Metadatabase",
            airflow_health.get("metadatabase", {}).get("status", "unknown"),
        )

    with a2:
        info_card(
            "Scheduler",
            airflow_health.get("scheduler", {}).get("status", "unknown"),
        )

    with a3:
        info_card(
            "DAG processor",
            str(airflow_health.get("dag_processor", {}).get("status", "not enabled")),
        )
else:
    st.warning("Unable to load Airflow health endpoint.")

section_title("Grafana dashboards and tools")

g1, g2, g3, g4 = st.columns(4)

with g1:
    st.link_button("Open Grafana", "http://127.0.0.1:3000")

with g2:
    st.link_button("Open Prometheus", "http://127.0.0.1:9090")

with g3:
    st.link_button("Open Airflow", "http://127.0.0.1:8080")

with g4:
    st.link_button("Open FastAPI Docs", "http://127.0.0.1:8000/docs")

section_title("Alerting rules")

alerts = [
    {
        "alert": "FastAPI Down",
        "query": 'up{job="retailflow-fastapi"} == 0',
        "meaning": "The API is unreachable by Prometheus.",
    },
    {
        "alert": "PostgreSQL Down",
        "query": 'pg_up{job="retailflow-postgres"} == 0',
        "meaning": "The PostgreSQL exporter cannot reach the database.",
    },
    {
        "alert": "High API Error Rate",
        "query": 'sum(rate(http_requests_total{status=~"5.."}[1m])) > 0',
        "meaning": "The API is generating server-side errors.",
    },
    {
        "alert": "High API Latency",
        "query": "p95 latency > 1 second",
        "meaning": "The API becomes too slow for normal usage.",
    },
]

df_alerts = pd.DataFrame(alerts)
st.dataframe(df_alerts, use_container_width=True, hide_index=True)

section_title("What this page demonstrates")

d1, d2, d3 = st.columns(3)

with d1:
    info_card(
        "Production mindset",
        "The platform is not only functional; it is monitored and observable.",
    )

with d2:
    info_card(
        "Operational visibility",
        "API, database and orchestration components expose health signals.",
    )

with d3:
    info_card(
        "Architecture validation",
        "Prometheus and Grafana validate that the deployed architecture can be supervised.",
    )

with st.expander("Technical evidence"):
    st.markdown(
        """
        Main observability components:

        - FastAPI `/metrics`
        - FastAPI `/health`
        - PostgreSQL exporter `:9187/metrics`
        - Prometheus targets
        - Grafana dashboards
        - Airflow `/health`
        - Alerting rules documentation

        Main files:

        - `monitoring/prometheus/prometheus.yml`
        - `monitoring/grafana/dashboards/retailflow_api_overview.json`
        - `monitoring/grafana/dashboards/retailflow_platform_overview.json`
        - `monitoring/grafana/alerts/alert_rules.md`
        """
    )

footer_note()
