import pandas as pd
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
    Cette page sert de matrice finale de preuves pour la soutenance.
    Elle relie chaque critère important aux éléments concrets implémentés dans RetailFlow,
    avec les outils à ouvrir et les emplacements à montrer.
    """
)

section_title("Evidence overview")

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Covered blocks", 4)

with k2:
    st.metric("Main tools", "10+")

with k3:
    st.metric("Evidence pages", 10)

with k4:
    st.metric("Demo status", "Ready")

o1, o2, o3 = st.columns(3)

with o1:
    info_card(
        "Purpose",
        "Donner au jury une vue consolidée des preuves techniques, métier et académiques.",
    )

with o2:
    info_card(
        "Usage",
        "Utiliser cette page comme point d'entrée pour naviguer vers Streamlit, GitHub, Airflow, Grafana, Prometheus et pgAdmin.",
    )

with o3:
    info_card(
        "Positioning",
        "RetailFlow est présenté comme une plateforme démonstrative réaliste de retail intelligence.",
    )

section_title("Final evidence matrix")

evidence_rows = [
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Plan de gouvernance des données",
        "Preuve RetailFlow": "Cadre de gouvernance avec rôles, responsabilités, politiques de rétention, consentement et audit.",
        "Outils": "Streamlit, PostgreSQL, pgAdmin, VSCode",
        "Où chercher": "Streamlit > Data Governance ; VSCode > streamlit_app/pages/4_Data_Governance.py",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Parties prenantes et responsabilités",
        "Preuve RetailFlow": "Executive Sponsor, Governance Council, Data Owner, Data Steward, Data Custodian / IT, DPO, ML Engineer et Business Users.",
        "Outils": "Streamlit",
        "Où chercher": "Streamlit > Data Governance > Governance operating model",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Consentement et usages analytiques",
        "Preuve RetailFlow": "Suivi des consentements marketing, analytics et personalization ; filtre analytics consent dans Customer Intelligence.",
        "Outils": "Streamlit, FastAPI, PostgreSQL, pgAdmin",
        "Où chercher": "Streamlit > Data Governance > Consent management ; Streamlit > Customer Intelligence > Consent filter",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Rétention et anonymisation",
        "Preuve RetailFlow": "Politiques de rétention, actions d'anonymisation et journal d'audit.",
        "Outils": "Streamlit, PostgreSQL, pgAdmin, Airflow",
        "Où chercher": "Streamlit > Data Governance > Retention, anonymization and audit trail ; Airflow > retention_cleanup",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Gestion des violations et incidents",
        "Preuve RetailFlow": "Procédure breach response : detect, contain, assess, notify, correct, review.",
        "Outils": "Streamlit, VSCode",
        "Où chercher": "Streamlit > Data Governance > Breach response procedure",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Risques data et mitigation",
        "Preuve RetailFlow": "Registre de risques : exposition données personnelles, data quality, drift ML, accès non autorisé, incident opérationnel.",
        "Outils": "Streamlit",
        "Où chercher": "Streamlit > Data Governance > Data risk register",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 1",
        "Critère / sujet": "Accessibilité et inclusion",
        "Preuve RetailFlow": "Interface structurée, textes courts, sections lisibles, navigation par pages et détails en expanders.",
        "Outils": "Streamlit",
        "Où chercher": "Streamlit > Data Governance > Accessibility and inclusion",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Architecture data",
        "Preuve RetailFlow": "Architecture PostgreSQL, Redpanda, FastAPI, Streamlit, Airflow, Prometheus et Grafana.",
        "Outils": "Streamlit, Docker Compose, VSCode",
        "Où chercher": "Streamlit > Data Architecture ; VSCode > docker-compose.yml",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Structure des données",
        "Preuve RetailFlow": "Schémas core, raw, analytics et governance avec tables métiers, événements, prédictions et logs qualité.",
        "Outils": "PostgreSQL, pgAdmin, VSCode",
        "Où chercher": "pgAdmin > retailflow_db ; VSCode > database/init/",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Scalabilité et découplage",
        "Preuve RetailFlow": "Découplage producer / broker / consumer avec Redpanda et services Docker indépendants.",
        "Outils": "Docker Compose, Redpanda, FastAPI, Streamlit",
        "Où chercher": "VSCode > docker-compose.yml ; Streamlit > Customer View > Event pipeline path",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Disponibilité et exploitation",
        "Preuve RetailFlow": "Healthchecks Docker, documentation d'exploitation, backup/restore PostgreSQL et monitoring Prometheus.",
        "Outils": "Docker Compose, Prometheus, VSCode",
        "Où chercher": "VSCode > docker-compose.yml ; VSCode > docs/INFRA_OPERATIONS.md ; Prometheus > Targets",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Sécurité technique",
        "Preuve RetailFlow": "Rôle readonly PostgreSQL, séparation des services, variables d'environnement exemple et contrôles CI sécurité non bloquants.",
        "Outils": "PostgreSQL, GitHub Actions, VSCode",
        "Où chercher": "VSCode > database/init/ ; VSCode > .github/workflows/ ; GitHub > Actions",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 2",
        "Critère / sujet": "Observabilité infrastructure",
        "Preuve RetailFlow": "Targets Prometheus, dashboards Grafana, alert rules et liens directs depuis Streamlit.",
        "Outils": "Streamlit, Prometheus, Grafana",
        "Où chercher": "Streamlit > Observability ; Prometheus > Targets ; Grafana > Dashboards",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Pipeline temps réel",
        "Preuve RetailFlow": "Génération d'événements depuis Streamlit, publication FastAPI, topic Redpanda, consumer Python et stockage PostgreSQL.",
        "Outils": "Streamlit, FastAPI, Redpanda, PostgreSQL",
        "Où chercher": "Streamlit > Customer View > Generate full demo journey ; FastAPI Docs > /events",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Contrôle des erreurs pipeline",
        "Preuve RetailFlow": "Événements invalides isolés dans governance.dead_letter_events avec raison du rejet et payload brut.",
        "Outils": "Streamlit, PostgreSQL, pgAdmin",
        "Où chercher": "Streamlit > Customer View > Generate invalid event ; Streamlit > Data Quality > Latest dead-letter evidence",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Traçabilité des événements",
        "Preuve RetailFlow": "event_id, event_type, customer_id, session_id, timestamp, raw_payload et dead_letter_id.",
        "Outils": "PostgreSQL, pgAdmin, Streamlit",
        "Où chercher": "pgAdmin > raw.events ; pgAdmin > governance.dead_letter_events ; Streamlit > Data Quality",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Qualité des données",
        "Preuve RetailFlow": "Page Data Quality avec dead-letter, synthèse des anomalies, règles qualité et workflow de remédiation.",
        "Outils": "Streamlit, PostgreSQL, Airflow",
        "Où chercher": "Streamlit > Data Quality ; Airflow > daily_data_quality",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Automatisation pipeline",
        "Preuve RetailFlow": "DAGs Airflow pour agrégation ventes, qualité quotidienne, cleanup rétention et retraining ML.",
        "Outils": "Airflow, VSCode",
        "Où chercher": "Airflow > DAGs ; VSCode > airflow/dags/",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 3",
        "Critère / sujet": "Monitoring pipeline",
        "Preuve RetailFlow": "Alert rules Prometheus, dashboards Grafana, Data Quality page et logs consumer.",
        "Outils": "Prometheus, Grafana, Streamlit, Docker",
        "Où chercher": "Streamlit > Observability ; Prometheus > Alerts ; Grafana > RetailFlow dashboards",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Cas d'usage IA",
        "Preuve RetailFlow": "Churn prediction, CLV prediction et customer segmentation intégrés dans la plateforme.",
        "Outils": "Streamlit, FastAPI, Python ML",
        "Où chercher": "Streamlit > Customer Intelligence ; Streamlit > AI Monitoring",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Serving des prédictions",
        "Preuve RetailFlow": "Endpoints FastAPI IA utilisés par Streamlit pour afficher profils clients, churn, CLV et segments.",
        "Outils": "FastAPI, Streamlit",
        "Où chercher": "FastAPI Docs > /ai ; Streamlit > Customer Intelligence",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Explicabilité métier",
        "Preuve RetailFlow": "Decision framework et recommended actions traduisent les prédictions en décisions métier.",
        "Outils": "Streamlit",
        "Où chercher": "Streamlit > Customer Intelligence > Decision framework",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Model registry",
        "Preuve RetailFlow": "Registre de modèles avec artefacts et métadonnées utilisé dans AI Monitoring.",
        "Outils": "Streamlit, VSCode",
        "Où chercher": "Streamlit > AI Monitoring > Model registry ; VSCode > ml/model_registry.json",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Rapports ML",
        "Preuve RetailFlow": "Rapports churn, CLV, segmentation, model summary et drift report visibles depuis Streamlit.",
        "Outils": "Streamlit, VSCode",
        "Où chercher": "Streamlit > AI Monitoring > Model reports ; VSCode > ml/reports/",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Retraining",
        "Preuve RetailFlow": "DAG Airflow de retraining et journal retraining_runs.json.",
        "Outils": "Airflow, Streamlit, VSCode",
        "Où chercher": "Airflow > ml_retraining ; Streamlit > AI Monitoring > Training and retraining evidence",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "Robustesse et tests",
        "Preuve RetailFlow": "Tests unitaires, tests ML, tests de registry, compileall et CI GitHub Actions.",
        "Outils": "GitHub Actions, pytest, VSCode",
        "Où chercher": "GitHub > retailflow-platform > Actions ; VSCode > tests/ ; VSCode > ml/tests/",
        "Statut": "Implémenté",
    },
    {
        "Bloc": "Bloc 4",
        "Critère / sujet": "CI/CD et sécurité",
        "Preuve RetailFlow": "Workflow GitHub Actions avec tests, lint/checks, rapports sécurité non bloquants et documentation CI/CD.",
        "Outils": "GitHub Actions, VSCode",
        "Où chercher": "GitHub > Actions ; VSCode > .github/workflows/ ; VSCode > docs/CI_CD.md",
        "Statut": "Implémenté",
    },
]

df_evidence = pd.DataFrame(evidence_rows)

selected_blocs = st.multiselect(
    "Filter by bloc",
    sorted(df_evidence["Bloc"].unique().tolist()),
    default=sorted(df_evidence["Bloc"].unique().tolist()),
)

filtered_df = df_evidence[df_evidence["Bloc"].isin(selected_blocs)].copy()

st.dataframe(filtered_df, use_container_width=True, hide_index=True)

section_title("Evidence by block")

for bloc in ["Bloc 1", "Bloc 2", "Bloc 3", "Bloc 4"]:
    bloc_df = df_evidence[df_evidence["Bloc"] == bloc]

    with st.expander(f"{bloc} evidence summary", expanded=False):
        st.dataframe(bloc_df, use_container_width=True, hide_index=True)

section_title("Live demo path")

demo_path = [
    {
        "Step": 1,
        "Page / tool": "Streamlit > Platform Overview",
        "What to show": "Présenter RetailFlow, l'architecture et les liens outils.",
    },
    {
        "Step": 2,
        "Page / tool": "Streamlit > Customer View",
        "What to show": "Générer un parcours complet et un événement invalide.",
    },
    {
        "Step": 3,
        "Page / tool": "Streamlit > Data Quality",
        "What to show": "Montrer la dead-letter, error_reason, raw_payload et workflow de remédiation.",
    },
    {
        "Step": 4,
        "Page / tool": "Streamlit > Customer Intelligence",
        "What to show": "Sélectionner un client et expliquer les décisions IA.",
    },
    {
        "Step": 5,
        "Page / tool": "Streamlit > Data Governance",
        "What to show": "Montrer rôles, consentements, rétention, risques et breach response.",
    },
    {
        "Step": 6,
        "Page / tool": "Streamlit > AI Monitoring",
        "What to show": "Montrer registry, reports, retraining runs et drift.",
    },
    {
        "Step": 7,
        "Page / tool": "Streamlit > Observability",
        "What to show": "Montrer targets Prometheus, alert rules et dashboards Grafana.",
    },
    {
        "Step": 8,
        "Page / tool": "GitHub Actions",
        "What to show": "Montrer la CI verte et les workflows.",
    },
    {
        "Step": 9,
        "Page / tool": "Airflow",
        "What to show": "Montrer les DAGs opérationnels.",
    },
    {
        "Step": 10,
        "Page / tool": "pgAdmin",
        "What to show": "Montrer raw.events, governance.dead_letter_events et analytics.customer_predictions.",
    },
]

st.dataframe(pd.DataFrame(demo_path), use_container_width=True, hide_index=True)

section_title("Tool map")

tool_rows = [
    {
        "Tool": "Streamlit",
        "Role in demo": "Interface principale de démonstration métier et technique.",
        "Open": "http://localhost:8501",
    },
    {
        "Tool": "FastAPI",
        "Role in demo": "API de publication d'événements et serving IA.",
        "Open": "http://localhost:8000/docs",
    },
    {
        "Tool": "PostgreSQL / pgAdmin",
        "Role in demo": "Stockage des données, événements, prédictions, gouvernance et qualité.",
        "Open": "http://localhost:5050",
    },
    {
        "Tool": "Airflow",
        "Role in demo": "Automatisation qualité, agrégations, cleanup rétention et retraining.",
        "Open": "http://localhost:8080",
    },
    {
        "Tool": "Prometheus",
        "Role in demo": "Scraping, métriques, targets et alert rules.",
        "Open": "http://localhost:9090",
    },
    {
        "Tool": "Grafana",
        "Role in demo": "Dashboards d'exploitation API et plateforme.",
        "Open": "http://localhost:3000",
    },
    {
        "Tool": "GitHub Actions",
        "Role in demo": "CI/CD, tests, sécurité et validation continue.",
        "Open": "GitHub > retailflow-platform > Actions",
    },
    {
        "Tool": "VSCode / WSL",
        "Role in demo": "Code source, scripts, docs, configuration et preuves techniques.",
        "Open": "~/projects/Master_Thesis/retailflow-platform",
    },
]

st.dataframe(pd.DataFrame(tool_rows), use_container_width=True, hide_index=True)

section_title("Soutenance-ready proof cards")

p1, p2, p3, p4 = st.columns(4)

with p1:
    proof_card(
        "Bloc 1",
        "Gouvernance, consentement, rétention, risques, breach response et accessibilité.",
    )

with p2:
    proof_card(
        "Bloc 2",
        "Architecture data conteneurisée, PostgreSQL, Redpanda, services, sauvegarde et monitoring.",
    )

with p3:
    proof_card(
        "Bloc 3",
        "Pipeline événementiel, qualité, dead-letter, Airflow, monitoring et traçabilité.",
    )

with p4:
    proof_card(
        "Bloc 4",
        "Churn, CLV, segmentation, serving IA, registry, drift, retraining et CI/CD.",
    )

section_title("Academic mapping")

academic_mapping(
    [
        {
            "Bloc": "Bloc 1",
            "Section": "Final evidence matrix",
            "Preuve": "Matrice de preuves pour gouvernance, conformité, risques et responsabilités.",
        },
        {
            "Bloc": "Bloc 2",
            "Section": "Final evidence matrix",
            "Preuve": "Matrice de preuves pour architecture, sécurité, exploitation et observabilité.",
        },
        {
            "Bloc": "Bloc 3",
            "Section": "Final evidence matrix",
            "Preuve": "Matrice de preuves pour pipelines, qualité, automatisation et monitoring.",
        },
        {
            "Bloc": "Bloc 4",
            "Section": "Final evidence matrix",
            "Preuve": "Matrice de preuves pour IA, MLOps, serving, retraining, drift et CI/CD.",
        },
    ]
)

technical_evidence(
    {
        "Primary Streamlit pages": [
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
        "Core technical proof": [
            "`docker-compose.yml`",
            "`database/init/`",
            "`api/app/`",
            "`pipeline/consumer/`",
            "`airflow/dags/`",
            "`ml/src/`",
            "`ml/reports/`",
            "`monitoring/`",
            "`.github/workflows/`",
            "`docs/`",
        ],
        "Recommended demo order": [
            "Streamlit first",
            "Then Prometheus / Grafana",
            "Then Airflow",
            "Then pgAdmin",
            "Then GitHub Actions / VSCode proof",
        ],
    }
)

footer_note()
