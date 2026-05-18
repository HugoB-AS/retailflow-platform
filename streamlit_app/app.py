import os
import uuid

import pandas as pd
import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://fastapi:8000")

st.set_page_config(
    page_title="RetailFlow Platform",
    page_icon="🛒",
    layout="wide",
)


def api_get(path: str, params=None):
    response = requests.get(f"{API_URL}{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict):
    response = requests.post(f"{API_URL}{path}", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


if "customer_id" not in st.session_state:
    st.session_state.customer_id = "cust_000001"

if "session_id" not in st.session_state:
    st.session_state.session_id = f"sess_live_{uuid.uuid4().hex[:8]}"

if "cart" not in st.session_state:
    st.session_state.cart = []


def track_event(event_type: str, product_id=None, page_url=None):
    payload = {
        "customer_id": st.session_state.customer_id,
        "session_id": st.session_state.session_id,
        "event_type": event_type,
        "product_id": product_id,
        "page_url": page_url,
    }
    api_post("/events", payload)


st.sidebar.title("RetailFlow")
st.sidebar.write(f"Customer: {st.session_state.customer_id}")
st.sidebar.write(f"Session: {st.session_state.session_id}")

page = st.sidebar.radio(
    "Navigation",
    [
        "Store Home",
        "Catalog",
        "Product Explorer",
        "Cart",
        "Checkout",
        "Analytics Dashboard",
        "Churn Candidates",
        "Data Quality Monitor",
    ],
)


if page == "Store Home":
    st.title("RetailFlow Storefront")
    st.markdown("Interactive demo storefront.")

    try:
        track_event("page_view", page_url="/")
    except:
        pass

    st.success("Store session active")

    st.markdown("""
    Simulated customer journey:

    - Browse products
    - View product details
    - Add to cart
    - Checkout
    - Generate live events
    """)


elif page == "Catalog":
    st.title("Product Catalog")

    category = st.text_input("Category filter (optional)", "")

    try:
        params = {"limit": 20}
        if category.strip():
            params["category"] = category.strip()

        products = api_get("/products", params=params)
        df = pd.DataFrame(products)

        st.dataframe(df, use_container_width=True)

        try:
            track_event("catalog_view", page_url="/catalog")
        except:
            pass

    except Exception as exc:
        st.error(f"API error: {exc}")


elif page == "Product Explorer":
    st.title("Product Explorer")

    product_id = st.text_input("Product ID", "prod_000001")

    if st.button("Load Product"):
        try:
            product = api_get(f"/products/{product_id}")

            track_event(
                "product_view",
                product_id=product_id,
                page_url=f"/product/{product_id}",
            )

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Price", f"{product['price_incl_tax']} €")
                st.metric("Stock", product["stock_quantity"])

            with col2:
                st.metric("Brand", product["brand"])
                st.metric("Category", product["category"])

            st.json(product)

            if st.button("Add to cart"):
                st.session_state.cart.append(product)

                track_event(
                    "add_to_cart",
                    product_id=product_id,
                    page_url=f"/product/{product_id}",
                )

                st.success("Added to cart")

        except Exception as exc:
            st.error(f"Error: {exc}")


elif page == "Cart":
    st.title("Cart")

    cart = st.session_state.cart

    if not cart:
        st.info("Cart is empty")
    else:
        df = pd.DataFrame(cart)
        st.dataframe(df[["product_id", "product_name", "price_incl_tax"]])

        total = df["price_incl_tax"].sum()
        st.metric("Cart total", f"{total:.2f} €")

        if st.button("Start checkout"):
            track_event("checkout_started", page_url="/checkout")
            st.success("Checkout event sent")


elif page == "Checkout":
    st.title("Checkout")

    cart = st.session_state.cart

    if not cart:
        st.warning("Cart empty")
    else:
        total = pd.DataFrame(cart)["price_incl_tax"].sum()
        st.metric("Order total", f"{total:.2f} €")

        if st.button("Confirm purchase"):
            for item in cart:
                track_event(
                    "purchase",
                    product_id=item["product_id"],
                    page_url="/checkout/complete",
                )

            st.session_state.cart = []
            st.success("Purchase simulated")


elif page == "Analytics Dashboard":
    st.title("Analytics Dashboard")

    data = api_get("/analytics/top-customers", params={"limit": 10})
    df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=True)

    if not df.empty:
        st.bar_chart(df.set_index("customer_id")["total_spent"])


elif page == "Churn Candidates":
    st.title("Churn Candidates")

    data = api_get("/analytics/churn-candidates", params={"limit": 10})
    df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=True)

    if not df.empty:
        st.bar_chart(df.set_index("customer_id")["days_since_last_order"])

elif page == "Data Quality Monitor":
    st.title("Data Quality Monitor")

    st.markdown(
        """
        Cette page montre les événements rejetés par le consumer streaming
        et les règles qualité déclenchées.
        """
    )

    try:
        dead_letters = api_get("/quality/dead-letters", params={"limit": 20})
        quality_summary = api_get("/quality/summary")
        dead_letter_summary = api_get("/quality/dead-letter-summary")

        df_dead = pd.DataFrame(dead_letters)
        df_quality = pd.DataFrame(quality_summary)
        df_summary = pd.DataFrame(dead_letter_summary)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Dead-letter events", len(df_dead))

        with col2:
            failed_rules = df_quality["rule_id"].nunique() if not df_quality.empty else 0
            st.metric("Failed rules", failed_rules)

        with col3:
            high_severity = (
                len(df_dead[df_dead["severity"] == "high"])
                if not df_dead.empty and "severity" in df_dead.columns
                else 0
            )
            st.metric("High severity", high_severity)

        st.subheader("Dead-letter events")
        st.dataframe(df_dead, use_container_width=True)

        st.subheader("Quality rules summary")
        st.dataframe(df_quality, use_container_width=True)

        st.subheader("Dead-letter summary")
        st.dataframe(df_summary, use_container_width=True)

        if not df_quality.empty:
            st.bar_chart(df_quality.set_index("rule_name")["checks_count"])

    except Exception as exc:
        st.error(f"Error loading quality metrics: {exc}")