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
    dag_id="daily_sales_aggregation",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 5, 1, tz="UTC"),
    catchup=False,
    default_args=default_args,
    tags=["retailflow", "analytics", "sales"],
)
def daily_sales_aggregation():

    @task
    def refresh_daily_sales():
        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

        sql = """
            INSERT INTO analytics.daily_sales (
                sales_date,
                orders_count,
                revenue_excl_tax,
                tax_amount,
                revenue_incl_tax,
                avg_order_value,
                returns_count,
                refund_amount,
                created_at
            )
            SELECT
                DATE(o.order_datetime) AS sales_date,
                COUNT(DISTINCT o.order_id) AS orders_count,
                COALESCE(SUM(o.total_excl_tax), 0)::NUMERIC(14,2) AS revenue_excl_tax,
                COALESCE(SUM(o.tax_amount), 0)::NUMERIC(14,2) AS tax_amount,
                COALESCE(SUM(o.total_incl_tax), 0)::NUMERIC(14,2) AS revenue_incl_tax,
                COALESCE(AVG(o.total_incl_tax), 0)::NUMERIC(12,2) AS avg_order_value,
                COALESCE(COUNT(DISTINCT r.return_id), 0)::INTEGER AS returns_count,
                COALESCE(SUM(r.refund_amount), 0)::NUMERIC(14,2) AS refund_amount,
                CURRENT_TIMESTAMP AS created_at
            FROM core.orders o
            LEFT JOIN core.returns r
                ON o.order_id = r.order_id
            GROUP BY DATE(o.order_datetime)
            ON CONFLICT (sales_date)
            DO UPDATE SET
                orders_count = EXCLUDED.orders_count,
                revenue_excl_tax = EXCLUDED.revenue_excl_tax,
                tax_amount = EXCLUDED.tax_amount,
                revenue_incl_tax = EXCLUDED.revenue_incl_tax,
                avg_order_value = EXCLUDED.avg_order_value,
                returns_count = EXCLUDED.returns_count,
                refund_amount = EXCLUDED.refund_amount,
                created_at = CURRENT_TIMESTAMP;
        """

        hook.run(sql)

    @task
    def validate_daily_sales():
        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

        row = hook.get_first("""
            SELECT COUNT(*)
            FROM analytics.daily_sales;
        """)

        return {"daily_sales_rows": row[0]}

    refresh_daily_sales() >> validate_daily_sales()


daily_sales_aggregation()
