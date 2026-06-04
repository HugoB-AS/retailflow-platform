import os

import pandas as pd
import requests
import streamlit as st

from components import load_css, section_title, info_card, footer_note


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
            "Priorité business : programme VIP, avantages exclusifs, fidélisation premium "
            "et attention commerciale renforcée."
        ),
        "Dormant Low Value Customers": (
            "Priorité business : campagne de réactivation à faible coût, relance ciblée "
            "et limitation des investissements marketing lourds."
        ),
        "Promo-Sensitive Browsers": (
            "Priorité business : offres promotionnelles, coupons limités dans le temps "
            "et messages orientés prix."
        ),
        "Return-Prone Customers": (
            "Priorité business : améliorer l'information produit, le sizing, le support client "
            "et réduire les causes de retour."
        ),
        "Standard Active Customers": (
            "Priorité business : marketing lifecycle standard, cross-sell, recommandations produits "
            "et maintien de l'engagement."
        ),
    }

    for key, value in mapping.items():
        if key in segment_label:
            return value

    return (
        "Priorité business : analyser le comportement du segment et définir une action marketing adaptée."
    )


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
            "Utiliser des campagnes automatisées à faible coût avant un effort commercial plus important."
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


st.title("🧠 Customer Intelligence")
st.markdown(
    """
    Cette page représente la **vue entreprise** de RetailFlow.
    Elle montre comment les données clients deviennent des insights actionnables :
    churn, CLV, segmentation, profil client et recommandations métier.
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

    section_title("Top churn risk customers")

    st.markdown(
        """
        Ces clients sont prioritaires pour les actions de rétention.

        Les clients avec `total_orders = 0` sont exclus de cette vue métier,
        car l'analyse de churn concerne ici des clients ayant déjà acheté.
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

    section_title("Top predicted CLV customers")

    st.markdown(
        """
        Ces clients représentent la plus forte valeur future estimée.
        Ils peuvent être priorisés pour des actions de fidélisation ou d’upsell.
        """
    )

    if not df_clv.empty:
        st.dataframe(df_clv, use_container_width=True, hide_index=True)

        chart_cols = ["customer_id", "predicted_clv"]
        if all(col in df_clv.columns for col in chart_cols):
            st.bar_chart(df_clv.set_index("customer_id")["predicted_clv"])
    else:
        st.info("No CLV predictions available.")

    section_title("Customer segments")

    if not df_segments.empty:
        st.dataframe(df_segments, use_container_width=True, hide_index=True)

        if "segment_label" in df_segments.columns and "customers_count" in df_segments.columns:
            st.bar_chart(df_segments.set_index("segment_label")["customers_count"])

        st.subheader("Segment customer explorer")

        segment_options = sorted(df_segments["segment_label"].dropna().unique().tolist())
        selected_segment = st.selectbox(
            "Select segment",
            segment_options,
            help="Affiche les clients appartenant au segment sélectionné.",
        )

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

        st.dataframe(
            df_selected_segment[available_segment_cols],
            use_container_width=True,
            hide_index=True,
        )

        st.info(segment_recommendation(selected_segment))

    else:
        st.info("No customer segments available.")

    section_title("Customer explorer")

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

            selected_customer_id = st.selectbox(
                "Select customer",
                customer_options,
                help="Explore a complete AI profile for a specific customer.",
            )

            st.caption(
                "Consent filter enabled: only customers with analytics consent are shown."
                if only_analytics_consent
                else "Consent filter disabled: all customers are shown for technical demonstration."
            )

            if st.button("Load customer AI profile", use_container_width=True):
                profile = api_get(f"/ai/customer/{selected_customer_id}")

                customer = profile.get("customer") or {}
                churn_profile = profile.get("churn") or {}
                clv_profile = profile.get("clv") or {}
                segment_profile = profile.get("segment") or {}

                st.subheader("Customer profile")

                p1, p2, p3, p4 = st.columns(4)

                with p1:
                    st.metric("Country", customer.get("country", "N/A"))

                with p2:
                    st.metric("City", customer.get("city", "N/A"))

                with p3:
                    st.metric("Total orders", customer.get("total_orders", 0))

                with p4:
                    st.metric("Total spent", f"{float(customer.get('total_spent') or 0):.2f} €")

                m1, m2, m3 = st.columns(3)

                with m1:
                    st.metric(
                        "Churn risk",
                        churn_profile.get("prediction_label", "N/A"),
                        f"{float(churn_profile.get('prediction_value') or 0):.2%}",
                    )

                with m2:
                    st.metric(
                        "Predicted CLV",
                        f"{float(clv_profile.get('prediction_value') or 0):.2f} €",
                        clv_profile.get("prediction_label", "N/A"),
                    )

                with m3:
                    st.metric(
                        "Segment",
                        segment_profile.get("segment_label", "N/A"),
                    )

                st.subheader("Behavioral features")
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

                st.subheader("Business recommendations")

                recommendations = recommendation_from_profile(profile)

                for recommendation in recommendations:
                    st.markdown(f"- {recommendation}")

                with st.expander("Raw AI profile"):
                    st.json(profile)

    section_title("What this page demonstrates")

    d1, d2, d3 = st.columns(3)

    with d1:
        info_card(
            "Business value",
            "Transforms raw customer behavior into prioritizable business actions.",
        )

    with d2:
        info_card(
            "AI serving",
            "Predictions are exposed through FastAPI endpoints and consumed by Streamlit.",
        )

    with d3:
        info_card(
            "Governed analytics",
            "Customer exploration can be restricted to analytics-consented customers.",
        )

except Exception as exc:
    st.error(f"Unable to load Customer Intelligence data: {exc}")

footer_note()
