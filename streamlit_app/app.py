import os

import pandas as pd
import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://fastapi:8000")


st.set_page_config(
    page_title="RetailFlow Demo",
    page_icon="🛒",
    layout="wide",
)


def api_get(path: str, params: dict | None = None):
    url = f"{API_URL}{path}"
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


st.sidebar.title("RetailFlow")
page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Customer Lookup",
        "Analytics Dashboard",
        "Churn Candidates",
    ],
)


if page == "Home":
    st.title("RetailFlow — Data & AI Platform")
    st.markdown(
        """
        RetailFlow est une entreprise e-commerce fictive qui modernise sa plateforme data.

        Cette interface Streamlit sert de support de démonstration pour :
        - explorer les clients ;
        - consulter des indicateurs e-commerce ;
        - identifier des clients à risque ;
        - préparer les futures démonstrations pipeline et IA.
        """
    )

    st.subheader("Architecture MVP")
    st.code(
        """
Streamlit UI
    ↓
FastAPI
    ↓
PostgreSQL
        """,
        language="text",
    )

    try:
        health = api_get("/health")
        st.success(f"API status: {health['status']} — database: {health['database']}")
    except Exception as exc:
        st.error(f"API unavailable: {exc}")


elif page == "Customer Lookup":
    st.title("Customer Lookup")

    customer_id = st.text_input("Customer ID", value="cust_000001")

    if st.button("Load customer"):
        try:
            customer = api_get(f"/customers/{customer_id}")
            st.success("Customer found")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total orders", customer.get("total_orders", 0))
                st.metric("Total spent", f"{customer.get('total_spent', 0):,.2f} €")

            with col2:
                st.metric("Avg order value", f"{customer.get('avg_order_value', 0):,.2f} €")
                st.metric("Days since last order", customer.get("days_since_last_order", 0))

            with col3:
                st.metric("Return rate", f"{customer.get('return_rate', 0) * 100:.1f}%")
                st.metric("Cart abandon rate", f"{customer.get('cart_abandon_rate', 0) * 100:.1f}%")

            st.subheader("Customer details")
            st.json(customer)

        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 404:
                st.warning("Customer not found")
            else:
                st.error(f"API error: {exc}")
        except Exception as exc:
            st.error(f"Error: {exc}")


elif page == "Analytics Dashboard":
    st.title("Analytics Dashboard")

    limit = st.slider("Number of customers", min_value=3, max_value=20, value=10)

    try:
        data = api_get("/analytics/top-customers", params={"limit": limit})
        df = pd.DataFrame(data)

        st.subheader("Top customers by revenue")
        st.dataframe(df, use_container_width=True)

        if not df.empty:
            st.bar_chart(df.set_index("customer_id")["total_spent"])

    except Exception as exc:
        st.error(f"Error loading analytics: {exc}")


elif page == "Churn Candidates":
    st.title("Churn Candidates")

    limit = st.slider("Number of candidates", min_value=3, max_value=20, value=10)

    try:
        data = api_get("/analytics/churn-candidates", params={"limit": limit})
        df = pd.DataFrame(data)

        st.subheader("Potential churn candidates")
        st.dataframe(df, use_container_width=True)

        if not df.empty:
            st.bar_chart(df.set_index("customer_id")["days_since_last_order"])

        st.info(
            "Cette première version utilise des règles métier simples. "
            "Le modèle ML de churn viendra ensuite remplacer ce scoring heuristique."
        )

    except Exception as exc:
        st.error(f"Error loading churn candidates: {exc}")
