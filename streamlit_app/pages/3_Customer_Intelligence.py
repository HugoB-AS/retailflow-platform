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


def is_truthy(value) -> bool:
    return str(value).lower() in ["true", "1", "yes", "y"]


def has_analytics_consent(customer: dict) -> bool:
    return is_truthy(customer.get("analytics_consent"))


def filter_analytics_consent(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "analytics_consent" not in df.columns:
        return df.copy()

    return df[df["analytics_consent"].apply(is_truthy)].copy()


def filter_by_authorized_customers(
    df: pd.DataFrame,
    authorized_customer_ids: set,
) -> pd.DataFrame:
    if df.empty or "customer_id" not in df.columns:
        return df.copy()

    return df[df["customer_id"].isin(authorized_customer_ids)].copy()


def build_authorized_segments(df_authorized_customers: pd.DataFrame) -> pd.DataFrame:
    if df_authorized_customers.empty or "segment_label" not in df_authorized_customers.columns:
        return pd.DataFrame()

    aggregation = {
        "customer_id": "count",
    }

    optional_average_columns = [
        "total_orders",
        "total_spent",
        "predicted_clv",
        "churn_probability",
    ]

    for column in optional_average_columns:
        if column in df_authorized_customers.columns:
            aggregation[column] = "mean"

    df_segments = (
        df_authorized_customers
        .groupby("segment_label", dropna=False)
        .agg(aggregation)
        .reset_index()
        .rename(columns={"customer_id": "customers_count"})
    )

    rename_columns = {
        "total_orders": "avg_total_orders",
        "total_spent": "avg_total_spent",
        "predicted_clv": "avg_predicted_clv",
        "churn_probability": "avg_churn_probability",
    }

    df_segments = df_segments.rename(columns=rename_columns)

    return df_segments


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
    churn = api_get("/ai/churn-top", params={"limit": 10000})
    clv = api_get("/ai/clv-top", params={"limit": 10000})
    segments = api_get("/ai/segments")
    ai_customers = api_get(
        "/ai/customers",
        params={"limit": 5000, "analytics_consent_only": False},
    )

    df_churn = pd.DataFrame(churn)
    df_clv = pd.DataFrame(clv)
    df_segments = pd.DataFrame(segments)
    df_ai_customers = pd.DataFrame(ai_customers)

    df_authorized_customers = filter_analytics_consent(df_ai_customers)
    authorized_customer_ids = set(df_authorized_customers.get("customer_id", pd.Series(dtype=str)).dropna())

    df_churn_authorized = filter_by_authorized_customers(df_churn, authorized_customer_ids)
    df_clv_authorized = filter_by_authorized_customers(df_clv, authorized_customer_ids)
    df_segments_authorized = build_authorized_segments(df_authorized_customers)

    section_title("Business overview")

    authorized_customers_count = len(authorized_customer_ids)
    authorized_prediction_rows = len(df_churn_authorized) + len(df_clv_authorized)

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Predicted customers", authorized_customers_count)

    with k2:
        st.metric("Prediction rows", authorized_prediction_rows)

    with k3:
        high_risk_count = 0

        if not df_churn_authorized.empty:
            if "prediction_label" in df_churn_authorized.columns:
                high_risk_count = int(
                    df_churn_authorized["prediction_label"]
                    .astype(str)
                    .str.contains("high", case=False, na=False)
                    .sum()
                )
            elif "churn_risk" in df_churn_authorized.columns:
                high_risk_count = int(
                    df_churn_authorized["churn_risk"]
                    .astype(str)
                    .str.contains("high", case=False, na=False)
                    .sum()
                )

        st.metric("High churn risk", high_risk_count)

    with k4:
        st.metric("Business segments", len(df_segments_authorized))

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
            df_explorer = filter_analytics_consent(df_explorer)

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
                else "Consent filter disabled: all customers are shown for governance demonstration."
            )

            profile = api_get(f"/ai/customer/{selected_customer_id}")

            customer = profile.get("customer") or {}

            if "analytics_consent" not in customer and "customer_id" in df_ai_customers.columns:
                selected_rows = df_ai_customers[df_ai_customers["customer_id"] == selected_customer_id]
                if not selected_rows.empty:
                    customer["analytics_consent"] = selected_rows.iloc[0].get("analytics_consent")

            analytics_allowed = has_analytics_consent(customer)

            b1, b2, b3 = st.columns(3)

            with b1:
                info_card(
                    "Customer context",
                    f"{customer.get('city', 'N/A')} • {customer.get('country', 'N/A')} • {customer.get('total_orders', 0)} orders",
                )

            with b2:
                info_card(
                    "Analytics consent",
                    "Granted" if analytics_allowed else "Not granted",
                )

            with b3:
                info_card(
                    "Governance rule",
                    "AI predictions are displayed only when analytics consent is granted.",
                )

            if not analytics_allowed:
                st.warning(
                    "Ce client n’a pas donné son consentement analytics. "
                    "Les prédictions IA ne sont donc pas disponibles."
                )

            else:
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

                c1, c2 = st.columns(2)

                with c1:
                    info_card(
                        "Business reason",
                        decision["reason"],
                    )

                with c2:
                    info_card(
                        "Segment",
                        segment_profile.get("segment_label", "N/A"),
                    )

                st.subheader("Recommended actions")

                recommendations = recommendation_from_profile(profile)

                for recommendation in recommendations:
                    st.markdown(f"- {recommendation}")

                with st.expander("Raw AI profile"):
                    st.json(profile)

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
            Cette vue affiche uniquement les clients avec consentement analytics.
            """
        )

        if not df_churn_authorized.empty:
            if "total_orders" in df_churn_authorized.columns:
                df_churn_display = df_churn_authorized[df_churn_authorized["total_orders"] > 0].copy()
            else:
                df_churn_display = df_churn_authorized.copy()

            st.dataframe(df_churn_display, use_container_width=True, hide_index=True)

            chart_cols = ["customer_id", "churn_probability"]
            if all(col in df_churn_display.columns for col in chart_cols) and not df_churn_display.empty:
                st.bar_chart(df_churn_display.set_index("customer_id")["churn_probability"])
        else:
            st.info("No authorized churn predictions available.")

    with tab2:
        st.markdown(
            """
            Les clients avec CLV élevée peuvent être priorisés pour les stratégies de fidélisation,
            d'upsell ou d'expérience premium. Cette vue affiche uniquement les clients avec consentement analytics.
            """
        )

        if not df_clv_authorized.empty:
            st.dataframe(df_clv_authorized, use_container_width=True, hide_index=True)

            chart_cols = ["customer_id", "predicted_clv"]
            if all(col in df_clv_authorized.columns for col in chart_cols):
                st.bar_chart(df_clv_authorized.set_index("customer_id")["predicted_clv"])
        else:
            st.info("No authorized CLV predictions available.")

    with tab3:
        if not df_segments_authorized.empty:
            st.dataframe(df_segments_authorized, use_container_width=True, hide_index=True)

            if "segment_label" in df_segments_authorized.columns and "customers_count" in df_segments_authorized.columns:
                st.bar_chart(df_segments_authorized.set_index("segment_label")["customers_count"])

            st.subheader("Segment action guide")

            segment_options = sorted(df_segments_authorized["segment_label"].dropna().unique().tolist())
            selected_segment = st.selectbox(
                "Select segment",
                segment_options,
                help="Affiche l'action recommandée pour le segment sélectionné.",
            )

            st.info(segment_recommendation(selected_segment))

            df_selected_segment = df_authorized_customers[
                df_authorized_customers["segment_label"] == selected_segment
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
            st.info("No authorized customer segments available.")

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
            "Les prédictions IA sont affichées uniquement pour les clients avec consentement analytics.",
        )

    academic_mapping(
        [
            {
                "Bloc": "Bloc 1",
                "Section": "Customer decision explorer",
                "Preuve": "Règle de gouvernance : les prédictions IA sont masquées si le consentement analytics est absent.",
            },
            {
                "Bloc": "Bloc 4",
                "Section": "Business overview",
                "Preuve": "Prédictions churn, CLV et segmentation exposées pour l'aide à la décision sur les clients autorisés.",
            },
            {
                "Bloc": "Bloc 4",
                "Section": "Decision framework",
                "Preuve": "Traduction des sorties IA en actions métier explicables.",
            },
            {
                "Bloc": "Bloc 4",
                "Section": "Customer intelligence views",
                "Preuve": "API serving des prédictions et visualisation gouvernée dans l'interface applicative.",
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
            "Governance control": [
                "AI predictions are hidden when `analytics_consent = false`.",
                "Customer intelligence views are filtered to analytics-authorized customers.",
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
