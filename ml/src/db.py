import os

from sqlalchemy import create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://retailflow:retailflow@localhost:5432/retailflow_db",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
