import os

import pandas as pd
import requests
import streamlit as st

from components import load_css, section_title, info_card, footer_note


API_URL = os.getenv("API_URL", "http://fastapi:8000")

st.set_page_config(
    page_title="RetailFlow AI Monitoring",
    page_icon="🤖",
    layout="wide",
)

load_css()


def api_get(path: str, params=None):
    response = requests.get(f"{API_URL}{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def get_report(name: str):
    return api_get(f"/ai/model-report/{name}")


st.title("🤖 AI Monitoring")
st.markdown(
    """
    Cette page couvre le **Bloc 4 — AI / MLOps**.  
    Elle montre comment RetailFlow suit la performance, l’explicabilité, la validation
    et la dérive des modèles ML utilisés pour l’intelligence client.
    """
)

try:
    summary = api_get("/ai/summary")
    model_summary = get_report("model_summary")
    churn_report = get_report("churn")
    clv_report = get_report("clv")
    segmentation_report = get_report("segmentation")
    drift_report = get_report("drift")

    section_title("Executive model overview")

    churn_metrics = churn_report.get("holdout_calibrated_metrics", {}) or {}
    clv_metrics = clv_report.get("holdout_metrics", {}) or {}
    drift_overall = drift_report.get("overall", {}) or {}

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Churn ROC AUC", f"{churn_metrics.get('roc_auc', 0):.3f}")

    with k2:
        st.metric("Churn F1", f"{churn_metrics.get('f1', 0):.3f}")

    with k3:
        st.metric("CLV R²", f"{clv_metrics.get('r2', 0):.3f}")

    with k4:
        drift_label = "Detected" if drift_overall.get("drift_detected") else "Stable"
        st.metric("Drift status", drift_label)

    k5, k6, k7, k8 = st.columns(4)

    with k5:
        st.metric("CLV MAE", f"{clv_metrics.get('mae', 0):.2f}")

    with k6:
        st.metric("CLV RMSE", f"{clv_metrics.get('rmse', 0):.2f}")

    with k7:
        st.metric("Selected K", segmentation_report.get("selected_k", "N/A"))

    with k8:
        st.metric("Drifted features", drift_overall.get("drifted_features_count", 0))

    section_title("Model lifecycle")

    l1, l2, l3 = st.columns(3)

    with l1:
        info_card(
            "Training",
            "Churn, CLV and segmentation models are trained from customer behavioral features.",
        )

    with l2:
        info_card(
            "Serving",
            "Predictions are stored in PostgreSQL and exposed through FastAPI endpoints consumed by Streamlit.",
        )

    with l3:
        info_card(
            "Monitoring",
            "Reports track validation metrics, feature importance, model versions and lightweight drift detection.",
        )

    section_title("Churn model")

    c1, c2, c3 = st.columns(3)

    with c1:
        info_card(
            "Selected model",
            f"{churn_report.get('selected_model')} • version {churn_report.get('model_version')}",
        )

    with c2:
        positive_rate = churn_report.get("class_distribution", {}).get("positive_rate", 0)
        info_card(
            "Target distribution",
            f"Positive churn rate: {positive_rate:.2%}. The model uses calibrated probabilities to avoid overconfident scores.",
        )

    with c3:
        info_card(
            "Business interpretation",
            "The churn model is designed for prioritization: identifying customers who deserve retention attention.",
        )

    with st.expander("📖 Guide d'interprétation des métriques churn"):
        st.markdown(
            """
            ### ROC AUC
            **Définition**  
            Mesure la capacité du modèle à classer correctement les clients du moins risqué au plus risqué.

            **Interprétation métier**  
            Permet de prioriser les actions de rétention en identifiant les clients les plus susceptibles de quitter la plateforme.

            ### F1 Score
            **Définition**  
            Mesure l'équilibre entre la précision et le rappel.

            **Interprétation métier**  
            Indique si le modèle parvient à détecter les clients à risque sans générer trop de fausses alertes.

            ### Precision
            **Définition**  
            Pourcentage des clients prédits comme à risque qui sont réellement à risque.

            **Interprétation métier**  
            Mesure la fiabilité des alertes envoyées aux équipes.  
            Une faible précision signifie que trop de clients sont contactés inutilement.

            ### Recall
            **Définition**  
            Pourcentage des clients réellement à risque détectés par le modèle.

            **Interprétation métier**  
            Mesure la capacité du modèle à identifier les clients qu'il faut tenter de retenir avant leur départ.  
            

            ### Brier Score
            **Définition**  
            Mesure la qualité des probabilités produites par le modèle.

            **Interprétation métier**  
            Permet de vérifier si un score de risque annoncé à 70 % correspond réellement à un risque proche de 70 %.  
            Plus le score est faible, meilleure est la calibration du modèle.
            """
        )

    churn_metric_df = pd.DataFrame(
        [
            {
                "metric": "ROC AUC",
                "value": churn_metrics.get("roc_auc"),
                "meaning": "Capacité à classer correctement le risque churn.",
            },
            {
                "metric": "F1",
                "value": churn_metrics.get("f1"),
                "meaning": "Équilibre entre précision et rappel.",
            },
            {
                "metric": "Precision",
                "value": churn_metrics.get("precision"),
                "meaning": "Fiabilité des clients prédits à risque.",
            },
            {
                "metric": "Recall",
                "value": churn_metrics.get("recall"),
                "meaning": "Capacité à détecter les clients réellement à risque.",
            },
            {
                "metric": "Brier score",
                "value": churn_metrics.get("brier_score"),
                "meaning": "Qualité de calibration des probabilités.",
            },
        ]
    )

    st.dataframe(churn_metric_df, use_container_width=True, hide_index=True)

    section_title("CLV model")

    clv1, clv2, clv3 = st.columns(3)

    with clv1:
        info_card(
            "Selected model",
            f"{clv_report.get('selected_model')} • version {clv_report.get('model_version')}",
        )

    with clv2:
        target_summary = clv_report.get("target_summary", {}) or {}
        info_card(
            "Target distribution",
            f"Average synthetic CLV: {float(target_summary.get('mean', 0)):.2f} €.",
        )

    with clv3:
        info_card(
            "Business interpretation",
            "The CLV model helps prioritize customers for loyalty, upsell and retention strategies.",
        )

    with st.expander("📖 Guide d'interprétation des métriques CLV"):
        st.markdown(
            """
            ### MAE — Mean Absolute Error
            **Définition**  
            Erreur moyenne absolue entre la valeur client prédite et la valeur observée.

            **Interprétation métier**  
            Représente l'erreur moyenne commise sur la valeur financière estimée d'un client.

            ### RMSE — Root Mean Squared Error
            **Définition**  
            Erreur quadratique moyenne. Cette métrique pénalise davantage les grosses erreurs.

            **Interprétation métier**  
            Permet d'identifier si le modèle réalise parfois des erreurs importantes sur certains clients à forte valeur.

            ### R² — Coefficient de détermination
            **Définition**  
            Part de la variance expliquée par le modèle.

            **Interprétation métier**  
            Indique dans quelle mesure le modèle est capable d'expliquer les différences de valeur entre les clients.
            **Lecture rapide**   
            - `0.50` = capacité moyenne  
            - `0.80+` = très bonne capacité explicative    
            """
        )

    clv_metric_df = pd.DataFrame(
        [
            {
                "metric": "MAE",
                "value": clv_metrics.get("mae"),
                "meaning": "Erreur moyenne absolue en valeur monétaire.",
            },
            {
                "metric": "RMSE",
                "value": clv_metrics.get("rmse"),
                "meaning": "Erreur qui pénalise fortement les grosses erreurs.",
            },
            {
                "metric": "R²",
                "value": clv_metrics.get("r2"),
                "meaning": "Part de variance CLV expliquée par le modèle.",
            },
        ]
    )

    st.dataframe(clv_metric_df, use_container_width=True, hide_index=True)

    section_title("Segmentation model")

    s1, s2, s3 = st.columns(3)

    with s1:
        info_card(
            "Selected number of clusters",
            f"K = {segmentation_report.get('selected_k')} selected using {segmentation_report.get('selection_metric')}.",
        )

    with s2:
        info_card(
            "Business labels",
            "Clusters are translated into readable business segments such as High Value Loyal Customers or Promo-Sensitive Browsers.",
        )

    with s3:
        info_card(
            "Usage",
            "Segments support campaign targeting, lifecycle strategy and customer portfolio analysis.",
        )

    cluster_summary = pd.DataFrame(segmentation_report.get("cluster_summary", []))
    if not cluster_summary.empty:
        st.dataframe(cluster_summary, use_container_width=True, hide_index=True)

        if "segment_label" in cluster_summary.columns and "customers_count" in cluster_summary.columns:
            st.bar_chart(cluster_summary.set_index("segment_label")["customers_count"])

    section_title("Prediction distribution")

    with st.expander("📖 Que montre cette section ?"):
        st.markdown(
            """
            Cette visualisation présente la répartition des prédictions générées par les modèles.

            Elle permet de vérifier :
            - la cohérence des populations prédites ;
            - l'équilibre entre les différentes catégories ;
            - l'absence de comportement anormal du modèle ;
            - la présence éventuelle d'un modèle trop extrême ou trop déséquilibré.

            **Interprétation métier**  
            Cette section permet de vérifier que les modèles produisent des groupes clients réalistes.
            """
        )

    predictions_df = pd.DataFrame(summary.get("predictions_by_model", []))

    if not predictions_df.empty:
        st.dataframe(predictions_df, use_container_width=True, hide_index=True)

        predictions_df["label"] = predictions_df["model_name"] + " / " + predictions_df["prediction_label"]
        st.bar_chart(predictions_df.set_index("label")["predictions_count"])

    section_title("Feature importance")

    f1, f2 = st.columns(2)

    with f1:
        st.subheader("Churn drivers")
        churn_importance = pd.DataFrame(churn_report.get("feature_importance", []))

        if not churn_importance.empty:
            churn_top = churn_importance.head(10)
            st.dataframe(churn_top, use_container_width=True, hide_index=True)
            st.bar_chart(churn_top.set_index("feature")["normalized_importance"])
        else:
            st.info("No churn feature importance available.")

    with f2:
        st.subheader("CLV drivers")
        clv_importance = pd.DataFrame(clv_report.get("feature_importance", []))

        if not clv_importance.empty:
            clv_top = clv_importance.head(10)
            st.dataframe(clv_top, use_container_width=True, hide_index=True)
            st.bar_chart(clv_top.set_index("feature")["normalized_importance"])
        else:
            st.info("No CLV feature importance available.")

    section_title("Lightweight drift monitoring")

    with st.expander("📖 Qu'est-ce que le drift monitoring ?"):
        st.markdown(
            """
            Le **drift** correspond à une évolution du comportement des données dans le temps.

            Par exemple :
            - les habitudes d'achat changent ;
            - les profils clients évoluent ;
            - les comportements observés aujourd'hui deviennent différents de ceux utilisés lors de l'entraînement du modèle.

            ### Pourquoi surveiller le drift ?
            Même un bon modèle peut perdre en performance si les données évoluent.

            Le suivi du drift permet :
            - d'identifier une baisse potentielle de fiabilité ;
            - de déclencher une analyse ;
            - de décider d'un éventuel réentraînement.

            ### Interprétation métier
            Un drift important peut signifier que :
            - les campagnes marketing modifient le comportement client ;
            - le modèle ne représente plus correctement la réalité métier.
            """
        )

    d1, d2, d3 = st.columns(3)

    with d1:
        st.metric("Drift detected", str(drift_overall.get("drift_detected")))

    with d2:
        st.metric("Drifted features", drift_overall.get("drifted_features_count", 0))

    with d3:
        st.metric("Threshold", f"{float(drift_overall.get('threshold', 0)):.0%}")

    drift_df = pd.DataFrame(drift_report.get("feature_drift", []))

    if not drift_df.empty:
        st.dataframe(drift_df, use_container_width=True, hide_index=True)

        drift_chart = drift_df[["feature", "absolute_relative_mean_change"]].copy()
        st.bar_chart(drift_chart.set_index("feature")["absolute_relative_mean_change"])

    section_title("Validation details")

    with st.expander("Churn cross-validation"):
        st.json(churn_report.get("cross_validation", {}))

    with st.expander("CLV cross-validation"):
        st.json(clv_report.get("cross_validation", {}))

    with st.expander("Segmentation K evaluation"):
        st.json(segmentation_report.get("k_evaluation", {}))

    with st.expander("Technical evidence"):
        st.markdown(
            """
            Main artifacts used:

            - `ml/reports/churn_model_report.json`
            - `ml/reports/clv_model_report.json`
            - `ml/reports/segmentation_model_report.json`
            - `ml/reports/drift_report.json`
            - `ml/reports/model_summary.json`

            FastAPI endpoints used:

            - `/ai/summary`
            - `/ai/model-report/model_summary`
            - `/ai/model-report/churn`
            - `/ai/model-report/clv`
            - `/ai/model-report/segmentation`
            - `/ai/model-report/drift`
            """
        )

except Exception as exc:
    st.error(f"Unable to load AI Monitoring data: {exc}")

footer_note()
