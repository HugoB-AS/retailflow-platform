import pandas as pd
import streamlit as st

from components import (
    load_css,
    section_title,
    block_badges,
    technical_evidence,
    footer_note,
)


st.set_page_config(
    page_title="RetailFlow Project Evidence",
    page_icon="📌",
    layout="wide",
)

load_css()

st.title("📌 Project Evidence")
block_badges(["Bloc 1", "Bloc 2", "Bloc 3", "Bloc 4"])

st.markdown(
    """
    Cette page sert de carte de navigation des preuves RetailFlow.
    Elle indique quel élément du projet répond à quel bloc, avec l'outil à utiliser
    et l'endroit où chercher pendant la démonstration.
    """
)

evidence_rows = [
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Data governance operating model",
        "Preuve RetailFlow": "Rôles Data Owner, Data Steward, DPO, Data Custodian, Governance Council",
        "Outils": "Streamlit, VSCode",
        "Où chercher": "Streamlit > Data Governance ; VSCode > streamlit_app/pages/4_Data_Governance.py",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Consentement et RGPD",
        "Preuve RetailFlow": "Consent tracking, retention policies, anonymization and audit trail",
        "Outils": "Streamlit, pgAdmin, PostgreSQL",
        "Où chercher": "Streamlit > Data Governance ; pgAdmin > retailflow_db > governance",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Data risk management",
        "Preuve RetailFlow": "Risk register, breach response procedure, compliance controls",
        "Outils": "Streamlit, VSCode",
        "Où chercher": "Streamlit > Data Governance ; VSCode > docs/retailflow_data_governance...",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Architecture globale",
        "Preuve RetailFlow": "Docker Compose architecture with PostgreSQL, Redpanda, FastAPI, Streamlit, Airflow, Prometheus and Grafana",
        "Outils": "Streamlit, VSCode, Docker Compose",
        "Où chercher": "Streamlit > Data Architecture ; VSCode > docker-compose.yml",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Modèle de données",
        "Preuve RetailFlow": "Schemas raw, core, analytics and governance",
        "Outils": "pgAdmin, PostgreSQL, VSCode",
        "Où chercher": "pgAdmin > retailflow_db ; VSCode > database/init/",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Monitoring et observabilité",
        "Preuve RetailFlow": "Prometheus targets, Grafana dashboards, postgres_exporter",
        "Outils": "Prometheus, Grafana, Streamlit",
        "Où chercher": "Prometheus > Status > Targets ; Grafana > RetailFlow dashboards ; Streamlit > Observability",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Exploitation infrastructure",
        "Preuve RetailFlow": "Healthchecks, backup/restore scripts, readonly role and infrastructure documentation",
        "Outils": "VSCode, Docker Compose, PostgreSQL",
        "Où chercher": "VSCode > docs/INFRA_OPERATIONS.md ; VSCode > scripts/",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Pipeline temps réel",
        "Preuve RetailFlow": "Customer events published to Redpanda, consumed by Python consumer and stored in PostgreSQL",
        "Outils": "Streamlit, Redpanda, PostgreSQL, VSCode",
        "Où chercher": "Streamlit > Customer View ; VSCode > pipeline/consumer/ ; pgAdmin > raw.events",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Data quality",
        "Preuve RetailFlow": "Validation rules, dead-letter events and quality summaries",
        "Outils": "Streamlit, PostgreSQL, pgAdmin",
        "Où chercher": "Streamlit > Data Quality ; pgAdmin > governance.dead_letter_events",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Automatisation",
        "Preuve RetailFlow": "Airflow DAGs for sales aggregation, data quality, retention and ML retraining",
        "Outils": "Airflow, VSCode",
        "Où chercher": "Airflow > DAGs ; VSCode > airflow/dags/",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Performance pipeline",
        "Preuve RetailFlow": "Producer metrics report with delivered events, failures, duration and events per second",
        "Outils": "VSCode, Streamlit",
        "Où chercher": "VSCode > pipeline/reports/pipeline_metrics.json",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "AI use cases",
        "Preuve RetailFlow": "Churn prediction, CLV prediction and customer segmentation",
        "Outils": "Streamlit, FastAPI, PostgreSQL",
        "Où chercher": "Streamlit > Customer Intelligence ; FastAPI > /docs > /ai/*",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Model performance",
        "Preuve RetailFlow": "ROC AUC, F1, MAE, RMSE, R², segmentation metrics and drift indicators",
        "Outils": "Streamlit, VSCode",
        "Où chercher": "Streamlit > AI Monitoring ; VSCode > ml/reports/",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Model registry",
        "Preuve RetailFlow": "Generated model registry with artifacts, metrics, features and model status",
        "Outils": "Streamlit, VSCode",
        "Où chercher": "Streamlit > AI Monitoring ; VSCode > ml/model_registry.json",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Retraining automation",
        "Preuve RetailFlow": "Airflow ml_retraining DAG and retraining run logs",
        "Outils": "Airflow, Streamlit, VSCode",
        "Où chercher": "Airflow > DAGs > ml_retraining ; VSCode > ml/reports/retraining_runs.json",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "API serving",
        "Preuve RetailFlow": "FastAPI exposes AI endpoints consumed by Streamlit",
        "Outils": "FastAPI, Streamlit",
        "Où chercher": "FastAPI > /docs > AI endpoints ; Streamlit > Customer Intelligence",
        "Statut": "Présent",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "CI/CD",
        "Preuve RetailFlow": "GitHub Actions tests, Docker validation, build validation and security reports",
        "Outils": "GitHub Actions, VSCode",
        "Où chercher": "GitHub > retailflow-platform > Actions ; VSCode > .github/workflows/ci.yml",
        "Statut": "Présent",
    },
]

