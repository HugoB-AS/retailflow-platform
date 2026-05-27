from datetime import timedelta
import pendulum

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "retailflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="ml_retraining",
    description="Retrain RetailFlow ML models, refresh predictions, and generate lightweight ML monitoring reports.",
    schedule="@weekly",
    start_date=pendulum.datetime(2026, 5, 1, tz="UTC"),
    catchup=False,
    default_args=default_args,
    tags=["retailflow", "ml", "ai", "monitoring"],
) as dag:

    train_churn = BashOperator(
        task_id="train_churn_model",
        bash_command="cd /opt/airflow && python -m ml.src.train_churn",
    )

    train_segmentation = BashOperator(
        task_id="train_segmentation_model",
        bash_command="cd /opt/airflow && python -m ml.src.train_segmentation",
    )

    train_clv = BashOperator(
        task_id="train_clv_model",
        bash_command="cd /opt/airflow && python -m ml.src.train_clv",
    )

    refresh_predictions = BashOperator(
        task_id="refresh_ml_predictions",
        bash_command="cd /opt/airflow && python -m ml.src.predict",
    )

    evaluate_drift = BashOperator(
        task_id="evaluate_lightweight_drift",
        bash_command="cd /opt/airflow && python -m ml.src.evaluate_drift",
    )

    [train_churn, train_segmentation, train_clv] >> refresh_predictions >> evaluate_drift
