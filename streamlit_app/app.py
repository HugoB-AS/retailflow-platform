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
