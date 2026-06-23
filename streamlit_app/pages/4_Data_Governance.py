import os

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
    page_title="RetailFlow Data Governance",
    page_icon="🛡️",
    layout="wide",
)

load_css()


def api_get(path: str, params=None):
    response = requests.get(f"{API_URL}{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("🛡️ Data Governance")
block_badges(["Bloc 1", "Bloc 2", "Bloc 3", "Bloc 4"])

st.markdown(
    """
    Cette page présente le cadre de gouvernance des données RetailFlow :
    rôles, consentements, rétention, anonymisation, risques, conformité,
    accessibilité et auditabilité.
    """
)

try:
    summary = api_get("/governance/summary")
    policies = api_get("/governance/retention-policies")
    actions = api_get("/governance/retention-actions", params={"limit": 50})
    consents = api_get("/governance/customer-consents", params={"limit": 50})

    consent = summary.get("consent", {}) or {}
    retention = summary.get("retention", {}) or {}
    action_summary = summary.get("actions", {}) or {}

    section_title("Governance overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Customers", consent.get("customers_count", 0))

    with c2:
        st.metric("Retention policies", retention.get("retention_policies_count", 0))

    with c3:
        st.metric("Anonymized customers", consent.get("anonymized_customers_count", 0))

    with c4:
        st.metric("Retention actions", action_summary.get("retention_actions_count", 0))

    section_title("Governance operating model")

    st.markdown(
        """
        Le modèle de gouvernance répartit les responsabilités entre les acteurs métier,
        techniques, conformité et décisionnels. Les rôles ne sont pas forcément des postes
        dédiés : ils peuvent être portés par des personnes existantes dans l'organisation.
        """
    )

    stakeholders = [
        {
            "Role": "Executive Sponsor",
            "Responsibility": "Porte la vision, arbitre les priorités et donne l'autorité au programme data.",
            "Main evidence": "Sponsor du cadre de gouvernance et des décisions de priorité.",
        },
        {
            "Role": "Governance Council",
            "Responsibility": "Réunit métier, IT, data, conformité et sécurité pour piloter les règles communes.",
            "Main evidence": "Instance de décision pour politiques, risques et arbitrages.",
        },
        {
            "Role": "Data Owner",
            "Responsibility": "Responsable métier d'un domaine de données et de ses usages.",
            "Main evidence": "Définit les règles d'usage et les priorités métier.",
        },
        {
            "Role": "Data Steward",
            "Responsibility": "Suit qualité, documentation, cohérence opérationnelle et règles de gestion.",
            "Main evidence": "Surveille qualité, metadata et anomalies.",
        },
        {
            "Role": "Data Custodian / IT",
            "Responsibility": "Gère l'infrastructure, les accès, les sauvegardes et la sécurité technique.",
            "Main evidence": "PostgreSQL, Docker Compose, backup/restore, readonly role.",
        },
        {
            "Role": "DPO / Compliance",
            "Responsibility": "Veille RGPD, consentement, rétention, anonymisation et conformité.",
            "Main evidence": "Consent tracking, retention policies, audit trail.",
        },
        {
            "Role": "ML Engineer",
            "Responsibility": "Maintient lifecycle ML, retraining, model registry, monitoring et drift.",
            "Main evidence": "AI Monitoring, retraining runs, drift report.",
        },
        {
            "Role": "Business Users",
            "Responsibility": "Utilisent les insights clients et remontent les besoins métier.",
            "Main evidence": "Customer Intelligence, segments, churn, CLV.",
        },
    ]

    st.dataframe(pd.DataFrame(stakeholders), use_container_width=True, hide_index=True)

    section_title("Consent management")

    df_consents = pd.DataFrame(consents)

    if not df_consents.empty:
        k1, k2, k3 = st.columns(3)

        customers_count = max(consent.get("customers_count", 1), 1)

        with k1:
            marketing_rate = consent.get("marketing_consent_count", 0) / customers_count
            st.metric("Marketing consent", f"{marketing_rate:.1%}")

        with k2:
            analytics_rate = consent.get("analytics_consent_count", 0) / customers_count
            st.metric("Analytics consent", f"{analytics_rate:.1%}")

        with k3:
            personalization_rate = consent.get("personalization_consent_count", 0) / customers_count
            st.metric("Personalization consent", f"{personalization_rate:.1%}")

        with st.expander("Customer consent sample"):
            st.dataframe(df_consents, use_container_width=True, hide_index=True)
    else:
        st.info("No consent data available.")

    section_title("Retention, anonymization and audit trail")

    r1, r2 = st.columns(2)

    with r1:
        st.subheader("Retention policies")
        df_policies = pd.DataFrame(policies)

        if not df_policies.empty:
            st.dataframe(df_policies, use_container_width=True, hide_index=True)
        else:
            st.warning("No retention policies found.")

    with r2:
        st.subheader("Anonymization and audit actions")
        df_actions = pd.DataFrame(actions)

        if not df_actions.empty:
            st.dataframe(df_actions, use_container_width=True, hide_index=True)
        else:
            st.info("No retention actions logged yet.")

    section_title("Regulatory alignment")

    g1, g2, g3, g4 = st.columns(4)

    with g1:
        proof_card(
            "RGPD",
            "Consentement, minimisation, rétention, anonymisation et auditabilité.",
        )

    with g2:
        proof_card(
            "ISO 27001 mindset",
            "Gestion des risques, accès, documentation, sauvegarde et contrôle opérationnel.",
        )

    with g3:
        proof_card(
            "Accessibility",
            "Interface structurée, navigation claire, textes explicatifs et information compréhensible.",
        )

    with g4:
        proof_card(
            "Accountability",
            "Les politiques et actions de gouvernance sont visibles et traçables.",
        )

    with st.expander("Compliance mechanisms"):
        st.markdown(
            """
            **Mécanismes de conformité utilisés dans RetailFlow :**

            - suivi des consentements marketing, analytics et personalization ;
            - limitation des usages analytiques via le consentement analytics ;
            - politiques de rétention versionnées dans la base ;
            - anonymisation des clients selon les règles de rétention ;
            - journalisation des actions de rétention ;
            - rôle readonly pour l'accès en lecture ;
            - documentation d'exploitation et monitoring ;
            - rapports qualité et dead-letter events pour l'audit pipeline.
            """
        )

    section_title("Breach response procedure")

    breach_steps = [
        {
            "Step": 1,
            "Phase": "Detect",
            "Action": "Identifier l'incident via logs, monitoring, data quality, alertes ou signalement utilisateur.",
            "Owner": "Data Custodian / IT",
        },
        {
            "Step": 2,
            "Phase": "Contain",
            "Action": "Limiter l'impact : couper l'accès concerné, isoler le flux ou bloquer le traitement fautif.",
            "Owner": "IT / Data Engineer",
        },
        {
            "Step": 3,
            "Phase": "Assess",
            "Action": "Évaluer les données concernées, les personnes impactées, la gravité et le risque.",
            "Owner": "DPO / Compliance",
        },
        {
            "Step": 4,
            "Phase": "Notify",
            "Action": "Préparer la notification aux autorités ou personnes concernées si nécessaire.",
            "Owner": "DPO / Executive Sponsor",
        },
        {
            "Step": 5,
            "Phase": "Correct",
            "Action": "Appliquer les mesures correctives : patch, changement de règle, purge, anonymisation ou rollback.",
            "Owner": "Data Custodian / Data Engineer",
        },
        {
            "Step": 6,
            "Phase": "Review",
            "Action": "Documenter l'incident, mettre à jour les politiques et intégrer les enseignements.",
            "Owner": "Governance Council",
        },
    ]

    st.dataframe(pd.DataFrame(breach_steps), use_container_width=True, hide_index=True)

    section_title("Data risk register")

    risks = [
        {
            "Risk": "Personal data exposure",
            "Impact": "Atteinte à la confidentialité ou non-conformité RGPD.",
            "Mitigation": "Consentement, rétention, anonymisation, readonly role et audit trail.",
            "Owner": "DPO / Data Custodian",
        },
        {
            "Risk": "Data quality issue",
            "Impact": "Données invalides utilisées dans analytics ou ML.",
            "Mitigation": "Validation events, dead-letter events, quality logs et Data Quality page.",
            "Owner": "Data Steward / Data Engineer",
        },
        {
            "Risk": "ML drift",
            "Impact": "Baisse de fiabilité des prédictions clients.",
            "Mitigation": "Drift report, retraining Airflow, model registry et AI Monitoring.",
            "Owner": "ML Engineer",
        },
        {
            "Risk": "Unauthorized access",
            "Impact": "Accès excessif ou non justifié aux données clients.",
            "Mitigation": "Principe du moindre privilège, rôle readonly, séparation des responsabilités.",
            "Owner": "Data Custodian / IT",
        },
        {
            "Risk": "Operational failure",
            "Impact": "Interruption de service ou perte de visibilité.",
            "Mitigation": "Healthchecks, backup/restore, Prometheus, Grafana et documentation operations.",
            "Owner": "IT / Data Engineer",
        },
        {
            "Risk": "Regulatory change",
            "Impact": "Décalage entre politiques internes et obligations réglementaires.",
            "Mitigation": "Revue périodique par DPO, Governance Council et mise à jour documentaire.",
            "Owner": "DPO / Governance Council",
        },
    ]

    st.dataframe(pd.DataFrame(risks), use_container_width=True, hide_index=True)

    section_title("Accessibility and inclusion")

    a1, a2, a3 = st.columns(3)

    with a1:
        info_card(
            "Clarté de l'information",
            "Les pages utilisent des titres structurés, métriques lisibles et explications courtes.",
        )

    with a2:
        info_card(
            "Navigation compréhensible",
            "Les pages sont organisées par thème et les preuves détaillées sont placées en expanders.",
        )

    with a3:
        info_card(
            "Langage accessible",
            "Les termes techniques sont accompagnés d'une interprétation métier lorsque nécessaire.",
        )

    section_title("Governance lifecycle")

    lifecycle = [
        {
            "Activity": "Define",
            "Description": "Définir politiques, rôles, règles d'usage et risques.",
        },
        {
            "Activity": "Implement",
            "Description": "Implémenter consentement, rétention, qualité, monitoring et accès.",
        },
        {
            "Activity": "Monitor",
            "Description": "Suivre métriques, erreurs, actions de rétention, drift et qualité.",
        },
        {
            "Activity": "Audit",
            "Description": "Contrôler traces, logs, rapports, règles et documentation.",
        },
        {
            "Activity": "Improve",
            "Description": "Mettre à jour les politiques selon incidents, risques et évolutions réglementaires.",
        },
    ]

    st.dataframe(pd.DataFrame(lifecycle), use_container_width=True, hide_index=True)

    section_title("What this page demonstrates")

    d1, d2, d3 = st.columns(3)

    with d1:
        info_card(
            "Governance structure",
            "Les responsabilités data sont distribuées entre métier, IT, conformité, ML et direction.",
        )

    with d2:
        info_card(
            "Regulatory control",
            "Consentement, rétention, anonymisation et audit trail soutiennent une logique RGPD.",
        )

    with d3:
        info_card(
            "Risk management",
            "Les risques data sont identifiés avec propriétaires, impacts et mesures de mitigation.",
        )

    academic_mapping(
        [
            {
                "Bloc": "Bloc 1",
                "Section": "Governance operating model",
                "Preuve": "Identification des parties prenantes et définition des rôles.",
            },
            {
                "Bloc": "Bloc 1",
                "Section": "Regulatory alignment",
                "Preuve": "RGPD, accessibilité, accountability et mécanismes de conformité.",
            },
            {
                "Bloc": "Bloc 1",
                "Section": "Breach response procedure",
                "Preuve": "Procédure de gestion des violations et mesures correctives.",
            },
            {
                "Bloc": "Bloc 1",
                "Section": "Data risk register",
                "Preuve": "Risques data identifiés avec stratégie de mitigation.",
            },
            {
                "Bloc": "Bloc 2",
                "Section": "Data Custodian / IT",
                "Preuve": "Lien avec architecture, accès, sauvegarde et exploitation.",
            },
            {
                "Bloc": "Bloc 3",
                "Section": "Data quality risk",
                "Preuve": "Lien entre gouvernance, qualité des pipelines et dead-letter events.",
            },
            {
                "Bloc": "Bloc 4",
                "Section": "ML drift risk",
                "Preuve": "Lien entre gouvernance, monitoring ML et retraining.",
            },
        ]
    )

    technical_evidence(
        {
            "FastAPI endpoints": [
                "`GET /governance/summary`",
                "`GET /governance/customer-consents`",
                "`GET /governance/retention-policies`",
                "`GET /governance/retention-actions`",
            ],
            "Database tables": [
                "`core.customers`",
                "`governance.data_retention_policies`",
                "`governance.retention_actions_log`",
                "`governance.dead_letter_events`",
                "`governance.data_quality_logs`",
            ],
            "Related files": [
                "`streamlit_app/pages/4_Data_Governance.py`",
                "`api/app/routes/governance.py`",
                "`database/init/`",
                "`docs/INFRA_OPERATIONS.md`",
            ],
            "Tools": [
                "Streamlit",
                "FastAPI",
                "PostgreSQL",
                "pgAdmin",
                "VSCode",
            ],
        }
    )

except Exception as exc:
    st.error(f"Unable to load Data Governance data: {exc}")

footer_note()
