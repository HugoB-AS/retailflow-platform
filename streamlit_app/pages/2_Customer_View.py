import os
import uuid

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
    page_title="RetailFlow Customer View",
    page_icon="🛒",
    layout="wide",
)

load_css()


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
    st.session_state.session_id = f"sess_demo_{uuid.uuid4().hex[:8]}"

if "cart" not in st.session_state:
    st.session_state.cart = []

if "selected_product_id" not in st.session_state:
    st.session_state.selected_product_id = "prod_000001"


def track_event(event_type: str, product_id=None, page_url=None, raw_payload=None):
    payload = {
        "customer_id": st.session_state.customer_id,
        "session_id": st.session_state.session_id,
        "event_type": event_type,
        "product_id": product_id,
        "page_url": page_url,
        "raw_payload": raw_payload or {},
    }
    return api_post("/events", payload)


def publish_demo_journey(products, views_count: int, add_to_cart_count: int, do_checkout: bool, do_purchase: bool):
    results = []

    selected_products = products[: max(views_count, add_to_cart_count, 1)]
    cart_products = selected_products[:add_to_cart_count]

    for product in selected_products[:views_count]:
        event = track_event(
            "product_view",
            product_id=product.get("product_id"),
            page_url=f"/product/{product.get('product_id')}",
            raw_payload={
                "demo_journey": True,
                "product_name": product.get("product_name"),
                "category": product.get("category"),
                "price_incl_tax": float(product.get("price_incl_tax") or 0),
            },
        )
        results.append(
            {
                "event_type": "product_view",
                "product_id": product.get("product_id"),
                "event_id": event.get("event_id"),
                "status": "published",
            }
        )

    for product in cart_products:
        st.session_state.cart.append(product)
        event = track_event(
            "add_to_cart",
            product_id=product.get("product_id"),
            page_url=f"/product/{product.get('product_id')}",
            raw_payload={
                "demo_journey": True,
                "product_name": product.get("product_name"),
                "price_incl_tax": float(product.get("price_incl_tax") or 0),
                "cart_size": len(st.session_state.cart),
            },
        )
        results.append(
            {
                "event_type": "add_to_cart",
                "product_id": product.get("product_id"),
                "event_id": event.get("event_id"),
                "status": "published",
            }
        )

    total = sum(float(product.get("price_incl_tax") or 0) for product in cart_products)

    if do_checkout:
        event = track_event(
            "checkout_started",
            page_url="/checkout",
            raw_payload={
                "demo_journey": True,
                "cart_items": len(cart_products),
                "cart_total": total,
            },
        )
        results.append(
            {
                "event_type": "checkout_started",
                "product_id": None,
                "event_id": event.get("event_id"),
                "status": "published",
            }
        )

    if do_purchase:
        for product in cart_products:
            event = track_event(
                "purchase",
                product_id=product.get("product_id"),
                page_url="/checkout/complete",
                raw_payload={
                    "demo_journey": True,
                    "product_name": product.get("product_name"),
                    "price_incl_tax": float(product.get("price_incl_tax") or 0),
                    "cart_total": total,
                },
            )
            results.append(
                {
                    "event_type": "purchase",
                    "product_id": product.get("product_id"),
                    "event_id": event.get("event_id"),
                    "status": "published",
                }
            )

    return results


st.title("🛒 Customer View")
block_badges(["Bloc 3", "Bloc 4"])

st.markdown(
    """
    Cette page simule un parcours client e-commerce : découverte produit,
    consultation, ajout au panier, checkout et achat.

    Chaque action peut générer un événement envoyé dans la pipeline temps réel RetailFlow.
    """
)

section_title("Demo customer session")

s1, s2, s3 = st.columns([1.2, 1.2, 2])

with s1:
    st.session_state.customer_id = st.text_input(
        "Customer ID",
        value=st.session_state.customer_id,
        help="Client simulé utilisé pour générer les événements.",
    )

with s2:
    st.text_input(
        "Session ID",
        value=st.session_state.session_id,
        disabled=True,
    )

with s3:
    info_card(
        "Customer journey",
        "Product discovery → Product view event → Add to cart → Checkout started → Purchase event.",
    )

section_title("Event pipeline path")

f1, f2, f3, f4, f5 = st.columns(5)

with f1:
    proof_card("1. Streamlit", "Action utilisateur ou parcours demo.")

with f2:
    proof_card("2. FastAPI", "Endpoint /events reçoit l'événement.")

with f3:
    proof_card("3. Redpanda", "L'événement est publié dans le topic.")

with f4:
    proof_card("4. Consumer", "Validation et routage qualité.")

with f5:
    proof_card("5. PostgreSQL", "Stockage dans raw.events ou dead-letter.")

section_title("Full demo journey generator")

st.markdown(
    """
    Ce générateur permet de produire rapidement un parcours complet sans cliquer manuellement
    sur chaque étape. Il est utile pour démontrer le pipeline temps réel pendant l'oral.
    """
)

