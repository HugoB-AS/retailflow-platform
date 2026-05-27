import os

import pandas as pd
import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://fastapi:8000")

st.set_page_config(
    page_title="RetailFlow AI Monitoring",
    page_icon="🤖",
    layout="wide",
)


def api_get(path: str, params=None):
    response = requests.get(f"{API_URL}{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def report_get(name: str):
    return api_get(f"/ai/model-report/{name}")


st.title("🤖 RetailFlow AI Monitoring")
st.markdown(
    """
    Vue hybride des modèles ML RetailFlow : indicateurs métier pour la démonstration,
    et détails techniques pour expliquer la qualité, les limites et la surveillance des modèles.
    """
)

try:
    summary = api_get("/ai/summary")
    churn_report = report_get("churn")
    clv_report = report_get("clv")
    segmentation_report = report_get("segmentation")
    drift_report = report_get("drift")

    freshness = summary.get("prediction_freshness", {}) or {}

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Predicted customers", freshness.get("predicted_customers", 0))

    with col2:
        st.metric("Prediction rows", freshness.get("prediction_rows", 0))

    with col3:
        st.metric("Churn ROC AUC", round(churn_report.get("holdout_calibrated_metrics", {}).get("roc_auc", 0), 4))

    with col4:
        st.metric("CLV R²", round(clv_report.get("holdout_metrics", {}).get("r2", 0), 4))

    st.subheader("Prediction distribution")

    predictions_df = pd.DataFrame(summary.get("predictions_by_model", []))
    if not predictions_df.empty:
        st.dataframe(predictions_df, use_container_width=True)

        chart_df = predictions_df.copy()
        chart_df["label"] = chart_df["model_name"] + " / " + chart_df["prediction_label"]
        st.bar_chart(chart_df.set_index("label")["predictions_count"])

    st.subheader("Business segments")

    segments_df = pd.DataFrame(summary.get("segments", []))
    if not segments_df.empty:
        st.dataframe(segments_df, use_container_width=True)
        st.bar_chart(segments_df.set_index("segment_label")["customers_count"])

    st.subheader("Model quality")

    q1, q2 = st.columns(2)

    with q1:
        st.markdown("### Churn model")
        st.write(f"Selected model: `{churn_report.get('selected_model')}`")
        st.write(f"Model version: `{churn_report.get('model_version')}`")
        churn_metrics = churn_report.get("holdout_calibrated_metrics", {})
        st.json({
            "roc_auc": churn_metrics.get("roc_auc"),
            "f1": churn_metrics.get("f1"),
            "precision": churn_metrics.get("precision"),
            "recall": churn_metrics.get("recall"),
            "brier_score": churn_metrics.get("brier_score"),
        })

    with q2:
        st.markdown("### CLV model")
        st.write(f"Selected model: `{clv_report.get('selected_model')}`")
        st.write(f"Model version: `{clv_report.get('model_version')}`")
        st.json(clv_report.get("holdout_metrics", {}))

    st.subheader("Feature importance")

    f1, f2 = st.columns(2)

    with f1:
        st.markdown("### Churn feature importance")
        churn_importance = pd.DataFrame(churn_report.get("feature_importance", []))
        if not churn_importance.empty:
            top = churn_importance.head(10)
            st.dataframe(top, use_container_width=True)
            st.bar_chart(top.set_index("feature")["normalized_importance"])

    with f2:
        st.markdown("### CLV feature importance")
        clv_importance = pd.DataFrame(clv_report.get("feature_importance", []))
        if not clv_importance.empty:
            top = clv_importance.head(10)
            st.dataframe(top, use_container_width=True)
            st.bar_chart(top.set_index("feature")["normalized_importance"])

    st.subheader("Lightweight drift monitoring")

    drift_overall = drift_report.get("overall", {})
    d1, d2, d3 = st.columns(3)

    with d1:
        st.metric("Drift detected", str(drift_overall.get("drift_detected")))

    with d2:
        st.metric("Drifted features", drift_overall.get("drifted_features_count", 0))

    with d3:
        st.metric("Threshold", f"{drift_overall.get('threshold', 0) * 100:.0f}%")

    drift_df = pd.DataFrame(drift_report.get("feature_drift", []))
    if not drift_df.empty:
        st.dataframe(drift_df, use_container_width=True)

        drift_chart = drift_df[["feature", "absolute_relative_mean_change"]].copy()
        st.bar_chart(drift_chart.set_index("feature")["absolute_relative_mean_change"])

    with st.expander("Technical details: churn cross-validation"):
        st.json(churn_report.get("cross_validation", {}))

    with st.expander("Technical details: CLV cross-validation"):
        st.json(clv_report.get("cross_validation", {}))

    with st.expander("Technical details: segmentation evaluation"):
        st.json({
            "selected_k": segmentation_report.get("selected_k"),
            "k_evaluation": segmentation_report.get("k_evaluation"),
            "cluster_summary": segmentation_report.get("cluster_summary"),
        })

    with st.expander("Production note"):
        st.markdown(
            """
            Le drift monitoring actuel est volontairement léger : il simule un dataset courant
            pour démontrer la logique de détection. En production, il faudrait comparer des
            snapshots réels dans le temps et déclencher des alertes ou un retraining automatique.
            """
        )

except Exception as exc:
    st.error(f"Unable to load AI monitoring data: {exc}")
