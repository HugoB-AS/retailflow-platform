import streamlit as st

from components import (
    load_css,
    hero,
    section_title,
    info_card,
    footer_note,
)

st.set_page_config(
    page_title="RetailFlow",
    page_icon="🔷",
    layout="wide",
)

load_css()

hero()

section_title("Welcome")

st.markdown(
    """
    RetailFlow is an end-to-end retail intelligence platform designed to demonstrate
    how a modern organization can combine data governance, real-time pipelines,
    machine learning and observability to support business decision-making.

    This project was developed as part of a Master 2 Data for Finance program and
    simulates a production-oriented retail analytics platform using synthetic data.
    """
)

section_title("Platform capabilities")

col1, col2, col3 = st.columns(3)

with col1:
    info_card(
        "Data Platform",
        "Real-time ingestion, PostgreSQL storage, Airflow orchestration and data quality controls.",
    )

with col2:
    info_card(
        "Customer Intelligence",
        "Customer segmentation, churn prediction, CLV estimation and business recommendations.",
    )

with col3:
    info_card(
        "Monitoring",
        "ML monitoring, Prometheus metrics, Grafana dashboards and platform observability.",
    )


st.info(
    "Open 'Platform Overview' from the left navigation menu to start the complete demonstration."
)

footer_note()