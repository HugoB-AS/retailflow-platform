"""
RetailFlow synthetic dataset generator.

This generator creates coherent e-commerce data for:
- Data Governance
- Data Architecture
- Real-time pipelines
- ML / MLOps

Important design choice:
Customer personas are used internally to generate realistic behavior,
but they are NOT exported to the database. Models must infer patterns
from observable behavior.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from faker import Faker
from tqdm import tqdm


NOW = datetime.now().replace(microsecond=0)

CATEGORIES = {
    "electronics": ["laptop", "smartphone", "headphones", "monitor", "keyboard"],
    "home": ["chair", "lamp", "desk", "coffee_machine", "storage_box"],
    "fashion": ["shoes", "jacket", "tshirt", "bag", "watch"],
    "beauty": ["skincare", "perfume", "makeup", "haircare", "wellness"],
    "sports": ["fitness_tracker", "running_shoes", "bike_accessory", "yoga_mat", "dumbbells"],
    "books": ["business", "data_science", "fiction", "self_improvement", "education"],
}

CATEGORY_PRICE_RANGES = {
    "electronics": (80, 1800),
    "home": (25, 600),
    "fashion": (20, 500),
    "beauty": (10, 250),
    "sports": (15, 700),
    "books": (8, 80),
}

COUNTRIES = ["France", "Belgium", "Germany", "Spain", "Italy", "Netherlands"]
MANUFACTURING_COUNTRIES = ["France", "Germany", "Italy", "Spain", "China", "Vietnam", "Poland", "Portugal"]

LOYALTY_BY_PERSONA = {
    "loyal_high_value": "gold",
    "promo_hunter": "silver",
    "window_shopper": "bronze",
    "dissatisfied_customer": "bronze",
    "new_customer": "new",
    "luxury_buyer": "platinum",
    "at_risk_former_loyal": "gold",
}

PREFERRED_CATEGORY_BY_PERSONA = {
    "loyal_high_value": ["electronics", "home", "sports"],
    "promo_hunter": ["fashion", "beauty", "home"],
    "window_shopper": ["electronics", "fashion", "beauty"],
    "dissatisfied_customer": ["fashion", "electronics", "home"],
    "new_customer": ["fashion", "beauty", "books", "electronics"],
    "luxury_buyer": ["electronics", "fashion", "home"],
    "at_risk_former_loyal": ["electronics", "home", "sports"],
}

ORDER_WEIGHT_BY_PERSONA = {
    "loyal_high_value": 2.5,
    "promo_hunter": 1.6,
    "window_shopper": 0.35,
    "dissatisfied_customer": 0.9,
    "new_customer": 0.55,
    "luxury_buyer": 0.8,
    "at_risk_former_loyal": 1.9,
}

SESSION_WEIGHT_BY_PERSONA = {
    "loyal_high_value": 1.5,
    "promo_hunter": 1.4,
    "window_shopper": 2.7,
    "dissatisfied_customer": 0.8,
    "new_customer": 1.2,
    "luxury_buyer": 0.7,
    "at_risk_former_loyal": 0.55,
}

CONVERSION_RATE_BY_PERSONA = {
    "loyal_high_value": 0.42,
    "promo_hunter": 0.30,
    "window_shopper": 0.06,
    "dissatisfied_customer": 0.10,
    "new_customer": 0.14,
    "luxury_buyer": 0.25,
    "at_risk_former_loyal": 0.08,
}

DISCOUNT_RATE_BY_PERSONA = {
    "loyal_high_value": 0.18,
    "promo_hunter": 0.72,
    "window_shopper": 0.22,
    "dissatisfied_customer": 0.18,
    "new_customer": 0.28,
    "luxury_buyer": 0.05,
    "at_risk_former_loyal": 0.32,
}

RETURN_WEIGHT_BY_PERSONA = {
    "loyal_high_value": 0.6,
    "promo_hunter": 1.1,
    "window_shopper": 0.4,
    "dissatisfied_customer": 4.0,
    "new_customer": 0.9,
    "luxury_buyer": 0.5,
    "at_risk_former_loyal": 1.3,
}

SUPPORT_WEIGHT_BY_PERSONA = {
    "loyal_high_value": 0.5,
    "promo_hunter": 0.9,
    "window_shopper": 0.3,
    "dissatisfied_customer": 5.0,
    "new_customer": 0.7,
    "luxury_buyer": 0.8,
    "at_risk_former_loyal": 1.8,
}

REVIEW_RATING_BY_PERSONA = {
    "loyal_high_value": [4, 5, 5, 5],
    "promo_hunter": [3, 4, 4, 5],
    "window_shopper": [3, 4, 4],
    "dissatisfied_customer": [1, 2, 2, 3],
    "new_customer": [3, 4, 5],
    "luxury_buyer": [4, 5, 5],
    "at_risk_former_loyal": [2, 3, 4],
}


def load_config(config_path: str) -> dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def make_id(prefix: str, number: int, width: int = 6) -> str:
    return f"{prefix}_{number:0{width}d}"


def random_datetime_between(rng: np.random.Generator, start: datetime, end: datetime) -> datetime:
    delta_seconds = int((end - start).total_seconds())
    if delta_seconds <= 0:
        return start
    return start + timedelta(seconds=int(rng.integers(0, delta_seconds)))


def sample_past_datetime(rng: np.random.Generator, persona: str) -> datetime:
    """Sample order/session dates with persona-specific recency behavior."""
    if persona == "new_customer":
        days_ago = int(rng.integers(1, 120))
    elif persona == "at_risk_former_loyal":
        days_ago = int(rng.integers(120, 730))
    elif persona == "loyal_high_value":
        days_ago = int(rng.choice([rng.integers(1, 90), rng.integers(90, 730)], p=[0.45, 0.55]))
    elif persona == "luxury_buyer":
        days_ago = int(rng.integers(15, 730))
    elif persona == "dissatisfied_customer":
        days_ago = int(rng.integers(30, 540))
    else:
        days_ago = int(rng.integers(1, 730))

    hour = int(rng.integers(8, 23))
    minute = int(rng.integers(0, 60))
    second = int(rng.integers(0, 60))
    return (NOW - timedelta(days=days_ago)).replace(hour=hour, minute=minute, second=second)


def weighted_choice(values: list[str], weights: list[float], rng: np.random.Generator, size: int) -> np.ndarray:
    probs = np.array(weights, dtype=float)
    probs = probs / probs.sum()
    return rng.choice(values, size=size, p=probs)


def generate_customers(
    n_customers: int,
    personas_config: dict[str, float],
    fake: Faker,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, dict[str, str], dict[str, str]]:
    personas = list(personas_config.keys())
    weights = list(personas_config.values())
    sampled_personas = weighted_choice(personas, weights, rng, n_customers)

    rows = []
    persona_by_customer: dict[str, str] = {}
    preferred_category_by_customer: dict[str, str] = {}

    for i in tqdm(range(1, n_customers + 1), desc="Generating customers"):
        customer_id = make_id("cust", i)
        persona = str(sampled_personas[i - 1])
        persona_by_customer[customer_id] = persona

        preferred_category = str(rng.choice(PREFERRED_CATEGORY_BY_PERSONA[persona]))
        preferred_category_by_customer[customer_id] = preferred_category

        registration_days_ago = {
            "new_customer": int(rng.integers(1, 120)),
            "at_risk_former_loyal": int(rng.integers(700, 1600)),
            "loyal_high_value": int(rng.integers(365, 1600)),
            "luxury_buyer": int(rng.integers(200, 1600)),
        }.get(persona, int(rng.integers(30, 1300)))

        registration_date = (NOW - timedelta(days=registration_days_ago)).date()

        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name}.{last_name}.{i}@example-retailflow.local".lower().replace(" ", "")
        country = str(rng.choice(COUNTRIES))
        city = fake.city()

        marketing_prob = {
            "loyal_high_value": 0.75,
            "promo_hunter": 0.85,
            "window_shopper": 0.45,
            "dissatisfied_customer": 0.25,
            "new_customer": 0.55,
            "luxury_buyer": 0.50,
            "at_risk_former_loyal": 0.40,
        }[persona]

        analytics_prob = 0.78
        personalization_prob = {
            "loyal_high_value": 0.70,
            "promo_hunter": 0.65,
            "window_shopper": 0.45,
            "dissatisfied_customer": 0.30,
            "new_customer": 0.50,
            "luxury_buyer": 0.55,
            "at_risk_former_loyal": 0.38,
        }[persona]

        account_status = "active"
        if persona == "at_risk_former_loyal" and rng.random() < 0.25:
            account_status = "inactive"
        if persona == "dissatisfied_customer" and rng.random() < 0.10:
            account_status = "inactive"

        rows.append(
            {
                "customer_id": customer_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone_number": fake.phone_number(),
                "birth_date": fake.date_of_birth(minimum_age=18, maximum_age=78),
                "gender": str(rng.choice(["female", "male", "other", "not_specified"], p=[0.47, 0.47, 0.02, 0.04])),
                "country": country,
                "city": city,
                "postal_code": fake.postcode(),
                "registration_date": registration_date,
                "marketing_consent": bool(rng.random() < marketing_prob),
                "analytics_consent": bool(rng.random() < analytics_prob),
                "personalization_consent": bool(rng.random() < personalization_prob),
                "loyalty_status": LOYALTY_BY_PERSONA[persona],
                "account_status": account_status,
                "created_at": datetime.combine(registration_date, datetime.min.time()),
                "updated_at": NOW,
                "last_interaction_at": None,
                "is_anonymized": False,
                "anonymized_at": None,
            }
        )

    return pd.DataFrame(rows), persona_by_customer, preferred_category_by_customer


def generate_suppliers(n_suppliers: int, fake: Faker, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for i in tqdm(range(1, n_suppliers + 1), desc="Generating suppliers"):
        supplier_id = make_id("sup", i)
        esg_score = float(np.round(rng.uniform(35, 98), 2))
        esg_compliant = esg_score >= 65
        certifications = []
        if esg_compliant:
            certifications = list(rng.choice(["ISO14001", "B-Corp", "EcoVadis", "FairTrade"], size=int(rng.integers(1, 3)), replace=False))

        rows.append(
            {
                "supplier_id": supplier_id,
                "supplier_name": fake.company(),
                "country": str(rng.choice(MANUFACTURING_COUNTRIES)),
                "esg_compliant": bool(esg_compliant),
                "esg_score": esg_score,
                "certifications": ",".join(certifications),
                "supplier_risk_level": "low" if esg_score >= 75 else "medium" if esg_score >= 55 else "high",
                "primary_contact_name": fake.name(),
                "primary_contact_email": fake.company_email(),
                "primary_contact_role": str(rng.choice(["Account Manager", "Sales Director", "Operations Manager", "Sustainability Officer"])),
                "support_phone": fake.phone_number(),
                "created_at": NOW - timedelta(days=int(rng.integers(200, 1500))),
                "updated_at": NOW,
            }
        )
    return pd.DataFrame(rows)


def generate_products(n_products: int, suppliers: pd.DataFrame, fake: Faker, rng: np.random.Generator) -> pd.DataFrame:
    supplier_ids = suppliers["supplier_id"].tolist()
    rows = []

    for i in tqdm(range(1, n_products + 1), desc="Generating products"):
        product_id = make_id("prod", i)
        category = str(rng.choice(list(CATEGORIES.keys())))
        subcategory = str(rng.choice(CATEGORIES[category]))
        min_price, max_price = CATEGORY_PRICE_RANGES[category]
        price_excl_tax = float(np.round(rng.uniform(min_price, max_price), 2))
        tax_rate = 0.055 if category == "books" else 0.20
        price_incl_tax = float(np.round(price_excl_tax * (1 + tax_rate), 2))
        cost = float(np.round(price_excl_tax * rng.uniform(0.45, 0.78), 2))

        rows.append(
            {
                "product_id": product_id,
                "product_name": f"{fake.word().title()} {subcategory.replace('_', ' ').title()}",
                "category": category,
                "subcategory": subcategory,
                "brand": fake.company().split()[0],
                "color": str(rng.choice(["black", "white", "blue", "green", "red", "silver", "beige", "none"])),
                "size": str(rng.choice(["XS", "S", "M", "L", "XL", "standard", "none"])),
                "material": str(rng.choice(["plastic", "metal", "cotton", "leather", "wood", "paper", "mixed"])),
                "manufacturing_country": str(rng.choice(MANUFACTURING_COUNTRIES)),
                "price_excl_tax": price_excl_tax,
                "tax_rate": tax_rate,
                "price_incl_tax": price_incl_tax,
                "cost": cost,
                "stock_quantity": int(rng.integers(0, 1000)),
                "supplier_id": str(rng.choice(supplier_ids)),
                "image_code": f"{category}_{i:04d}",
                "is_active": bool(rng.random() > 0.04),
                "created_at": NOW - timedelta(days=int(rng.integers(30, 1300))),
                "updated_at": NOW,
            }
        )

    return pd.DataFrame(rows)


def adjusted_item_counts(n_orders: int, target_items: int, rng: np.random.Generator) -> np.ndarray:
    counts = rng.choice([1, 2, 3, 4, 5], size=n_orders, p=[0.22, 0.32, 0.25, 0.14, 0.07])
    diff = int(target_items - counts.sum())

    while diff > 0:
        idx = int(rng.integers(0, n_orders))
        if counts[idx] < 8:
            counts[idx] += 1
            diff -= 1

    while diff < 0:
        idx = int(rng.integers(0, n_orders))
        if counts[idx] > 1:
            counts[idx] -= 1
            diff += 1

    return counts


def generate_orders_and_related(
    n_orders: int,
    target_order_items: int,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    persona_by_customer: dict[str, str],
    preferred_category_by_customer: dict[str, str],
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    customer_ids = customers["customer_id"].tolist()
    order_weights = np.array([ORDER_WEIGHT_BY_PERSONA[persona_by_customer[cid]] for cid in customer_ids], dtype=float)
    order_weights = order_weights / order_weights.sum()

    product_by_category = {
        category: products[products["category"] == category]["product_id"].tolist()
        for category in products["category"].unique()
    }
    product_lookup = products.set_index("product_id").to_dict("index")

    order_item_counts = adjusted_item_counts(n_orders, target_order_items, rng)

    orders = []
    order_items = []
    payments = []
    shipments = []
    item_counter = 1

    for order_number in tqdm(range(1, n_orders + 1), desc="Generating orders"):
        order_id = make_id("ord", order_number)
        customer_id = str(rng.choice(customer_ids, p=order_weights))
        persona = persona_by_customer[customer_id]
        order_datetime = sample_past_datetime(rng, persona)

        items_count = int(order_item_counts[order_number - 1])
        preferred_category = preferred_category_by_customer[customer_id]

        subtotal_excl_tax = 0.0
        total_tax = 0.0
        total_incl_tax = 0.0

        for _ in range(items_count):
            if rng.random() < 0.72 and product_by_category.get(preferred_category):
                product_id = str(rng.choice(product_by_category[preferred_category]))
            else:
                product_id = str(rng.choice(products["product_id"].values))

            product = product_lookup[product_id]
            quantity = int(rng.choice([1, 1, 1, 2, 2, 3], p=[0.45, 0.15, 0.10, 0.18, 0.08, 0.04]))
            discount_used = rng.random() < DISCOUNT_RATE_BY_PERSONA[persona]
            discount_rate = float(np.round(rng.uniform(0.05, 0.35), 2)) if discount_used else 0.0

            unit_price_excl_tax = float(product["price_excl_tax"])
            tax_rate = float(product["tax_rate"])
            unit_price_incl_tax = float(product["price_incl_tax"])

            line_total_excl_tax = float(np.round(unit_price_excl_tax * quantity * (1 - discount_rate), 2))
            line_tax_amount = float(np.round(line_total_excl_tax * tax_rate, 2))
            line_total_incl_tax = float(np.round(line_total_excl_tax + line_tax_amount, 2))

            subtotal_excl_tax += line_total_excl_tax
            total_tax += line_tax_amount
            total_incl_tax += line_total_incl_tax

            order_items.append(
                {
                    "order_item_id": make_id("item", item_counter),
                    "order_id": order_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_price_excl_tax": unit_price_excl_tax,
                    "tax_rate": tax_rate,
                    "unit_price_incl_tax": unit_price_incl_tax,
                    "discount_rate": discount_rate,
                    "line_total_excl_tax": line_total_excl_tax,
                    "line_tax_amount": line_tax_amount,
                    "line_total_incl_tax": line_total_incl_tax,
                }
            )
            item_counter += 1

        discount_amount = float(np.round(subtotal_excl_tax * rng.uniform(0.02, 0.08), 2)) if rng.random() < 0.15 else 0.0

        order_status = str(rng.choice(["paid", "shipped", "delivered", "cancelled"], p=[0.08, 0.12, 0.77, 0.03]))
        payment_status = "failed" if order_status == "cancelled" and rng.random() < 0.55 else "succeeded"
        shipping_status = {
            "paid": "pending",
            "shipped": "in_transit",
            "delivered": "delivered",
            "cancelled": "cancelled",
        }[order_status]

        orders.append(
            {
                "order_id": order_id,
                "customer_id": customer_id,
                "order_datetime": order_datetime,
                "order_hour": order_datetime.hour,
                "order_status": order_status,
                "sales_channel": str(rng.choice(["web", "mobile_app"], p=[0.62, 0.38])),
                "items_count": items_count,
                "total_excl_tax": float(np.round(subtotal_excl_tax, 2)),
                "tax_amount": float(np.round(total_tax, 2)),
                "total_incl_tax": float(np.round(total_incl_tax, 2)),
                "discount_amount": discount_amount,
                "coupon_code": f"PROMO{int(rng.integers(10, 99))}" if discount_amount > 0 else None,
                "payment_status": payment_status,
                "shipping_status": shipping_status,
                "delivery_address": f"{int(rng.integers(1, 250))} {str(rng.choice(['rue', 'avenue', 'boulevard']))} Retail",
                "delivery_city": str(rng.choice(["Paris", "Lyon", "Marseille", "Lille", "Bordeaux", "Nantes", "Toulouse"])),
                "delivery_postal_code": str(int(rng.integers(10000, 95999))),
                "delivery_country": "France",
                "has_return": False,
                "return_status": None,
                "returned_items_count": 0,
                "refund_total_amount": 0.0,
                "created_at": order_datetime,
                "updated_at": NOW,
            }
        )

        payments.append(
            {
                "payment_id": make_id("pay", order_number),
                "order_id": order_id,
                "payment_method": str(rng.choice(["card", "paypal", "apple_pay", "bank_transfer"], p=[0.70, 0.15, 0.10, 0.05])),
                "payment_provider": str(rng.choice(["Stripe", "Adyen", "PayPal", "MockBank"], p=[0.45, 0.30, 0.20, 0.05])),
                "card_network": str(rng.choice(["Visa", "Mastercard", "Amex", "none"], p=[0.48, 0.42, 0.05, 0.05])),
                "payment_status": payment_status,
                "payment_amount": float(np.round(total_incl_tax, 2)),
                "payment_datetime": order_datetime + timedelta(minutes=int(rng.integers(1, 10))),
                "transaction_reference_tokenized": f"tok_{order_id}_{int(rng.integers(10000, 99999))}",
                "fraud_score": float(np.round(rng.uniform(0.001, 0.25), 4)),
                "created_at": order_datetime,
            }
        )

        if order_status != "cancelled":
            estimated = order_datetime + timedelta(days=int(rng.integers(2, 8)))
            actual = estimated + timedelta(days=int(rng.choice([-1, 0, 0, 1, 2, 3], p=[0.10, 0.45, 0.15, 0.15, 0.10, 0.05])))
            shipments.append(
                {
                    "shipment_id": make_id("shp", len(shipments) + 1),
                    "order_id": order_id,
                    "shipment_direction": "outbound",
                    "carrier": str(rng.choice(["Colissimo", "DHL", "UPS", "Chronopost", "Mondial Relay"])),
                    "shipping_date": order_datetime + timedelta(days=1),
                    "estimated_delivery_date": estimated,
                    "actual_delivery_date": actual if order_status == "delivered" else None,
                    "delivery_status": shipping_status,
                    "shipping_delay_days": int((actual - estimated).days) if order_status == "delivered" else None,
                    "tracking_reference": f"trk_{order_id}",
                    "created_at": order_datetime,
                }
            )

    return pd.DataFrame(orders), pd.DataFrame(order_items), pd.DataFrame(payments), pd.DataFrame(shipments)


def generate_returns(
    n_returns: int,
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    products: pd.DataFrame,
    persona_by_customer: dict[str, str],
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    delivered_orders = orders[orders["order_status"].isin(["delivered", "shipped"])].copy()
    eligible_items = order_items.merge(delivered_orders[["order_id", "customer_id", "order_datetime"]], on="order_id", how="inner")
    eligible_items = eligible_items.merge(products[["product_id", "category"]], on="product_id", how="left")

    if eligible_items.empty:
        return pd.DataFrame(), orders, pd.DataFrame()

    weights = []
    for _, row in eligible_items.iterrows():
        persona = persona_by_customer[str(row["customer_id"])]
        category_factor = 1.8 if row["category"] == "fashion" else 1.2 if row["category"] == "electronics" else 1.0
        weights.append(RETURN_WEIGHT_BY_PERSONA[persona] * category_factor)

    weights_np = np.array(weights, dtype=float)
    weights_np = weights_np / weights_np.sum()

    n_returns = min(n_returns, len(eligible_items))
    chosen_idx = rng.choice(eligible_items.index.values, size=n_returns, replace=False, p=weights_np)

    returns = []
    return_shipments = []

    for i, idx in enumerate(tqdm(chosen_idx, desc="Generating returns"), start=1):
        item = eligible_items.loc[idx]
        return_date = pd.to_datetime(item["order_datetime"]).to_pydatetime() + timedelta(days=int(rng.integers(5, 60)))
        refund_amount = float(np.round(float(item["line_total_incl_tax"]) * rng.uniform(0.75, 1.0), 2))

        returns.append(
            {
                "return_id": make_id("ret", i),
                "order_id": item["order_id"],
                "product_id": item["product_id"],
                "customer_id": item["customer_id"],
                "return_date": return_date,
                "return_reason": str(rng.choice(["size_issue", "defective", "not_as_expected", "late_delivery", "changed_mind"])),
                "return_status": str(rng.choice(["requested", "approved", "refunded"], p=[0.15, 0.25, 0.60])),
                "refund_amount": refund_amount,
                "is_refunded": bool(rng.random() < 0.70),
                "created_at": return_date,
            }
        )

        return_shipments.append(
            {
                "shipment_id": make_id("rshp", i),
                "order_id": item["order_id"],
                "shipment_direction": "return",
                "carrier": str(rng.choice(["Colissimo", "DHL", "UPS", "Mondial Relay"])),
                "shipping_date": return_date,
                "estimated_delivery_date": return_date + timedelta(days=4),
                "actual_delivery_date": return_date + timedelta(days=int(rng.integers(3, 8))),
                "delivery_status": "returned",
                "shipping_delay_days": int(rng.integers(0, 4)),
                "tracking_reference": f"rtrk_{item['order_id']}_{i}",
                "created_at": return_date,
            }
        )

    returns_df = pd.DataFrame(returns)
    return_shipments_df = pd.DataFrame(return_shipments)

    if not returns_df.empty:
        return_summary = returns_df.groupby("order_id").agg(
            returned_items_count=("return_id", "count"),
            refund_total_amount=("refund_amount", "sum"),
        ).reset_index()

        orders = orders.merge(return_summary, on="order_id", how="left", suffixes=("", "_ret"))
        orders["returned_items_count"] = orders["returned_items_count_ret"].fillna(orders["returned_items_count"]).fillna(0).astype(int)
        orders["refund_total_amount"] = orders["refund_total_amount_ret"].fillna(orders["refund_total_amount"]).fillna(0).round(2)
        orders["has_return"] = orders["returned_items_count"] > 0
        orders["return_status"] = np.where(orders["has_return"], "partial_or_full_return", orders["return_status"])
        orders = orders.drop(columns=[col for col in ["returned_items_count_ret", "refund_total_amount_ret"] if col in orders.columns])

    return returns_df, orders, return_shipments_df


def generate_sessions(
    n_sessions: int,
    customers: pd.DataFrame,
    persona_by_customer: dict[str, str],
    rng: np.random.Generator,
) -> pd.DataFrame:
    customer_ids = customers["customer_id"].tolist()
    weights = np.array([SESSION_WEIGHT_BY_PERSONA[persona_by_customer[cid]] for cid in customer_ids], dtype=float)
    weights = weights / weights.sum()

    rows = []
    for i in tqdm(range(1, n_sessions + 1), desc="Generating sessions"):
        session_id = make_id("sess", i)
        customer_id = str(rng.choice(customer_ids, p=weights))
        persona = persona_by_customer[customer_id]
        start_time = sample_past_datetime(rng, persona)
        duration = int(rng.integers(30, 1800))
        converted = bool(rng.random() < CONVERSION_RATE_BY_PERSONA[persona])
        pages_viewed = int(rng.integers(1, 6) + (rng.integers(3, 12) if converted else 0))

        rows.append(
            {
                "session_id": session_id,
                "customer_id": customer_id,
                "start_time": start_time,
                "end_time": start_time + timedelta(seconds=duration),
                "device_type": str(rng.choice(["desktop", "mobile", "tablet"], p=[0.45, 0.48, 0.07])),
                "traffic_source": str(rng.choice(["direct", "seo", "paid_ads", "email", "social"], p=[0.28, 0.25, 0.18, 0.17, 0.12])),
                "session_duration_seconds": duration,
                "pages_viewed": pages_viewed,
                "converted": converted,
                "created_at": start_time,
            }
        )

    return pd.DataFrame(rows)


def generate_support_tickets(
    n_tickets: int,
    customers: pd.DataFrame,
    persona_by_customer: dict[str, str],
    rng: np.random.Generator,
) -> pd.DataFrame:
    customer_ids = customers["customer_id"].tolist()
    weights = np.array([SUPPORT_WEIGHT_BY_PERSONA[persona_by_customer[cid]] for cid in customer_ids], dtype=float)
    weights = weights / weights.sum()

    templates = {
        "delivery": [
            "My parcel arrived late and I need help.",
            "The tracking link is not working.",
            "I received the wrong delivery update.",
        ],
        "refund": [
            "I am waiting for my refund.",
            "The refund amount does not match my order.",
            "I returned the product but did not receive confirmation.",
        ],
        "product_quality": [
            "The product does not match the description.",
            "The item seems defective.",
            "The product quality is below expectations.",
        ],
        "account": [
            "I cannot access my account.",
            "My email address should be updated.",
            "I want to change my marketing preferences.",
        ],
    }

    rows = []
    for i in tqdm(range(1, n_tickets + 1), desc="Generating support tickets"):
        customer_id = str(rng.choice(customer_ids, p=weights))
        persona = persona_by_customer[customer_id]
        category = str(rng.choice(list(templates.keys())))
        created_at = sample_past_datetime(rng, persona)
        priority = "high" if persona == "dissatisfied_customer" and rng.random() < 0.45 else str(rng.choice(["low", "medium", "high"], p=[0.45, 0.43, 0.12]))
        status = str(rng.choice(["open", "in_progress", "resolved", "closed"], p=[0.08, 0.12, 0.50, 0.30]))

        rows.append(
            {
                "ticket_id": make_id("tick", i),
                "customer_id": customer_id,
                "created_at": created_at,
                "category": category,
                "priority": priority,
                "status": status,
                "ticket_text": str(rng.choice(templates[category])),
                "resolution_time_hours": float(np.round(rng.uniform(1, 96), 2)),
                "satisfaction_score": float(np.round(rng.uniform(1.0, 3.0), 2)) if persona == "dissatisfied_customer" else float(np.round(rng.uniform(3.0, 5.0), 2)),
                "contains_personal_data": bool(rng.random() < 0.18),
                "moderation_status": str(rng.choice(["approved", "flagged", "pending"], p=[0.86, 0.04, 0.10])),
            }
        )

    return pd.DataFrame(rows)


def generate_reviews(
    n_reviews: int,
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    persona_by_customer: dict[str, str],
    rng: np.random.Generator,
) -> pd.DataFrame:
    eligible = order_items.merge(orders[["order_id", "customer_id", "order_datetime"]], on="order_id", how="inner")
    if eligible.empty:
        return pd.DataFrame()

    chosen_idx = rng.choice(eligible.index.values, size=min(n_reviews, len(eligible)), replace=False)
    rows = []

    positive_texts = [
        "Great product and fast delivery.",
        "Good value for money.",
        "Very satisfied with the purchase.",
        "Product matches the description.",
    ]
    negative_texts = [
        "The product did not meet expectations.",
        "Delivery was late and support was not helpful.",
        "Quality issue after a few days of use.",
        "I will probably not order this item again.",
    ]

    for i, idx in enumerate(tqdm(chosen_idx, desc="Generating reviews"), start=1):
        item = eligible.loc[idx]
        customer_id = str(item["customer_id"])
        persona = persona_by_customer[customer_id]
        rating = int(rng.choice(REVIEW_RATING_BY_PERSONA[persona]))
        review_text = str(rng.choice(negative_texts if rating <= 2 else positive_texts))
        review_date = pd.to_datetime(item["order_datetime"]).to_pydatetime() + timedelta(days=int(rng.integers(3, 45)))

        rows.append(
            {
                "review_id": make_id("rev", i),
                "customer_id": customer_id,
                "product_id": item["product_id"],
                "rating": rating,
                "review_text": review_text,
                "review_date": review_date,
                "moderation_status": str(rng.choice(["approved", "pending", "flagged"], p=[0.88, 0.10, 0.02])),
                "contains_personal_data": bool(rng.random() < 0.05),
            }
        )

    return pd.DataFrame(rows)


def generate_events(
    n_events: int,
    sessions: pd.DataFrame,
    products: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    if sessions.empty:
        return pd.DataFrame()

    session_records = sessions.to_dict("records")
    product_ids = products["product_id"].tolist()
    rows = []

    event_types = ["page_view", "product_view", "search", "add_to_cart", "remove_from_cart", "checkout_started", "purchase", "login", "logout"]
    base_probs = np.array([0.30, 0.24, 0.12, 0.12, 0.04, 0.07, 0.04, 0.04, 0.03], dtype=float)
    base_probs = base_probs / base_probs.sum()

    for i in tqdm(range(1, n_events + 1), desc="Generating raw events"):
        session = session_records[int(rng.integers(0, len(session_records)))]
        event_type = str(rng.choice(event_types, p=base_probs))
        session_start = pd.to_datetime(session["start_time"]).to_pydatetime()
        session_end = pd.to_datetime(session["end_time"]).to_pydatetime()
        event_timestamp = random_datetime_between(rng, session_start, session_end)

        product_id = None
        if event_type in ["product_view", "add_to_cart", "remove_from_cart", "checkout_started", "purchase"]:
            product_id = str(rng.choice(product_ids))

        raw_payload = {
            "event_id": make_id("evt", i),
            "event_type": event_type,
            "customer_id": session["customer_id"],
            "session_id": session["session_id"],
            "product_id": product_id,
            "raw_payload_version": "v1",
        }

        rows.append(
            {
                "event_id": make_id("evt", i),
                "customer_id": session["customer_id"],
                "session_id": session["session_id"],
                "event_type": event_type,
                "product_id": product_id,
                "event_timestamp": event_timestamp,
                "device_type": session["device_type"],
                "browser": str(rng.choice(["Chrome", "Safari", "Firefox", "Edge"], p=[0.55, 0.22, 0.13, 0.10])),
                "country": "France",
                "page_url": f"/{event_type.replace('_', '-')}",
                "referrer": str(rng.choice(["direct", "google", "newsletter", "instagram", "facebook"], p=[0.35, 0.30, 0.15, 0.12, 0.08])),
                "sales_channel": "mobile_app" if session["device_type"] == "mobile" and rng.random() < 0.45 else "web",
                "raw_payload": json.dumps(raw_payload),
                "created_at": event_timestamp,
            }
        )

    return pd.DataFrame(rows)


def generate_customer_consents(customers: pd.DataFrame) -> pd.DataFrame:
    rows = []
    consent_counter = 1

    consent_mapping = {
        "marketing_email": "marketing_consent",
        "analytics_tracking": "analytics_consent",
        "personalized_recommendation": "personalization_consent",
    }

    for _, customer in tqdm(customers.iterrows(), total=len(customers), desc="Generating consents"):
        for consent_type, source_column in consent_mapping.items():
            consent_date = pd.to_datetime(customer["registration_date"]).to_pydatetime() + timedelta(hours=1)
            rows.append(
                {
                    "consent_id": make_id("cons", consent_counter),
                    "customer_id": customer["customer_id"],
                    "consent_type": consent_type,
                    "consent_value": bool(customer[source_column]),
                    "consent_date": consent_date,
                    "source": "account_creation",
                    "withdrawal_date": None if bool(customer[source_column]) else consent_date + timedelta(days=30),
                    "created_at": consent_date,
                }
            )
            consent_counter += 1

    return pd.DataFrame(rows)


def build_customer_features(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    products: pd.DataFrame,
    returns: pd.DataFrame,
    sessions: pd.DataFrame,
    support_tickets: pd.DataFrame,
    reviews: pd.DataFrame,
) -> pd.DataFrame:
    customer_ids = customers["customer_id"].tolist()

    order_agg = orders.groupby("customer_id").agg(
        total_orders=("order_id", "count"),
        total_spent=("total_incl_tax", "sum"),
        avg_order_value=("total_incl_tax", "mean"),
        last_order=("order_datetime", "max"),
        discounted_orders=("discount_amount", lambda s: int((s.fillna(0) > 0).sum())),
    ).reset_index()

    return_agg = returns.groupby("customer_id").agg(
        returns_count=("return_id", "count")
    ).reset_index() if not returns.empty else pd.DataFrame(columns=["customer_id", "returns_count"])

    session_30d = sessions[pd.to_datetime(sessions["start_time"]) >= (NOW - timedelta(days=30))]
    session_agg = session_30d.groupby("customer_id").agg(
        session_count_30d=("session_id", "count"),
        pages_viewed_30d=("pages_viewed", "sum"),
        converted_30d=("converted", "sum"),
    ).reset_index()

    support_agg = support_tickets.groupby("customer_id").agg(
        support_tickets_count=("ticket_id", "count")
    ).reset_index() if not support_tickets.empty else pd.DataFrame(columns=["customer_id", "support_tickets_count"])

    review_agg = reviews.groupby("customer_id").agg(
        avg_rating_given=("rating", "mean")
    ).reset_index() if not reviews.empty else pd.DataFrame(columns=["customer_id", "avg_rating_given"])

    item_category = order_items.merge(orders[["order_id", "customer_id"]], on="order_id", how="left").merge(
        products[["product_id", "category"]], on="product_id", how="left"
    )
    preferred = (
        item_category.groupby(["customer_id", "category"]).size().reset_index(name="count")
        .sort_values(["customer_id", "count"], ascending=[True, False])
        .drop_duplicates("customer_id")
        [["customer_id", "category"]]
        .rename(columns={"category": "preferred_category"})
    )

    features = pd.DataFrame({"customer_id": customer_ids})
    for df in [order_agg, return_agg, session_agg, support_agg, review_agg, preferred]:
        features = features.merge(df, on="customer_id", how="left")

    features = features.merge(customers[["customer_id", "loyalty_status"]], on="customer_id", how="left")

    features["total_orders"] = features["total_orders"].fillna(0).astype(int)
    features["total_spent"] = features["total_spent"].fillna(0).round(2)
    features["avg_order_value"] = features["avg_order_value"].fillna(0).round(2)

    features["last_order"] = pd.to_datetime(features["last_order"])
    features["days_since_last_order"] = (pd.Timestamp(NOW) - features["last_order"]).dt.days
    features["days_since_last_order"] = features["days_since_last_order"].fillna(999).astype(int)
    features = features.drop(columns=["last_order"])

    features["returns_count"] = features["returns_count"].fillna(0).astype(int)
    features["return_rate"] = np.where(features["total_orders"] > 0, features["returns_count"] / features["total_orders"], 0).round(4)

    features["session_count_30d"] = features["session_count_30d"].fillna(0).astype(int)
    features["pages_viewed_30d"] = features["pages_viewed_30d"].fillna(0).astype(int)
    features["converted_30d"] = features["converted_30d"].fillna(0).astype(int)
    features["cart_abandon_rate"] = np.where(
        features["session_count_30d"] > 0,
        1 - (features["converted_30d"] / features["session_count_30d"]),
        1.0,
    ).round(4)
    features = features.drop(columns=["converted_30d"])

    features["support_tickets_count"] = features["support_tickets_count"].fillna(0).astype(int)
    features["avg_rating_given"] = features["avg_rating_given"].fillna(0).round(2)

    features["discounted_orders"] = features["discounted_orders"].fillna(0).astype(int)
    features["discount_usage_rate"] = np.where(
        features["total_orders"] > 0,
        features["discounted_orders"] / features["total_orders"],
        0,
    ).round(4)
    features = features.drop(columns=["discounted_orders"])

    features["preferred_category"] = features["preferred_category"].fillna("unknown")
    features["feature_date"] = NOW.date()

    ordered_columns = [
        "customer_id",
        "total_orders",
        "total_spent",
        "avg_order_value",
        "days_since_last_order",
        "return_rate",
        "cart_abandon_rate",
        "session_count_30d",
        "pages_viewed_30d",
        "support_tickets_count",
        "avg_rating_given",
        "discount_usage_rate",
        "preferred_category",
        "loyalty_status",
        "feature_date",
    ]

    return features[ordered_columns]


def update_customer_last_interaction(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    sessions: pd.DataFrame,
    support_tickets: pd.DataFrame,
) -> pd.DataFrame:
    interactions = []

    if not orders.empty:
        interactions.append(orders[["customer_id", "order_datetime"]].rename(columns={"order_datetime": "interaction_at"}))
    if not sessions.empty:
        interactions.append(sessions[["customer_id", "start_time"]].rename(columns={"start_time": "interaction_at"}))
    if not support_tickets.empty:
        interactions.append(support_tickets[["customer_id", "created_at"]].rename(columns={"created_at": "interaction_at"}))

    if not interactions:
        return customers

    all_interactions = pd.concat(interactions, ignore_index=True)
    all_interactions["interaction_at"] = pd.to_datetime(all_interactions["interaction_at"])
    last_interaction = all_interactions.groupby("customer_id")["interaction_at"].max().reset_index()

    customers = customers.drop(columns=["last_interaction_at"]).merge(last_interaction, on="customer_id", how="left")
    customers = customers.rename(columns={"interaction_at": "last_interaction_at"})
    return customers


def write_csv(df: pd.DataFrame, output_dir: Path, filename: str) -> None:
    path = output_dir / filename
    df.to_csv(path, index=False)
    print(f"Wrote {len(df):>8} rows -> {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate RetailFlow synthetic dataset.")
    parser.add_argument("--profile", default="small", choices=["small", "medium", "large"], help="Dataset size profile.")
    parser.add_argument("--config", default="data_generator/config.yaml", help="Path to config YAML.")
    args = parser.parse_args()

    config = load_config(args.config)
    profile = config["dataset_profiles"][args.profile]
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    seed = int(config.get("random_seed", 42))
    rng = np.random.default_rng(seed)
    fake = Faker("fr_FR")
    Faker.seed(seed)

    print(f"Generating RetailFlow dataset with profile='{args.profile}'")
    print(json.dumps(profile, indent=2))

    customers, persona_by_customer, preferred_category_by_customer = generate_customers(
        profile["customers"], config["personas"], fake, rng
    )
    suppliers = generate_suppliers(profile["suppliers"], fake, rng)
    products = generate_products(profile["products"], suppliers, fake, rng)

    orders, order_items, payments, shipments = generate_orders_and_related(
        profile["orders"],
        profile["order_items"],
        customers,
        products,
        persona_by_customer,
        preferred_category_by_customer,
        rng,
    )

    returns, orders, return_shipments = generate_returns(
        profile["returns"],
        orders,
        order_items,
        products,
        persona_by_customer,
        rng,
    )

    if not return_shipments.empty:
        shipments = pd.concat([shipments, return_shipments], ignore_index=True)

    sessions = generate_sessions(profile["sessions"], customers, persona_by_customer, rng)
    support_tickets = generate_support_tickets(profile["support_tickets"], customers, persona_by_customer, rng)
    reviews = generate_reviews(profile["reviews"], orders, order_items, persona_by_customer, rng)
    events = generate_events(profile["events"], sessions, products, rng)
    customer_consents = generate_customer_consents(customers)

    customers = update_customer_last_interaction(customers, orders, sessions, support_tickets)

    customer_features = build_customer_features(
        customers,
        orders,
        order_items,
        products,
        returns,
        sessions,
        support_tickets,
        reviews,
    )

    debug_personas = pd.DataFrame(
        [
            {
                "customer_id": customer_id,
                "hidden_persona": persona_by_customer[customer_id],
                "preferred_category_seed": preferred_category_by_customer[customer_id],
            }
            for customer_id in persona_by_customer.keys()
        ]
    )

    write_csv(debug_personas, output_dir, "_debug_personas.csv")


    write_csv(customers, output_dir, "customers.csv")
    write_csv(suppliers, output_dir, "suppliers.csv")
    write_csv(products, output_dir, "products.csv")
    write_csv(orders, output_dir, "orders.csv")
    write_csv(order_items, output_dir, "order_items.csv")
    write_csv(payments, output_dir, "payments.csv")
    write_csv(shipments, output_dir, "shipments.csv")
    write_csv(returns, output_dir, "returns.csv")
    write_csv(sessions, output_dir, "sessions.csv")
    write_csv(support_tickets, output_dir, "support_tickets.csv")
    write_csv(reviews, output_dir, "reviews.csv")
    write_csv(events, output_dir, "events.csv")
    write_csv(customer_consents, output_dir, "customer_consents.csv")
    write_csv(customer_features, output_dir, "customer_features.csv")

    print("Dataset generation completed successfully.")


if __name__ == "__main__":
    main()
