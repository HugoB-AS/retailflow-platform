from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://retailflow:retailflow@localhost:5432/retailflow_db",
)

DATA_DIR = Path(os.getenv("DATA_DIR", "data/raw"))


LOAD_PLAN = [
    ("core", "suppliers", "suppliers.csv"),
    ("core", "products", "products.csv"),
    ("core", "customers", "customers.csv"),
    ("core", "orders", "orders.csv"),
    ("core", "order_items", "order_items.csv"),
    ("core", "payments", "payments.csv"),
    ("core", "shipments", "shipments.csv"),
    ("core", "returns", "returns.csv"),
    ("core", "sessions", "sessions.csv"),
    ("core", "support_tickets", "support_tickets.csv"),
    ("core", "reviews", "reviews.csv"),
    ("raw", "events", "events.csv"),
    ("governance", "customer_consents", "customer_consents.csv"),
    ("analytics", "customer_features", "customer_features.csv"),
]


TRUNCATE_ORDER = [
    "analytics.customer_features",
    "analytics.customer_segments",
    "analytics.ml_predictions",
    "analytics.daily_sales",
    "governance.customer_consents",
    "governance.data_quality_logs",
    "governance.dead_letter_events",
    "governance.retention_actions_log",
    "raw.events",
    "core.reviews",
    "core.support_tickets",
    "core.sessions",
    "core.returns",
    "core.shipments",
    "core.payments",
    "core.order_items",
    "core.orders",
    "core.products",
    "core.suppliers",
    "core.customers",
]


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_csv(path)

    # Convert NaN to None for cleaner SQL inserts.
    df = df.where(pd.notnull(df), None)

    return df


def truncate_tables(engine) -> None:
    print("Truncating existing data...")
    with engine.begin() as conn:
        for table in TRUNCATE_ORDER:
            conn.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))


def load_table(engine, schema: str, table: str, filename: str) -> None:
    path = DATA_DIR / filename
    df = read_csv(path)

    print(f"Loading {len(df):>8} rows -> {schema}.{table}")

    df.to_sql(
        name=table,
        con=engine,
        schema=schema,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )


def main() -> None:
    print(f"Using DATABASE_URL={DATABASE_URL}")
    print(f"Using DATA_DIR={DATA_DIR}")

    engine = create_engine(DATABASE_URL)

    truncate_tables(engine)

    for schema, table, filename in LOAD_PLAN:
        load_table(engine, schema, table, filename)

    print("PostgreSQL load completed successfully.")


if __name__ == "__main__":
    main()
