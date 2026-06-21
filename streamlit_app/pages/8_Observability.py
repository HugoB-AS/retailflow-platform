import os
from datetime import datetime

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


PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://grafana:3000")

PROMETHEUS_PUBLIC_URL = os.getenv("PROMETHEUS_PUBLIC_URL", "http://localhost:9090")
GRAFANA_PUBLIC_URL = os.getenv("GRAFANA_PUBLIC_URL", "http://localhost:3000")

GRAFANA_USER = os.getenv("GRAFANA_USER", "admin")
GRAFANA_PASSWORD = os.getenv("GRAFANA_PASSWORD", "admin")

st.set_page_config(
    page_title="RetailFlow Observability",
    page_icon="📡",
    layout="wide",
)

load_css()


def safe_get_json(url: str, params=None, auth=None, timeout: int = 10):
    try:
        response = requests.get(url, params=params, auth=auth, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        return {"error": str(exc)}


def safe_http_ok(url: str, timeout: int = 10) -> bool:
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False


def target_status_from_keywords(targets_df: pd.DataFrame, keywords: list[str]) -> str:
    if targets_df.empty:
        return "N/A"

    for _, row in targets_df.iterrows():
        row_text = " ".join(str(value).lower() for value in row.to_dict().values())

        if all(keyword.lower() in row_text for keyword in keywords):
            health = str(row.get("health", "")).lower()

            if health == "up":
                return "OK"

            if health == "down":
                return "Attention"

            return health or "N/A"

    return "N/A"


def prometheus_query(query: str):
    payload = safe_get_json(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": query},
    )

    if payload.get("status") != "success":
        return None

    result = payload.get("data", {}).get("result", [])

    if not result:
        return None

    try:
        return float(result[0]["value"][1])
    except Exception:
        return None


def get_prometheus_targets() -> pd.DataFrame:
    payload = safe_get_json(f"{PROMETHEUS_URL}/api/v1/targets")

    if payload.get("status") != "success":
        return pd.DataFrame()

    targets = payload.get("data", {}).get("activeTargets", [])

    rows = []

    for target in targets:
        labels = target.get("labels", {}) or {}
        discovered = target.get("discoveredLabels", {}) or {}

        rows.append(
            {
                "job": labels.get("job") or discovered.get("__meta_docker_container_label_com_docker_compose_service"),
                "instance": labels.get("instance"),
                "health": target.get("health"),
                "scrape_url": target.get("scrapeUrl"),
                "last_scrape": target.get("lastScrape"),
                "last_error": target.get("lastError"),
            }
        )

    return pd.DataFrame(rows)


def get_prometheus_rules() -> pd.DataFrame:
    payload = safe_get_json(f"{PROMETHEUS_URL}/api/v1/rules")

    if payload.get("status") != "success":
        return pd.DataFrame()

    groups = payload.get("data", {}).get("groups", [])

    rows = []

    for group in groups:
        group_name = group.get("name")

        for rule in group.get("rules", []):
            if rule.get("type") != "alerting":
                continue

            labels = rule.get("labels", {}) or {}
            annotations = rule.get("annotations", {}) or {}

            rows.append(
                {
                    "group": group_name,
                    "alert": rule.get("name"),
                    "state": rule.get("state"),
                    "severity": labels.get("severity"),
                    "summary": annotations.get("summary"),
                    "duration": rule.get("duration"),
                    "query": rule.get("query"),
                }
            )

    return pd.DataFrame(rows)


def get_prometheus_alerts() -> pd.DataFrame:
    payload = safe_get_json(f"{PROMETHEUS_URL}/api/v1/alerts")

    if payload.get("status") != "success":
        return pd.DataFrame()

    alerts = payload.get("data", {}).get("alerts", [])

    rows = []

    for alert in alerts:
        labels = alert.get("labels", {}) or {}
        annotations = alert.get("annotations", {}) or {}

        rows.append(
            {
                "alert": labels.get("alertname"),
                "state": alert.get("state"),
                "severity": labels.get("severity"),
                "instance": labels.get("instance"),
                "job": labels.get("job"),
                "summary": annotations.get("summary"),
                "active_at": alert.get("activeAt"),
            }
        )

    return pd.DataFrame(rows)


def get_grafana_health() -> dict:
    return safe_get_json(
        f"{GRAFANA_URL}/api/health",
        auth=(GRAFANA_USER, GRAFANA_PASSWORD),
    )


def get_grafana_dashboards() -> pd.DataFrame:
    payload = safe_get_json(
        f"{GRAFANA_URL}/api/search",
        params={"type": "dash-db"},
        auth=(GRAFANA_USER, GRAFANA_PASSWORD),
    )

    if isinstance(payload, dict) and payload.get("error"):
        return pd.DataFrame()

    if not isinstance(payload, list):
        return pd.DataFrame()

    rows = []

    for dashboard in payload:
        uid = dashboard.get("uid")
        uri = dashboard.get("uri")
        title = dashboard.get("title")

        if uid:
            public_url = f"{GRAFANA_PUBLIC_URL}/d/{uid}"
        elif uri:
            public_url = f"{GRAFANA_PUBLIC_URL}/{uri}"
        else:
            public_url = GRAFANA_PUBLIC_URL

        rows.append(
            {
                "title": title,
                "type": dashboard.get("type"),
                "folder": dashboard.get("folderTitle"),
                "uid": uid,
                "url": public_url,
            }
        )

    return pd.DataFrame(rows)


def status_label(value) -> str:
    if value in [1, 1.0, True, "ok", "healthy", "success", "up", "OK"]:
        return "OK"

    if value in [0, 0.0, False, "error", "unhealthy", "down", "Attention"]:
        return "Attention"

    if value is None:
        return "N/A"

    return str(value)


def format_metric(value, suffix: str = "") -> str:
    if value is None:
        return "N/A"

    try:
        if float(value).is_integer():
            return f"{int(value)}{suffix}"
        return f"{float(value):.2f}{suffix}"
    except Exception:
        return f"{value}{suffix}"


st.title("📡 Observability")
block_badges(["Bloc 2", "Bloc 3", "Bloc 4"])

st.markdown(
    """
    Cette page présente l'observabilité de RetailFlow :
    disponibilité des services, scraping Prometheus, règles d'alerte,
    dashboards Grafana et preuves opérationnelles pour le pilotage de la plateforme.
    """
)

section_title("Monitoring access")

l1, l2, l3 = st.columns(3)

with l1:
    st.link_button("Open Prometheus", PROMETHEUS_PUBLIC_URL)

with l2:
    st.link_button("Open Grafana", GRAFANA_PUBLIC_URL)

with l3:
    st.link_button("Open FastAPI Docs", "http://localhost:8000/docs")

section_title("Platform health overview")

prometheus_ok = safe_http_ok(f"{PROMETHEUS_URL}/-/healthy")
grafana_health = get_grafana_health()

targets_df = get_prometheus_targets()
rules_df = get_prometheus_rules()
alerts_df = get_prometheus_alerts()
dashboards_df = get_grafana_dashboards()

targets_up = 0
targets_total = 0

if not targets_df.empty and "health" in targets_df.columns:
    targets_total = len(targets_df)
    targets_up = int(targets_df["health"].astype(str).str.lower().eq("up").sum())

active_alerts = 0

if not alerts_df.empty and "state" in alerts_df.columns:
    active_alerts = int(alerts_df["state"].astype(str).str.lower().eq("firing").sum())

rules_count = len(rules_df) if not rules_df.empty else 0
dashboards_count = len(dashboards_df) if not dashboards_df.empty else 0

k1, k2, k3, k4 = st.columns(4)

with k1:
    prometheus_status = "OK" if prometheus_ok else "Attention"
    st.metric("Prometheus", prometheus_status)

with k2:
    grafana_status = grafana_health.get("database", "unknown") if isinstance(grafana_health, dict) else "unknown"
    st.metric("Grafana DB", status_label(grafana_status))

with k3:
    st.metric("Targets up", f"{targets_up}/{targets_total}")

with k4:
    st.metric("Active alerts", active_alerts)

section_title("Core service metrics")

fastapi_up = target_status_from_keywords(targets_df, ["fastapi"])
postgres_exporter_up = target_status_from_keywords(targets_df, ["postgres"])
prometheus_targets_up = prometheus_query("sum(up)")
http_requests = prometheus_query("sum(rate(http_requests_total[5m]))")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("FastAPI target", status_label(fastapi_up))

with m2:
    st.metric("PostgreSQL exporter", status_label(postgres_exporter_up))

with m3:
    st.metric("Total targets up", format_metric(prometheus_targets_up))

with m4:
    st.metric("HTTP req/s", format_metric(http_requests))

section_title("Prometheus targets")

if not targets_df.empty:
    display_cols = [
        "job",
        "instance",
        "health",
        "last_scrape",
        "last_error",
    ]

    available_cols = [col for col in display_cols if col in targets_df.columns]

    st.dataframe(
        targets_df[available_cols],
        use_container_width=True,
        hide_index=True,
    )

    if "health" in targets_df.columns:
        st.bar_chart(targets_df["health"].value_counts())
else:
    st.warning("No Prometheus target data available.")

section_title("Prometheus alert rules")

if not rules_df.empty:
    rule_cols = [
        "group",
        "alert",
        "state",
        "severity",
        "summary",
        "duration",
    ]

    available_rule_cols = [col for col in rule_cols if col in rules_df.columns]

    st.dataframe(
        rules_df[available_rule_cols],
        use_container_width=True,
        hide_index=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        if "state" in rules_df.columns:
            st.subheader("Rules by state")
            st.bar_chart(rules_df["state"].value_counts())

    with c2:
        if "severity" in rules_df.columns:
            st.subheader("Rules by severity")
            st.bar_chart(rules_df["severity"].fillna("unknown").value_counts())

    with st.expander("Alert rule queries"):
        st.dataframe(
            rules_df[["alert", "query"]] if "query" in rules_df.columns else rules_df,
            use_container_width=True,
            hide_index=True,
        )
else:
    st.warning("No Prometheus alert rules found.")

section_title("Active alerts")

if not alerts_df.empty:
    st.dataframe(alerts_df, use_container_width=True, hide_index=True)

    if "state" in alerts_df.columns:
        st.bar_chart(alerts_df["state"].value_counts())
else:
    st.success("No active Prometheus alert currently firing.")

section_title("Grafana dashboards")

if not dashboards_df.empty:
    display_cols = ["title", "folder", "uid", "url"]
    available_cols = [col for col in display_cols if col in dashboards_df.columns]

    st.dataframe(
        dashboards_df[available_cols],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("**Direct dashboard access**")

    dashboard_columns = st.columns(min(len(dashboards_df), 3))

    for index, (_, row) in enumerate(dashboards_df.head(3).iterrows()):
        with dashboard_columns[index % len(dashboard_columns)]:
            st.link_button(row.get("title", "Open dashboard"), row.get("url", GRAFANA_PUBLIC_URL))
else:
    st.warning("No Grafana dashboard found through the API.")

section_title("Observability coverage")

coverage = [
    {
        "Layer": "Application",
        "Observed component": "FastAPI",
        "Evidence": "Prometheus target, HTTP metrics, Grafana API dashboard.",
    },
    {
        "Layer": "Database",
        "Observed component": "PostgreSQL",
        "Evidence": "postgres_exporter target, platform dashboard and DB metrics.",
    },
    {
        "Layer": "Pipeline",
        "Observed component": "Event consumer and data quality",
        "Evidence": "Dead-letter events, quality page, logs and alerting principles.",
    },
    {
        "Layer": "ML",
        "Observed component": "Model reports and drift",
        "Evidence": "AI Monitoring page, model registry, drift report and retraining runs.",
    },
    {
        "Layer": "Infrastructure",
        "Observed component": "Docker Compose services",
        "Evidence": "Healthchecks, Prometheus targets and Grafana dashboards.",
    },
]

st.dataframe(pd.DataFrame(coverage), use_container_width=True, hide_index=True)

section_title("Operational response model")

response_model = [
    {
        "Signal": "Service down",
        "Detection": "Prometheus target down alert.",
        "Response": "Check Docker service, logs, healthcheck and restart if needed.",
        "Tool": "Prometheus / Docker / Grafana",
    },
    {
        "Signal": "High API latency",
        "Detection": "Prometheus latency rule.",
        "Response": "Inspect API load, database queries and recent pipeline activity.",
        "Tool": "Prometheus / Grafana / FastAPI logs",
    },
    {
        "Signal": "High API error rate",
        "Detection": "Prometheus 5xx alert.",
        "Response": "Inspect API logs, failing endpoint and recent code changes.",
        "Tool": "Grafana / Docker logs / GitHub Actions",
    },
    {
        "Signal": "Pipeline data quality issue",
        "Detection": "Dead-letter events and quality monitoring.",
        "Response": "Classify error reason, correct rule or source and reprocess if appropriate.",
        "Tool": "Streamlit / PostgreSQL / pgAdmin",
    },
    {
        "Signal": "Model drift",
        "Detection": "Drift report and AI Monitoring.",
        "Response": "Review features, retrain model and update registry.",
        "Tool": "Airflow / ML reports / GitHub Actions",
    },
]

st.dataframe(pd.DataFrame(response_model), use_container_width=True, hide_index=True)

section_title("What this page demonstrates")

d1, d2, d3 = st.columns(3)

with d1:
    info_card(
        "Availability",
        "Les services principaux sont supervisés via Prometheus targets et healthchecks.",
    )

with d2:
    info_card(
        "Alerting",
        "Les règles Prometheus rendent les incidents détectables et actionnables.",
    )

with d3:
    info_card(
        "Dashboards",
        "Grafana expose une vision opérationnelle pour API, base de données et plateforme.",
    )

academic_mapping(
    [
        {
            "Bloc": "Bloc 2",
            "Section": "Platform health overview",
            "Preuve": "Supervision de disponibilité, healthchecks et targets Prometheus.",
        },
        {
            "Bloc": "Bloc 2",
            "Section": "Grafana dashboards",
            "Preuve": "Dashboards d'exploitation pour piloter la plateforme.",
        },
        {
            "Bloc": "Bloc 3",
            "Section": "Prometheus alert rules",
            "Preuve": "Alertes opérationnelles pour fiabilité des pipelines et services.",
        },
        {
            "Bloc": "Bloc 3",
            "Section": "Operational response model",
            "Preuve": "Réponse structurée aux incidents pipeline et qualité.",
        },
        {
            "Bloc": "Bloc 4",
            "Section": "Observability coverage",
            "Preuve": "Lien avec drift, retraining et monitoring des modèles.",
        },
    ]
)

technical_evidence(
    {
        "Prometheus endpoints": [
            "`GET /api/v1/targets`",
            "`GET /api/v1/rules`",
            "`GET /api/v1/alerts`",
            "`GET /api/v1/query`",
        ],
        "Grafana endpoints": [
            "`GET /api/health`",
            "`GET /api/search?type=dash-db`",
        ],
        "Monitoring files": [
            "`monitoring/prometheus/prometheus.yml`",
            "`monitoring/prometheus/rules/retailflow_alerts.yml`",
            "`monitoring/grafana/provisioning/`",
            "`monitoring/grafana/dashboards/`",
        ],
        "Related documentation": [
            "`docs/MONITORING.md`",
            "`docs/MONITORING_EVIDENCE.md`",
            "`docs/INFRA_OPERATIONS.md`",
        ],
        "Tools": [
            "Prometheus",
            "Grafana",
            "Docker Compose",
            "FastAPI",
            "PostgreSQL exporter",
            "Streamlit",
        ],
        "Page generated at": [
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        ],
    }
)

footer_note()