g1, g2, g3, g4, g5 = st.columns(5)

with g1:
    demo_views_count = st.number_input(
        "Nombre de produits vus",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
    )

with g2:
    demo_cart_count = st.number_input(
        "Nombre d'ajouts panier",
        min_value=0,
        max_value=10,
        value=2,
        step=1,
    )

with g3:
    demo_checkout = st.checkbox("Déclencher checkout", value=True)

with g4:
    demo_purchase = st.checkbox("Déclencher purchase", value=True)

with g5:
    st.metric("Current cart", len(st.session_state.cart))

if st.button("Generate full demo journey", use_container_width=True):
    try:
        products_for_demo = api_get(
            "/products",
            params={"limit": max(int(demo_views_count), int(demo_cart_count), 5)},
        )

        if not products_for_demo:
            st.warning("No products available to generate the demo journey.")
        else:
            results = publish_demo_journey(
                products_for_demo,
                views_count=int(demo_views_count),
                add_to_cart_count=int(demo_cart_count),
                do_checkout=bool(demo_checkout),
                do_purchase=bool(demo_purchase),
            )

            st.success(f"{len(results)} demo events published.")
            st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

    except Exception as exc:
        st.error(f"Unable to generate full demo journey: {exc}")

section_title("Invalid event for data quality demo")

st.markdown(
    """
    Ce bouton publie un événement volontairement incohérent pour démontrer le contrôle qualité.
    L'objectif est de montrer qu'un événement non conforme peut être isolé dans le mécanisme
    de dead-letter au lieu de polluer les données analytiques.
    """
)

if st.button("Generate invalid event for data quality demo", use_container_width=True):
    invalid_payload = {
        "customer_id": st.session_state.customer_id,
        "session_id": st.session_state.session_id,
        "event_type": "invalid_demo_event",
        "product_id": "prod_invalid_demo",
        "page_url": "/demo/invalid-event",
        "raw_payload": {
            "demo": True,
            "expected_destination": "governance.dead_letter_events",
            "reason": "Unsupported event_type generated for data quality demonstration.",
        },
    }

    try:
        response = api_post("/events", invalid_payload)
        st.warning(
            "Invalid demo event published. Check the Data Quality page after the consumer processes it."
        )
        st.json(response)

    except Exception as exc:
        st.error(
            "The API rejected the invalid event before the streaming pipeline. "
            f"Error: {exc}"
        )

section_title("Product catalog")

try:
    all_products = api_get("/products", params={"limit": 200})
    df_all = pd.DataFrame(all_products)

    if df_all.empty:
        st.warning("No products returned by the API.")
    else:
        categories = ["All"] + sorted(df_all["category"].dropna().unique().tolist())

        c1, c2, c3 = st.columns([1.2, 1, 2])

        with c1:
            selected_category = st.selectbox("Category", categories)

        with c2:
            limit = st.slider("Products shown", min_value=5, max_value=50, value=20, step=5)

        params = {"limit": limit}
        if selected_category != "All":
            params["category"] = selected_category

        products = api_get("/products", params=params)
        df_products = pd.DataFrame(products)

        if not df_products.empty:
            display_cols = [
                "product_id",
                "product_name",
                "category",
                "subcategory",
                "brand",
                "price_incl_tax",
                "stock_quantity",
            ]
            available_cols = [col for col in display_cols if col in df_products.columns]

            st.dataframe(
                df_products[available_cols],
                use_container_width=True,
                hide_index=True,
            )

            product_options = df_products["product_id"].tolist()

            if st.session_state.selected_product_id not in product_options:
                st.session_state.selected_product_id = product_options[0]

            st.session_state.selected_product_id = st.selectbox(
                "Select a product to explore",
                product_options,
                index=product_options.index(st.session_state.selected_product_id),
            )

except Exception as exc:
    st.error(f"Unable to load product catalog: {exc}")

section_title("Product explorer")

try:
    product = api_get(f"/products/{st.session_state.selected_product_id}")

    p1, p2, p3 = st.columns([1.1, 1.1, 1.4])

    with p1:
        st.metric("Price", f"{float(product['price_incl_tax']):.2f} €")
        st.metric("Stock", product.get("stock_quantity", 0))

    with p2:
        st.metric("Brand", product.get("brand", "N/A"))
        st.metric("Category", product.get("category", "N/A"))

    with p3:
        info_card(
            product.get("product_name", "Product"),
            f"Product ID: {product.get('product_id')} • Color: {product.get('color')} • Material: {product.get('material')}",
        )

    with st.expander("Product details"):
        st.json(product)

    b1, b2, b3 = st.columns([1, 1, 2])

    with b1:
        if st.button("Generate product view event", use_container_width=True):
            event = track_event(
                "product_view",
                product_id=product["product_id"],
                page_url=f"/product/{product['product_id']}",
                raw_payload={
                    "product_name": product.get("product_name"),
                    "category": product.get("category"),
                    "price_incl_tax": float(product.get("price_incl_tax", 0)),
                },
            )
            st.success(f"Product view event published: {event['event_id']}")

    with b2:
        if st.button("Add to cart", use_container_width=True):
            st.session_state.cart.append(product)

            event = track_event(
                "add_to_cart",
                product_id=product["product_id"],
                page_url=f"/product/{product['product_id']}",
                raw_payload={
                    "product_name": product.get("product_name"),
                    "price_incl_tax": float(product.get("price_incl_tax", 0)),
                    "cart_size": len(st.session_state.cart),
                },
            )
            st.success(f"Add-to-cart event published: {event['event_id']}")

    with b3:
        info_card(
            "Streaming link",
            "Each product interaction is published to Redpanda, consumed by the event consumer and stored in PostgreSQL.",
        )

