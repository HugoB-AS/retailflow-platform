import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://retailflow:retailflow@localhost:5432/retailflow_db",
)


def get_engine():
    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        future=True,
    )


def get_connection():
    engine = get_engine()
    return engine.connect()


engine = get_engine()