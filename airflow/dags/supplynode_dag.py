from datetime import timedelta

import pendulum
from airflow.sdk import dag, task


def dag_failure_callback(context):
    """Handle failures at the DAG level."""
    print("SupplyNode pipeline failed.")
    print(f"DAG run: {context['dag_run'].run_id}")


@dag(
    dag_id="supplynode_pipeline",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    on_failure_callback=dag_failure_callback,
    tags=["supplynode", "inventory"],
)
def supplynode_pipeline():

    @task.python
    def load_data_task():
        print("Loading SupplyNode data...")
        return "data_loaded"

    @task.python
    def calculate_kpis_task(data_status):
        print(f"Calculating KPIs after: {data_status}")
        return "kpis_calculated"

    @task.python
    def stockout_task(kpi_status):
        print(f"Running stockout analysis after: {kpi_status}")
        return "stockout_complete"

    @task.python
    def deadstock_task(kpi_status):
        print(f"Running deadstock analysis after: {kpi_status}")
        return "deadstock_complete"

    @task.python
    def reorder_task(stockout_status):
        print(f"Running reorder analysis after: {stockout_status}")
        return "reorder_complete"

    @task.python
    def composite_risk_task(reorder_status, deadstock_status):
        print(
            "Calculating composite risk from "
            f"{reorder_status} and {deadstock_status}"
        )
        return "risk_calculated"

    @task.python
    def claude_analysis_task(risk_status):
        print(f"Running Claude analysis after: {risk_status}")
        return "analysis_complete"

    @task.python
    def save_alert_task(analysis_status):
        print(f"Saving alert after: {analysis_status}")
        return "alert_saved"

    # Pipeline
    data = load_data_task()

    kpis = calculate_kpis_task(data)

    stockout = stockout_task(kpis)
    deadstock = deadstock_task(kpis)

    reorder = reorder_task(stockout)

    risk = composite_risk_task(
        reorder,
        deadstock,
    )

    analysis = claude_analysis_task(risk)

    save_alert_task(analysis)


supplynode_pipeline()