except Exception as exc:
    st.error(f"Unable to load product details: {exc}")

section_title("Cart and checkout simulation")

cart = st.session_state.cart

if not cart:
    st.info("The simulated cart is currently empty.")
else:
    df_cart = pd.DataFrame(cart)
    cart_cols = [
        "product_id",
        "product_name",
        "category",
        "brand",
        "price_incl_tax",
    ]
    available_cart_cols = [col for col in cart_cols if col in df_cart.columns]

    st.dataframe(
        df_cart[available_cart_cols],
        use_container_width=True,
        hide_index=True,
    )

    total = float(df_cart["price_incl_tax"].sum())

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Cart items", len(cart))

    with c2:
        st.metric("Cart total", f"{total:.2f} €")

    with c3:
        if st.button("Start checkout", use_container_width=True):
            event = track_event(
                "checkout_started",
                page_url="/checkout",
                raw_payload={
                    "cart_items": len(cart),
                    "cart_total": total,
                },
            )
            st.success(f"Checkout event published: {event['event_id']}")

    with c4:
        if st.button("Complete purchase", use_container_width=True):
            for item in cart:
                track_event(
                    "purchase",
                    product_id=item["product_id"],
                    page_url="/checkout/complete",
                    raw_payload={
                        "product_name": item.get("product_name"),
                        "price_incl_tax": float(item.get("price_incl_tax", 0)),
                        "cart_total": total,
                    },
                )

            st.session_state.cart = []
            st.success("Purchase events published and cart cleared.")

    if st.button("Clear cart"):
        st.session_state.cart = []
        st.info("Cart cleared.")

section_title("Recent event stream preview")

try:
    recent_events = api_get("/events/recent", params={"limit": 20})
    df_events = pd.DataFrame(recent_events)

    if df_events.empty:
        st.info("No recent events available yet. Generate product or checkout events above.")
    else:
        st.dataframe(
            df_events,
            use_container_width=True,
            hide_index=True,
        )

except Exception as exc:
    st.warning(f"Unable to load recent events yet: {exc}")

section_title("What this page demonstrates")

d1, d2, d3 = st.columns(3)

with d1:
    info_card(
        "Business side",
        "A realistic e-commerce customer journey that creates behavioral signals.",
    )

with d2:
    info_card(
        "Data engineering side",
        "Events are sent through the streaming pipeline and persisted for analytics and monitoring.",
    )

with d3:
    info_card(
        "AI side",
        "Customer behavior becomes input for churn, CLV and segmentation models.",
    )

academic_mapping(
    [
        {
            "Bloc": "Bloc 3",
            "Section": "Full demo journey generator",
            "Preuve": "Génération d'événements temps réel utilisés par le pipeline.",
        },
        {
            "Bloc": "Bloc 3",
            "Section": "Invalid event for data quality demo",
            "Preuve": "Démonstration du routage qualité et du mécanisme dead-letter.",
        },
        {
            "Bloc": "Bloc 3",
            "Section": "Recent event stream preview",
            "Preuve": "Visualisation des événements ingérés et persistés.",
        },
        {
            "Bloc": "Bloc 4",
            "Section": "What this page demonstrates",
            "Preuve": "Les comportements clients deviennent des signaux exploitables pour l'IA.",
        },
    ]
)

technical_evidence(
    {
        "FastAPI endpoints": [
            "`GET /products`",
            "`GET /products/{product_id}`",
            "`POST /events`",
            "`GET /events/recent`",
        ],
        "Streaming path": [
            "Streamlit user action",
            "FastAPI `/events` endpoint",
            "Redpanda topic `retailflow_events`",
            "Python event consumer",
            "PostgreSQL `raw.events` or `governance.dead_letter_events`",
        ],
        "Related files": [
            "`streamlit_app/pages/2_Customer_View.py`",
            "`api/app/routes/events.py`",
            "`api/app/services/event_producer.py`",
            "`pipeline/consumer/event_consumer.py`",
            "`pipeline/consumer/validators.py`",
        ],
    }
)

with st.expander("Minimal legal information"):
    st.markdown(
        """
        **RetailFlow Demo Store**

        Société fictive utilisée dans un cadre académique.  
        Siège social : Paris, France.  
        Contact : support@retailflow.com
        """
    )

footer_note()
