import os

import pandas as pd
import requests
import streamlit as st

from components import load_css, section_title, info_card, footer_note


API_URL = os.getenv("API_URL", "http://fastapi:8000")

st.set_page_config(
    page_title="RetailFlow Data Quality",
    page_icon="✅",
    layout="wide",
)

load_css()


def api_get(path: str, params=None):
    response = requests.get(f"{API_URL}{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


st.title("✅ Data Quality")
st.markdown(
    """
    Cette page couvre le **Bloc 3 — Data Quality / Pipeline Quality**.  
    Elle montre comment RetailFlow détecte, isole et trace les erreurs dans les flux temps réel.
    """
)

try:
    dead_letters = api_get("/quality/dead-letters", params={"limit": 50})
    quality_summary = api_get("/quality/summary")
    dead_letter_summary = api_get("/quality/dead-letter-summary")

    df_dead = pd.DataFrame(dead_letters)
    df_quality = pd.DataFrame(quality_summary)
    df_summary = pd.DataFrame(dead_letter_summary)

    section_title("Pipeline quality overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Dead-letter events", len(df_dead))

    with c2:
        failed_rules = df_quality["rule_id"].nunique() if not df_quality.empty and "rule_id" in df_quality.columns else 0
        st.metric("Failed rules", failed_rules)

    with c3:
        high_severity = (
            len(df_dead[df_dead["severity"] == "high"])
            if not df_dead.empty and "severity" in df_dead.columns
            else 0
        )
        st.metric("High severity", high_severity)

    with c4:
        event_types = (
            df_dead["event_type"].nunique()
            if not df_dead.empty and "event_type" in df_dead.columns
            else 0
        )
        st.metric("Impacted event types", event_types)

    section_title("Quality control logic")

    q1, q2, q3 = st.columns(3)

    with q1:
        info_card(
            "Detect",
            "Incoming events are checked against data quality rules before being trusted by analytics and ML workflows.",
        )

    with q2:
        info_card(
            "Isolate",
            "Invalid events are redirected to a dead-letter mechanism instead of silently polluting analytical tables.",
        )

    with q3:
        info_card(
            "Trace",
            "Errors are stored with rule information, severity and payload context to support debugging and auditability.",
        )

    section_title("Dead-letter events")

    if not df_dead.empty:
        st.dataframe(df_dead, use_container_width=True, hide_index=True)

        if "severity" in df_dead.columns:
            st.subheader("Dead letters by severity")
            severity_counts = df_dead["severity"].value_counts().reset_index()
            severity_counts.columns = ["severity", "count"]
            st.bar_chart(severity_counts.set_index("severity")["count"])

        if "event_type" in df_dead.columns:
            st.subheader("Dead letters by event type")
            event_counts = df_dead["event_type"].value_counts().reset_index()
            event_counts.columns = ["event_type", "count"]
            st.bar_chart(event_counts.set_index("event_type")["count"])

    else:
        st.success("No dead-letter events found in the latest query.")

    section_title("Quality rules summary")

    if not df_quality.empty:
        st.dataframe(df_quality, use_container_width=True, hide_index=True)

        if "rule_name" in df_quality.columns and "checks_count" in df_quality.columns:
            st.subheader("Most triggered quality rules")
            chart_df = df_quality[["rule_name", "checks_count"]].copy()
            st.bar_chart(chart_df.set_index("rule_name")["checks_count"])
    else:
        st.info("No quality summary available.")

    section_title("Dead-letter summary")

    if not df_summary.empty:
        st.dataframe(df_summary, use_container_width=True, hide_index=True)
    else:
        st.info("No dead-letter summary available.")

    section_title("Streaming quality narrative")

    n1, n2, n3 = st.columns(3)

    with n1:
        info_card(
            "Real-time ingestion",
            "Events generated from the storefront are published to Redpanda and processed by the event consumer.",
        )

    with n2:
        info_card(
            "Validation layer",
            "The consumer validates event structure, mandatory fields and business consistency before storage.",
        )

    with n3:
        info_card(
            "Operational visibility",
            "Rejected events and rule failures are exposed in the UI to make pipeline quality observable.",
        )

    with st.expander("Technical evidence"):
        st.markdown(
            """
            Main concepts demonstrated:

            - real-time event ingestion ;
            - validation before persistence ;
            - dead-letter handling ;
            - quality rules monitoring ;
            - traceability for debugging and governance.

            FastAPI endpoints used:

            - `/quality/dead-letters`
            - `/quality/summary`
            - `/quality/dead-letter-summary`
            """
        )

except Exception as exc:
    st.error(f"Unable to load Data Quality data: {exc}")

footer_note()
