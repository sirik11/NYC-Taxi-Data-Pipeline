"""
taxi_data_dag.py
----------------

Example Apache Airflow DAG for orchestrating the NYC taxi data pipeline.
This DAG is not executed in the repository by default; it is provided
for illustrative purposes.  To run it, copy this file into your
Airflow DAGs directory, ensure that Airflow can access the scripts in
the `src/` folder and set up any required connections or variables.

The DAG consists of four tasks:

1. **ingest_data** – calls ``data_ingestion.py`` to download or
   generate raw data.
2. **process_data** – calls ``data_processing.py`` to clean and
   aggregate the raw data.
3. **load_to_db** – calls ``database_loader.py`` to load the
   processed data into a SQLite (or other) database.
4. **create_charts** – calls ``dashboard.py`` to generate charts.

These tasks run sequentially.  In a production environment you might
configure retries, notifications and sensors around these tasks.
"""

from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator


REPO_ROOT = Path(__file__).resolve().parents[1]

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}


with DAG(
    dag_id="taxi_data_pipeline",
    description="NYC Taxi data pipeline",
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args=default_args,
) as dag:
    ingest_data = BashOperator(
        task_id="ingest_data",
        bash_command=f"python {REPO_ROOT}/src/data_ingestion.py --output {REPO_ROOT}/data/raw/yellow_tripdata_2025-01.csv",
    )
    process_data = BashOperator(
        task_id="process_data",
        bash_command=f"python {REPO_ROOT}/src/data_processing.py --input {REPO_ROOT}/data/raw/yellow_tripdata_2025-01.csv",
    )
    load_to_db = BashOperator(
        task_id="load_to_db",
        bash_command=(
            f"python {REPO_ROOT}/src/database_loader.py "
            f"--trips {REPO_ROOT}/data/processed/cleaned_trips.csv "
            f"--summary {REPO_ROOT}/data/processed/trip_summary.csv "
            f"--db {REPO_ROOT}/database/taxi_trips.db"
        ),
    )
    create_charts = BashOperator(
        task_id="create_charts",
        bash_command=(
            f"python {REPO_ROOT}/src/dashboard.py "
            f"--cleaned {REPO_ROOT}/data/processed/cleaned_trips.csv "
            f"--summary {REPO_ROOT}/data/processed/trip_summary.csv "
            f"--output-dir {REPO_ROOT}/reports/plots"
        ),
    )

    ingest_data >> process_data >> load_to_db >> create_charts