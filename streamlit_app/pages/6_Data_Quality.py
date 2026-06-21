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
    page_title="RetailFlow Data Quality",
    page_icon="✅",
    layout="wide",
)

load_css()


def api_get(path: str, params=None):
    response = requests.get(f"{API_URL}{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def safe_api_get(path: str, params=None, default=None):
    try:
        return api_get(path, params=params)
    except Exception:
        return default if default is not None else []


def normalize_records(payload):
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ["items", "events", "data", "results"]:
            if isinstance(payload.get(key), list):
                return payload[key]

    return []


def first_existing_column(df: pd.DataFrame, candidates: list[str]):
    for column in candidates:
        if column in df.columns:
            return column
    return None


st.title("✅ Data Quality")
block_badges(["Bloc 1", "Bloc 3"])

st.markdown(
    """
    Cette page démontre comment RetailFlow contrôle la qualité des données dans la pipeline.
    Les événements valides alimentent les usages analytiques, tandis que les événements invalides
    sont isolés dans une table de dead-letter pour audit, correction ou reprocessing.
    """
)

try:
    dead_letters = normalize_records(
        api_get("/quality/dead-letters", params={"limit": 100})
    )
    quality_summary = normalize_records(api_get("/quality/summary"))
    dead_letter_summary = normalize_records(api_get("/quality/dead-letter-summary"))

    recent_events_payload = safe_api_get(
        "/events/recent",
        params={"limit": 20},
        default=[],
    )
    recent_events = normalize_records(recent_events_payload)

    df_dead = pd.DataFrame(dead_letters)
    df_quality = pd.DataFrame(quality_summary)
    df_summary = pd.DataFrame(dead_letter_summary)
    df_recent = pd.DataFrame(recent_events)

    section_title("Pipeline quality overview")

    dead_letter_count = len(df_dead)

    high_severity_count = 0
    if not df_dead.empty and "severity" in df_dead.columns:
        high_severity_count = int(
            df_dead["severity"].astype(str).str.lower().eq("high").sum()
        )

    reprocessed_count = 0
    if not df_dead.empty and "reprocessed" in df_dead.columns:
        reprocessed_count = int(df_dead["reprocessed"].fillna(False).astype(bool).sum())

    quality_rules_count = 0
    if not df_quality.empty:
        rule_col = first_existing_column(df_quality, ["rule_id", "rule_name"])
        quality_rules_count = int(df_quality[rule_col].nunique()) if rule_col else len(df_quality)

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Dead-letter events", dead_letter_count)

    with k2:
        st.metric("High severity issues", high_severity_count)

    with k3:
        st.metric("Reprocessed events", reprocessed_count)

    with k4:
        st.metric("Quality rules", quality_rules_count)

    section_title("Quality control flow")

    f1, f2, f3 = st.columns(3)

    with f1:
        proof_card(
            "1. Valid event",
            "L'événement respecte les règles de schéma, de référentiel et de typologie.",
        )

    with f2:
        proof_card(
            "2. Invalid event",
            "L'événement est rejeté si le type, le produit, la structure ou la donnée métier est invalide.",
        )

    with f3:
        proof_card(
            "3. Quality log",
            "L'anomalie est stockée dans `governance.dead_letter_events` pour audit et reprocessing.",
        )

    st.markdown(
        """
        Exemple : depuis **Customer View**, un événement
        `invalid_demo_event` est publié dans Redpanda, puis rejeté par le consumer
        et enregistré dans la dead-letter table.
        """
    )

    section_title("Latest dead-letter evidence")

    if df_dead.empty:
        st.info("No dead-letter event available yet. Generate an invalid event from the Customer View page.")
    else:
        created_col = first_existing_column(df_dead, ["created_at", "event_timestamp", "timestamp"])

        if created_col:
            df_dead_display = df_dead.sort_values(created_col, ascending=False).copy()
        else:
            df_dead_display = df_dead.copy()

        preferred_columns = [
            "dead_letter_id",
            "event_id",
            "source_topic",
            "event_type",
            "severity",
            "error_reason",
            "created_at",
            "reprocessed",
        ]

        available_columns = [
            column for column in preferred_columns if column in df_dead_display.columns
        ]

        st.dataframe(
            df_dead_display[available_columns] if available_columns else df_dead_display,
            use_container_width=True,
            hide_index=True,
        )

        latest_dead_letter = df_dead_display.iloc[0].to_dict()

        with st.expander("Latest dead-letter raw payload"):
            st.json(latest_dead_letter)

    section_title("Dead-letter analysis")

    if not df_summary.empty:
        st.dataframe(df_summary, use_container_width=True, hide_index=True)

        chart_dimension = first_existing_column(
            df_summary,
            ["event_type", "severity", "error_reason", "source_topic"],
        )
        chart_metric = first_existing_column(
            df_summary,
            ["events_count", "dead_letters_count", "count", "total"],
        )

        if chart_dimension and chart_metric:
            chart_df = df_summary[[chart_dimension, chart_metric]].copy()
            chart_df[chart_metric] = pd.to_numeric(chart_df[chart_metric], errors="coerce").fillna(0)

            if not chart_df.empty:
                st.bar_chart(chart_df.set_index(chart_dimension)[chart_metric])
    else:
        st.info("No aggregated dead-letter summary available.")

    section_title("Quality rules monitoring")

    if not df_quality.empty:
        st.dataframe(df_quality, use_container_width=True, hide_index=True)

        rule_name_col = first_existing_column(df_quality, ["rule_name", "rule_id"])
        checks_col = first_existing_column(
            df_quality,
            ["checks_count", "failed_checks", "failures_count", "events_count", "count"],
        )

        if rule_name_col and checks_col:
            chart_df = df_quality[[rule_name_col, checks_col]].copy()
            chart_df[checks_col] = pd.to_numeric(chart_df[checks_col], errors="coerce").fillna(0)

            st.subheader("Most triggered quality controls")
            st.bar_chart(chart_df.set_index(rule_name_col)[checks_col])
    else:
        st.info("No quality summary available.")

    section_title("Recent accepted events")

    if not df_recent.empty:
        preferred_recent_columns = [
            "event_id",
            "event_type",
            "customer_id",
            "product_id",
            "event_timestamp",
            "created_at",
        ]

        available_recent_columns = [
            column for column in preferred_recent_columns if column in df_recent.columns
        ]

        st.dataframe(
            df_recent[available_recent_columns] if available_recent_columns else df_recent,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Cette vue permet de comparer les événements acceptés avec les événements rejetés."
        )
    else:
        st.info("No recent accepted events available from `/events/recent`.")

    section_title("Operational quality controls")

    controls = [
        {
            "Control": "Schema validation",
            "Purpose": "Vérifier que l'événement contient les champs nécessaires.",
            "Evidence": "FastAPI event schema et consumer validation.",
        },
        {
            "Control": "Reference validation",
            "Purpose": "Vérifier que les identifiants clients, produits ou sessions sont exploitables.",
            "Evidence": "Rejet de `product_id` inexistant dans la dead-letter table.",
        },
        {
            "Control": "Allowed event type",
            "Purpose": "Empêcher des types d'événements non reconnus d'alimenter les tables analytiques.",
            "Evidence": "Rejet de `invalid_demo_event`.",
        },
        {
            "Control": "Dead-letter isolation",
            "Purpose": "Isoler les données invalides sans bloquer tout le pipeline.",
            "Evidence": "`governance.dead_letter_events`.",
        },
        {
            "Control": "Auditability",
            "Purpose": "Conserver la raison du rejet, le payload brut et l'état de reprocessing.",
            "Evidence": "`error_reason`, `raw_payload`, `reprocessed`.",
        },
        {
            "Control": "Monitoring",
            "Purpose": "Rendre les anomalies visibles dans l'interface et dans l'observabilité.",
            "Evidence": "Streamlit, PostgreSQL, Prometheus/Grafana côté plateforme.",
        },
    ]

    st.dataframe(pd.DataFrame(controls), use_container_width=True, hide_index=True)

    section_title("Quality remediation workflow")

    remediation_steps = [
        {
            "Step": 1,
            "Phase": "Detect",
            "Description": "Identifier les anomalies dans la Data Quality page ou dans les logs du consumer.",
        },
        {
            "Step": 2,
            "Phase": "Classify",
            "Description": "Qualifier la cause : type invalide, identifiant inconnu, payload incomplet ou règle métier.",
        },
        {
            "Step": 3,
            "Phase": "Correct",
            "Description": "Corriger la source, le mapping ou la règle de validation.",
        },
        {
            "Step": 4,
            "Phase": "Reprocess",
            "Description": "Rejouer les événements lorsque la correction est compatible avec les règles métier.",
        },
        {
            "Step": 5,
            "Phase": "Audit",
            "Description": "Conserver la trace de l'incident, de la correction et de la décision de reprocessing.",
        },
    ]

    st.dataframe(pd.DataFrame(remediation_steps), use_container_width=True, hide_index=True)

    section_title("What this page demonstrates")

    d1, d2, d3 = st.columns(3)

    with d1:
        info_card(
            "Pipeline reliability",
            "Le pipeline continue de fonctionner même lorsqu'un événement invalide est détecté.",
        )

    with d2:
        info_card(
            "Traceability",
            "La raison du rejet et le payload brut sont conservés pour comprendre l'erreur.",
        )

    with d3:
        info_card(
            "Governed correction",
            "Les anomalies peuvent être qualifiées, corrigées puis rejouées si nécessaire.",
        )

    academic_mapping(
        [
            {
                "Bloc": "Bloc 3",
                "Section": "Quality control flow",
                "Preuve": "Contrôle des événements entrants avant alimentation des usages analytiques.",
            },
            {
                "Bloc": "Bloc 3",
                "Section": "Latest dead-letter evidence",
                "Preuve": "Événements invalides isolés avec raison de rejet et payload brut.",
            },
            {
                "Bloc": "Bloc 3",
                "Section": "Quality rules monitoring",
                "Preuve": "Synthèse des règles qualité et anomalies observées.",
            },
            {
                "Bloc": "Bloc 3",
                "Section": "Quality remediation workflow",
                "Preuve": "Processus de correction et reprocessing des anomalies pipeline.",
            },
            {
                "Bloc": "Bloc 1",
                "Section": "Operational quality controls",
                "Preuve": "Auditabilité, traçabilité et responsabilités de gouvernance qualité.",
            },
        ]
    )

    technical_evidence(
        {
            "FastAPI endpoints": [
                "`GET /quality/dead-letters`",
                "`GET /quality/summary`",
                "`GET /quality/dead-letter-summary`",
                "`GET /events/recent`",
            ],
            "Database tables": [
                "`raw.events`",
                "`governance.dead_letter_events`",
                "`governance.data_quality_logs`",
            ],
            "Pipeline components": [
                "Streamlit demo event",
                "FastAPI event publishing",
                "Redpanda topic `retailflow_events`",
                "Python event consumer",
                "PostgreSQL dead-letter storage",
            ],
            "Related files": [
                "`streamlit_app/pages/6_Data_Quality.py`",
                "`api/app/routes/quality.py`",
                "`pipeline/consumer/`",
                "`airflow/dags/daily_data_quality.py`",
            ],
            "Manual proof": [
                "`invalid_demo_event` generated from Customer View",
                "`governance.dead_letter_events` row with `severity = high`",
                "`error_reason` explaining invalid event type and unknown product",
            ],
        }
    )

except Exception as exc:
    st.error(f"Unable to load Data Quality data: {exc}")

footer_note()
