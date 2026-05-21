from datetime import timedelta
import pendulum

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

POSTGRES_CONN_ID = "retailflow_postgres"

default_args = {
    "owner": "retailflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

@dag(
    dag_id="daily_data_quality",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 5, 1, tz="UTC"),
    catchup=False,
    default_args=default_args,
    tags=["retailflow", "quality"],
)
def daily_data_quality():

    @task
    def check_connection():
        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        result = hook.get_first("SELECT 1;")
        return result

    @task
    def count_dead_letters():
        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        row = hook.get_first("""
            SELECT COUNT(*)
            FROM governance.dead_letter_events;
        """)
        return row[0]

    check_connection() >> count_dead_letters()

daily_data_quality()
