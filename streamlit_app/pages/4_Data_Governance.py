import os

import pandas as pd
import requests
import streamlit as st

from components import load_css, section_title, info_card, footer_note


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
st.markdown(
    """
    Cette page couvre le **Bloc 1 — Data Governance**.  
    Elle montre comment RetailFlow encadre l’usage, la conformité, la rétention,
    l’anonymisation et l’auditabilité des données clients.
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

    r1, r2, r3 = st.columns(3)

    with r1:
        info_card(
            "Data Owner",
            "Defines business ownership, data usage priorities and accountability for key data domains.",
        )

    with r2:
        info_card(
            "Data Steward",
            "Monitors quality, documentation, metadata and operational consistency of datasets.",
        )

    with r3:
        info_card(
            "DPO / Compliance",
            "Ensures GDPR alignment, consent management, retention policies and audit readiness.",
        )

    r4, r5, r6 = st.columns(3)

    with r4:
        info_card(
            "Data Engineer",
            "Implements reliable ingestion, transformation, orchestration and quality controls.",
        )

    with r5:
        info_card(
            "ML Engineer",
            "Maintains model lifecycle, retraining, serving, drift monitoring and explainability.",
        )

    with r6:
        info_card(
            "Business Owner",
            "Uses insights for retention, segmentation, customer value and decision-making.",
        )

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

        st.dataframe(df_consents, use_container_width=True, hide_index=True)
    else:
        st.info("No consent data available.")

    section_title("Retention policies")

    df_policies = pd.DataFrame(policies)

    if not df_policies.empty:
        st.dataframe(df_policies, use_container_width=True, hide_index=True)
    else:
        st.warning("No retention policies found.")

    section_title("Anonymization and audit trail")

    df_actions = pd.DataFrame(actions)

    if not df_actions.empty:
        st.dataframe(df_actions, use_container_width=True, hide_index=True)
    else:
        st.info("No retention actions logged yet.")

    section_title("Risk register")

    risk1, risk2 = st.columns(2)

    with risk1:
        info_card(
            "Personal data exposure",
            "Customer identity, contact details and behavioral data require retention limits, anonymization and access control.",
        )

    with risk2:
        info_card(
            "Data quality risk",
            "Invalid events or incomplete attributes can propagate to analytics and ML outputs if not detected early.",
        )

    risk3, risk4 = st.columns(2)

    with risk3:
        info_card(
            "ML drift risk",
            "Customer behavior may change over time, reducing model reliability without monitoring and retraining.",
        )

    with risk4:
        info_card(
            "Compliance risk",
            "Retention and consent policies must be auditable to support GDPR-aligned governance.",
        )

    section_title("GDPR alignment")

    st.markdown(
        """
        RetailFlow applique une logique de gouvernance inspirée du RGPD :

        - **Purpose limitation** : les données clients sont utilisées pour des cas d’usage définis.
        - **Consent management** : les consentements marketing, analytics et personalization sont suivis.
        - **Storage limitation** : les politiques de rétention définissent une durée et une action.
        - **Right to erasure / anonymization** : les clients peuvent être anonymisés selon les règles de rétention.
        - **Accountability** : les actions de rétention sont journalisées dans un audit trail.
        """
    )

    with st.expander("Technical evidence"):
        st.markdown(
            """
            Tables utilisées par cette page :

            - `core.customers`
            - `governance.data_retention_policies`
            - `governance.retention_actions_log`

            Endpoints FastAPI :

            - `/governance/summary`
            - `/governance/customer-consents`
            - `/governance/retention-policies`
            - `/governance/retention-actions`
            """
        )

except Exception as exc:
    st.error(f"Unable to load Data Governance data: {exc}")

footer_note()