df = pd.DataFrame(evidence_rows)

section_title("Evidence matrix")

b1, b2 = st.columns([1, 1])

with b1:
    selected_blocks = st.multiselect(
        "Filter by bloc",
        sorted(df["Bloc"].unique().tolist()),
        default=sorted(df["Bloc"].unique().tolist()),
    )

with b2:
    tool_values = sorted(
        {
            tool.strip()
            for tools in df["Outils"].tolist()
            for tool in tools.split(",")
        }
    )
    selected_tools = st.multiselect(
        "Filter by tool",
        tool_values,
        default=[],
        help="Optional filter. Leave empty to show all tools.",
    )

filtered = df[df["Bloc"].isin(selected_blocks)].copy()

if selected_tools:
    filtered = filtered[
        filtered["Outils"].apply(
            lambda value: any(tool in value for tool in selected_tools)
        )
    ]

st.dataframe(filtered, use_container_width=True, hide_index=True)

section_title("Coverage summary")

summary = (
    df.groupby("Bloc")
    .size()
    .reset_index(name="Evidence items")
    .sort_values("Bloc")
)

s1, s2, s3, s4 = st.columns(4)

for col, row in zip([s1, s2, s3, s4], summary.to_dict(orient="records")):
    with col:
        st.metric(row["Bloc"], row["Evidence items"])

section_title("How to use this page")

st.markdown(
    """
    Utilise cette page comme une carte de navigation pendant la démonstration.
    Elle ne remplace pas le PowerPoint : elle permet simplement de retrouver rapidement
    quelle preuve montrer dans quel outil.
    """
)

technical_evidence(
    {
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
        ],
        "Main external tools": [
            "GitHub Actions",
            "FastAPI",
            "Airflow",
            "pgAdmin",
            "PostgreSQL",
            "Prometheus",
            "Grafana",
            "VSCode",
        ],
        "Repository evidence": [
            "`docker-compose.yml`",
            "`.github/workflows/ci.yml`",
            "`database/init/`",
            "`pipeline/`",
            "`ml/`",
            "`monitoring/`",
            "`docs/`",
        ],
    }
)

footer_note()
