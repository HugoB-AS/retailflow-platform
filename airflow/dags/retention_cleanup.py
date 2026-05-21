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
    dag_id="retention_cleanup",
    schedule="@weekly",
    start_date=pendulum.datetime(2026, 5, 1, tz="UTC"),
    catchup=False,
    default_args=default_args,
    tags=["retailflow", "governance", "gdpr", "retention"],
)
def retention_cleanup():

    @task
    def find_expired_customers():
        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

        sql = """
            SELECT
                c.customer_id
            FROM core.customers c
            JOIN governance.data_retention_policies p
                ON p.policy_id = 'ret_001'
            WHERE c.is_anonymized = FALSE
              AND c.last_interaction_at IS NOT NULL
              AND c.last_interaction_at < NOW() - (p.retention_days || ' days')::INTERVAL
            LIMIT 50;
        """

        rows = hook.get_records(sql)
        return [row[0] for row in rows]

    @task
    def anonymize_customers(customer_ids: list[str]):
        if not customer_ids:
            return {"anonymized_customers": 0}

        hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

        for customer_id in customer_ids:
            hook.run(
                """
                UPDATE core.customers
                SET
                    first_name = 'ANONYMIZED',
                    last_name = 'ANONYMIZED',
                    email = CONCAT('deleted_', customer_id, '@retailflow.local'),
                    phone_number = NULL,
                    birth_date = NULL,
                    gender = NULL,
                    city = NULL,
                    postal_code = NULL,
                    marketing_consent = FALSE,
                    analytics_consent = FALSE,
                    personalization_consent = FALSE,
                    account_status = 'anonymized',
                    is_anonymized = TRUE,
                    anonymized_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE customer_id = %s
                  AND is_anonymized = FALSE;
                """,
                parameters=(customer_id,),
            )

            hook.run(
                """
                INSERT INTO governance.retention_actions_log (
                    action_id,
                    policy_id,
                    table_name,
                    record_id,
                    action_type,
                    action_status,
                    executed_at,
                    executed_by,
                    details
                )
                VALUES (
                    CONCAT('retact_', SUBSTRING(MD5(RANDOM()::TEXT), 1, 12)),
                    'ret_001',
                    'core.customers',
                    %s,
                    'anonymize',
                    'success',
                    CURRENT_TIMESTAMP,
                    'airflow_retention_cleanup',
                    'Customer personal data anonymized according to retention policy ret_001'
                );
                """,
                parameters=(customer_id,),
            )

        return {"anonymized_customers": len(customer_ids)}

    expired_customers = find_expired_customers()
    anonymize_customers(expired_customers)


retention_cleanup()
