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
    page_title="RetailFlow Customer Intelligence",
    page_icon="🧠",
    layout="wide",
)

load_css()


def api_get(path: str, params=None):
    response = requests.get(f"{API_URL}{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def segment_recommendation(segment_label: str) -> str:
    mapping = {
        "High Value Loyal Customers": (
            "Programme VIP, avantages exclusifs, fidélisation premium et attention commerciale renforcée."
        ),
        "Dormant Low Value Customers": (
            "Campagne de réactivation à faible coût et limitation des investissements marketing lourds."
        ),
        "Promo-Sensitive Browsers": (
            "Offres promotionnelles, coupons limités dans le temps et messages orientés prix."
        ),
        "Return-Prone Customers": (
            "Améliorer l'information produit, le sizing, le support client et réduire les causes de retour."
        ),
        "Standard Active Customers": (
            "Marketing lifecycle standard, cross-sell, recommandations produits et maintien de l'engagement."
        ),
    }

    for key, value in mapping.items():
        if key in segment_label:
            return value

    return "Analyser le comportement du segment et définir une action marketing adaptée."


def recommendation_from_profile(profile: dict) -> list[str]:
    recommendations = []

    churn = profile.get("churn") or {}
    clv = profile.get("clv") or {}
    segment = profile.get("segment") or {}
    customer = profile.get("customer") or {}

    churn_label = churn.get("prediction_label")
    clv_label = clv.get("prediction_label")
    segment_label = segment.get("segment_label", "")
    days_since_last_order = customer.get("days_since_last_order")
    cart_abandon_rate = customer.get("cart_abandon_rate")
    return_rate = customer.get("return_rate")

    if churn_label == "high_risk":
        recommendations.append(
            "Lancer une campagne de rétention personnalisée avec une incitation ciblée."
        )
    elif churn_label == "medium_risk":
        recommendations.append(
            "Surveiller l'engagement et déclencher une relance douce."
        )
    else:
        recommendations.append(
            "Maintenir un engagement régulier via les campagnes lifecycle standard."
        )

    if clv_label == "high_value":
        recommendations.append(
            "Prioriser les avantages fidélité et un traitement VIP."
        )
    elif clv_label == "medium_value":
        recommendations.append(
            "Encourager les achats répétés avec des recommandations produits ciblées."
        )
    else:
        recommendations.append(
            "Utiliser des campagnes automatisées à faible coût avant un effort commercial lourd."
        )

    if segment_label:
        recommendations.append(segment_recommendation(segment_label))

    if days_since_last_order is not None and days_since_last_order > 180:
        recommendations.append(
            "Inactivité élevée : prioriser une campagne de réactivation."
        )

    if cart_abandon_rate is not None and cart_abandon_rate > 0.5:
        recommendations.append(
            "Taux d'abandon panier élevé : tester des rappels checkout ou une offre livraison."
        )

    if return_rate is not None and return_rate > 0.25:
        recommendations.append(
            "Taux de retour élevé : revoir l'information produit, les attentes de livraison et les signaux support."
        )

    return list(dict.fromkeys(recommendations))


def business_decision_from_profile(profile: dict) -> dict:
    churn = profile.get("churn") or {}
    clv = profile.get("clv") or {}
    segment = profile.get("segment") or {}

    churn_label = churn.get("prediction_label", "unknown")
    clv_label = clv.get("prediction_label", "unknown")
    segment_label = segment.get("segment_label", "unknown")

    if churn_label == "high_risk" and clv_label == "high_value":
        return {
            "priority": "Très élevée",
            "decision": "Rétention prioritaire premium",
            "reason": "Client à forte valeur avec risque élevé de départ.",
        }

    if churn_label == "high_risk":
        return {
            "priority": "Élevée",
            "decision": "Campagne de rétention ciblée",
            "reason": "Client identifié comme prioritaire par le modèle churn.",
        }

    if clv_label == "high_value":
        return {
            "priority": "Élevée",
            "decision": "Fidélisation et upsell",
            "reason": "Client avec valeur future élevée.",
        }

    if "Dormant" in segment_label:
        return {
            "priority": "Moyenne",
            "decision": "Réactivation automatisée",
            "reason": "Client dormant à traiter avec une campagne à faible coût.",
        }

    if "Promo-Sensitive" in segment_label:
        return {
            "priority": "Moyenne",
            "decision": "Coupon ou offre limitée",
            "reason": "Segment sensible aux promotions.",
        }

    return {
        "priority": "Standard",
        "decision": "Marketing lifecycle standard",
        "reason": "Aucun signal de priorité critique détecté.",
    }


def format_eur(value) -> str:
    try:
        return f"{float(value):.2f} €"
    except Exception:
        return "N/A"


def format_pct(value) -> str:
    try:
        return f"{float(value):.2%}"
    except Exception:
        return "N/A"


st.title("🧠 Customer Intelligence")
block_badges(["Bloc 1", "Bloc 4"])

st.markdown(
    """
    Cette page représente la vue métier de RetailFlow.
    Elle transforme les données clients et les prédictions IA en décisions actionnables :
    rétention, valeur client, segmentation et recommandations.
    """
)

try:
    summary = api_get("/ai/summary")
    churn = api_get("/ai/churn-top", params={"limit": 100})
    clv = api_get("/ai/clv-top", params={"limit": 20})
    segments = api_get("/ai/segments")
    ai_customers = api_get(
        "/ai/customers",
        params={"limit": 5000, "analytics_consent_only": False},
    )

    df_churn = pd.DataFrame(churn)
    df_clv = pd.DataFrame(clv)
    df_segments = pd.DataFrame(segments)
    df_ai_customers = pd.DataFrame(ai_customers)

    section_title("Business overview")

    freshness = summary.get("prediction_freshness", {}) or {}

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Predicted customers", freshness.get("predicted_customers", 0))

    with k2:
        st.metric("Prediction rows", freshness.get("prediction_rows", 0))

    with k3:
        high_risk_count = 0
        for row in summary.get("predictions_by_model", []):
            if row.get("model_name") == "churn_model" and row.get("prediction_label") == "high_risk":
                high_risk_count = row.get("predictions_count", 0)
        st.metric("High churn risk", high_risk_count)

    with k4:
        st.metric("Business segments", len(summary.get("segments", [])))

    section_title("Decision framework")

    d1, d2, d3, d4 = st.columns(4)

    with d1:
        proof_card(
            "High churn + high CLV",
            "Rétention prioritaire premium.",
        )

    with d2:
        proof_card(
            "High churn",
            "Campagne de rétention ciblée.",
        )

    with d3:
        proof_card(
            "High CLV",
            "Fidélisation, upsell et traitement prioritaire.",
        )

    with d4:
        proof_card(
            "Segment spécifique",
            "Action marketing adaptée au comportement.",
        )

    section_title("Customer decision explorer")

    if df_ai_customers.empty:
        st.warning("No customer data available for explorer.")
    else:
        only_analytics_consent = st.checkbox(
            "Show only customers with analytics consent",
            value=True,
            help=(
                "Lorsque cette option est activée, seuls les clients ayant donné leur "
                "consentement analytics sont disponibles dans l'explorateur."
            ),
        )

        df_explorer = df_ai_customers.copy()

        if only_analytics_consent and "analytics_consent" in df_explorer.columns:
            df_explorer = df_explorer[df_explorer["analytics_consent"] == True]

        if df_explorer.empty:
            st.warning("No customer matches the selected consent filter.")
        else:
            customer_options = df_explorer["customer_id"].dropna().tolist()

            default_index = 0
            if "churn_risk" in df_explorer.columns:
                high_risk_customers = df_explorer[
                    df_explorer["churn_risk"].astype(str).str.contains("high", case=False, na=False)
                ]["customer_id"].tolist()

                if high_risk_customers and high_risk_customers[0] in customer_options:
                    default_index = customer_options.index(high_risk_customers[0])

            selected_customer_id = st.selectbox(
                "Select customer",
                customer_options,
                index=default_index,
                help="Explore a complete AI profile for a specific customer.",
            )

            st.caption(
                "Consent filter enabled: only customers with analytics consent are shown."
                if only_analytics_consent
                else "Consent filter disabled: all customers are shown for technical demonstration."
            )

            profile = api_get(f"/ai/customer/{selected_customer_id}")

            customer = profile.get("customer") or {}
            churn_profile = profile.get("churn") or {}
            clv_profile = profile.get("clv") or {}
            segment_profile = profile.get("segment") or {}
            decision = business_decision_from_profile(profile)

            p1, p2, p3, p4 = st.columns(4)

            with p1:
                st.metric("Priority", decision["priority"])

            with p2:
                st.metric("Decision", decision["decision"])

            with p3:
                st.metric(
                    "Churn risk",
                    churn_profile.get("prediction_label", "N/A"),
                    format_pct(churn_profile.get("prediction_value")),
                )

            with p4:
                st.metric(
                    "Predicted CLV",
                    format_eur(clv_profile.get("prediction_value")),
                    clv_profile.get("prediction_label", "N/A"),
                )

            b1, b2, b3 = st.columns(3)

            with b1:
                info_card(
                    "Business reason",
                    decision["reason"],
                )

            with b2:
                info_card(
                    "Segment",
                    segment_profile.get("segment_label", "N/A"),
                )

            with b3:
                info_card(
                    "Customer context",
                    f"{customer.get('city', 'N/A')} • {customer.get('country', 'N/A')} • {customer.get('total_orders', 0)} orders",
                )

            st.subheader("Recommended actions")

            recommendations = recommendation_from_profile(profile)

            for recommendation in recommendations:
                st.markdown(f"- {recommendation}")

            with st.expander("Behavioral features"):
                st.json(
                    {
                        "avg_order_value": customer.get("avg_order_value"),
                        "days_since_last_order": customer.get("days_since_last_order"),
                        "return_rate": customer.get("return_rate"),
                        "cart_abandon_rate": customer.get("cart_abandon_rate"),
                        "session_count_30d": customer.get("session_count_30d"),
                        "pages_viewed_30d": customer.get("pages_viewed_30d"),
                        "support_tickets_count": customer.get("support_tickets_count"),
                        "discount_usage_rate": customer.get("discount_usage_rate"),
                        "preferred_category": customer.get("preferred_category"),
                    }
                )

            with st.expander("Raw AI profile"):
                st.json(profile)

    section_title("Customer intelligence views")

    tab1, tab2, tab3 = st.tabs(
        [
            "Retention priorities",
            "Customer value",
            "Segments",
        ]
    )

    with tab1:
        st.markdown(
            """
            Les clients à risque sont prioritaires pour les actions de rétention.
            Les clients sans achat sont exclus de cette vue métier quand l'information est disponible.
            """
        )

        if not df_churn.empty:
            if "total_orders" in df_churn.columns:
                df_churn_display = df_churn[df_churn["total_orders"] > 0].copy()
            else:
                df_churn_display = df_churn.copy()

            st.dataframe(df_churn_display, use_container_width=True, hide_index=True)

            chart_cols = ["customer_id", "churn_probability"]
            if all(col in df_churn_display.columns for col in chart_cols) and not df_churn_display.empty:
                st.bar_chart(df_churn_display.set_index("customer_id")["churn_probability"])
        else:
            st.info("No churn predictions available.")

    with tab2:
        st.markdown(
            """
            Les clients avec CLV élevée peuvent être priorisés pour les stratégies de fidélisation,
            d'upsell ou d'expérience premium.
            """
        )

        if not df_clv.empty:
            st.dataframe(df_clv, use_container_width=True, hide_index=True)

            chart_cols = ["customer_id", "predicted_clv"]
            if all(col in df_clv.columns for col in chart_cols):
                st.bar_chart(df_clv.set_index("customer_id")["predicted_clv"])
        else:
            st.info("No CLV predictions available.")

    with tab3:
        if not df_segments.empty:
            st.dataframe(df_segments, use_container_width=True, hide_index=True)

            if "segment_label" in df_segments.columns and "customers_count" in df_segments.columns:
                st.bar_chart(df_segments.set_index("segment_label")["customers_count"])

            st.subheader("Segment action guide")

            segment_options = sorted(df_segments["segment_label"].dropna().unique().tolist())
            selected_segment = st.selectbox(
                "Select segment",
                segment_options,
                help="Affiche l'action recommandée pour le segment sélectionné.",
            )

            st.info(segment_recommendation(selected_segment))

            df_selected_segment = df_ai_customers[
                df_ai_customers["segment_label"] == selected_segment
            ].copy()

            segment_cols = [
                "customer_id",
                "city",
                "total_orders",
                "total_spent",
                "churn_risk",
                "predicted_clv",
                "clv_band",
                "segment_label",
            ]

            available_segment_cols = [
                col for col in segment_cols if col in df_selected_segment.columns
            ]

            with st.expander("Customers in selected segment"):
                st.dataframe(
                    df_selected_segment[available_segment_cols],
                    use_container_width=True,
                    hide_index=True,
                )

        else:
            st.info("No customer segments available.")

    section_title("What this page demonstrates")

    v1, v2, v3 = st.columns(3)

    with v1:
        info_card(
            "Business value",
            "Les prédictions sont traduites en priorités et actions métier concrètes.",
        )

    with v2:
        info_card(
            "AI serving",
            "Les profils IA sont exposés par FastAPI et consommés en temps réel dans Streamlit.",
        )

    with v3:
        info_card(
            "Governed analytics",
            "L'exploration peut être limitée aux clients avec consentement analytics.",
        )

    academic_mapping(
        [
            {
                "Bloc": "Bloc 1",
                "Section": "Customer decision explorer",
                "Preuve": "Filtre analytics consent pour limiter l'usage des données clients.",
            },
            {
                "Bloc": "Bloc 4",
                "Section": "Business overview",
                "Preuve": "Prédictions churn, CLV et segmentation exposées pour l'aide à la décision.",
            },
            {
                "Bloc": "Bloc 4",
                "Section": "Decision framework",
                "Preuve": "Traduction des sorties IA en actions métier explicables.",
            },
            {
                "Bloc": "Bloc 4",
                "Section": "Customer intelligence views",
                "Preuve": "API serving des prédictions et visualisation dans l'interface applicative.",
            },
        ]
    )

    technical_evidence(
        {
            "FastAPI endpoints": [
                "`GET /ai/summary`",
                "`GET /ai/churn-top`",
                "`GET /ai/clv-top`",
                "`GET /ai/segments`",
                "`GET /ai/customers`",
                "`GET /ai/customer/{customer_id}`",
            ],
            "Database usage": [
                "`analytics.customer_features`",
                "`analytics.customer_predictions`",
                "`core.customers`",
            ],
            "AI use cases": [
                "Churn prediction",
                "Customer lifetime value prediction",
                "Customer segmentation",
                "Business recommendation logic",
            ],
            "Related files": [
                "`streamlit_app/pages/3_Customer_Intelligence.py`",
                "`api/app/routes/ai.py`",
                "`ml/src/predict.py`",
            ],
        }
    )

except Exception as exc:
    st.error(f"Unable to load Customer Intelligence data: {exc}")

footer_note()
