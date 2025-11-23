# NYC Taxi Data Engineering Pipeline Project

This project demonstrates how to build a complete data engineering pipeline — from ingesting raw data to generating insights — using publicly available taxi‑trip data.  It is designed as an end‑to‑end showcase of typical data‑engineering tasks and tooling.  The pipeline can be run locally, but the repository also includes examples of how to deploy it in the cloud with orchestration and infrastructure‑as‑code (Terraform) to highlight production‑ready patterns.

## Overview

The goal is to build a reusable pipeline for processing New York City taxi trip data.  The pipeline performs the following high‑level stages:

1. **Data ingestion** – raw trip data are downloaded from the official Taxi & Limousine Commission data feed or generated synthetically for local testing.  If a remote download is desired, the script pulls monthly Parquet files from the TLC website and converts them to a CSV format for easier manipulation.  When running in a restricted environment or when Parquet dependencies are unavailable, the script falls back to generating a synthetic dataset that mimics the schema of the real taxi data.  The resulting dataset is stored in `data/raw`.
2. **Data processing (ETL)** – the raw data are cleaned and enriched.  In this step the pipeline removes records with missing or impossible values, derives additional columns (such as trip duration), and aggregates metrics at the daily and vendor‑level.  The processed dataset is saved in `data/processed` as a CSV file.
3. **Data warehouse loading** – using SQLite as a lightweight relational database, the processed data are loaded into a local database.  This step illustrates how you would load data into a warehouse such as BigQuery or Snowflake.  The database lives in the `database/` directory and contains two tables: a detailed trips table and an aggregated summary table.
4. **Analytics and visualization** – basic dashboards are generated to visualize trends in trip counts, distances and fares.  Charts are created with Matplotlib and stored in `reports/plots`.  Although this project uses static images, the same code can be adapted to feed BI tools such as Tableau, Looker or Power BI.
5. **Orchestration (Airflow)** – an example Airflow DAG is included in the `airflow/` folder.  When placed inside an Airflow environment, the DAG orchestrates each stage of the pipeline — ingestion, processing, loading and visualization — as individual tasks.
6. **Infrastructure as code (Terraform)** – the `terraform/` directory contains a minimal Terraform configuration showing how you might provision AWS resources (an S3 bucket, an EMR cluster and an RDS database) for a production deployment of this pipeline.  These scripts are illustrative only and require valid AWS credentials to run.

The repository emphasises reproducibility and clarity.  Every step is encapsulated in a Python script under `src/` so that it can be run independently or orchestrated by Airflow.

## Prerequisites

* **Python 3.9+** – the scripts rely only on built‑in Python libraries (`csv`, `datetime`, `sqlite3`, `random`, etc.) and `matplotlib`.  If you wish to process real Parquet data you will need the optional `pyarrow` library installed.
* **Matplotlib** – used to generate the charts.  It is included in the default environment on most systems but can be installed with `pip install matplotlib` if required.
* **SQLite** – included in the Python standard library via the `sqlite3` module.
* Optional: **Apache Airflow** and **Terraform** if you want to run the orchestration and infrastructure examples.

## Repository structure

```
data_engineering_project/
├── README.md               – this file
├── data/
│   ├── raw/                – raw input data (downloaded or synthetic)
│   └── processed/          – cleaned and aggregated data
├── database/
│   └── taxi_trips.db       – SQLite database created by the loader script
├── reports/
│   └── plots/              – charts generated from the processed data
├── diagrams/
│   └── architecture_diagram.png – visual overview of the pipeline
├── src/
│   ├── data_ingestion.py   – download or generate raw data
│   ├── data_processing.py  – clean and aggregate data
│   ├── database_loader.py  – load processed data into SQLite
│   ├── dashboard.py        – create charts from the data
│   └── pipeline.py         – orchestrate all steps end to end
├── airflow/
│   └── taxi_data_dag.py    – example Airflow DAG
├── terraform/
│   ├── main.tf             – sample Terraform configuration
│   └── variables.tf        – variable definitions for Terraform
├── requirements.txt        – Python dependencies
└── .gitignore              – files to ignore in version control
```

## Getting started

1. **Clone the repository**

   ```bash
   git clone https://github.com/your‑username/nyc‑taxi‑data‑pipeline.git
   cd nyc‑taxi‑data‑pipeline/data_engineering_project
   ```

2. **Install dependencies** (optional)

   The scripts rely only on Python’s standard library and Matplotlib.  If you plan to process Parquet files directly, install `pyarrow`:

   ```bash
   pip install matplotlib pyarrow
   ```

3. **Run the pipeline end‑to‑end**

   Execute the pipeline driver script.  It will download or generate raw data, perform the ETL process, load the results into a SQLite database and produce charts in the `reports/plots` folder.

   ```bash
   python src/pipeline.py
   ```

   If the environment cannot download the TLC Parquet data or lacks the `pyarrow` dependency, the ingestion script will automatically generate a synthetic dataset that mirrors the schema of the real taxi data.  You can also force synthetic data generation by setting the `--generate-synthetic` flag when invoking the ingestion script.

4. **Explore the results**

   * Inspect the processed CSV file in `data/processed/` to see the aggregated metrics.
   * Query the SQLite database in `database/taxi_trips.db` using any SQLite client.
   * View the charts in `reports/plots`.  They provide quick insights into trip volume over time and the distribution of trip distances and fares.

5. **Optional: Run with Airflow**

   If you have Airflow installed and configured, copy the DAG file `airflow/taxi_data_dag.py` into your Airflow DAGs folder.  Start the Airflow scheduler and webserver, then trigger the `taxi_data_pipeline` DAG from the UI.  Each task corresponds to one of the scripts in `src/`.

6. **Optional: Deploy to AWS with Terraform**

   The `terraform/` directory contains a simplified Terraform configuration that provisions:

   * An S3 bucket for storing raw and processed data.
   * An EMR cluster to run Spark jobs (for large‑scale processing).
   * An RDS PostgreSQL instance to act as a data warehouse.

   Before running Terraform, set the required variables in `terraform/variables.tf` and initialise the working directory with `terraform init`.  Then run `terraform apply` to provision the resources.  **Note:** Running Terraform scripts requires valid AWS credentials and may incur costs.

## Presenting this project

When presenting this project in an interview, consider the following talking points:

* **Problem statement:** Explain that New York City’s Taxi & Limousine Commission publishes high‑volume trip data and that a data engineer must build a pipeline to make this data useful for analysts.  Emphasise the business value of understanding trends in ride volume, trip distances and revenue.
* **Architecture overview:** Show the architecture diagram (provided in `diagrams/architecture_diagram.png`) to give a high‑level view of the pipeline components.  Walk through each stage: ingestion, processing, data warehouse loading and analytics.  Mention how orchestration and IaC play a role in real‑world deployments.
* **Challenges and decisions:** Discuss why Parquet is chosen for the raw data format (efficient storage and compression) and why the example falls back to CSV for ease of local use.  Talk about handling missing values, validating data quality and designing schemas for both the raw and transformed data.
* **Scaling considerations:** Note that although the example uses SQLite, the same pipeline can be directed to Snowflake, BigQuery or Redshift.  Describe how the Terraform scripts illustrate the infrastructure required for a cloud deployment and how Airflow would orchestrate the workflow.
* **Further enhancements:** Suggest extensions such as adding streaming ingestion via Kafka, integrating data quality tools like Great Expectations, or implementing a CI/CD pipeline using GitHub Actions.  You can also mention the possibility of building dashboards in BI tools for interactive analysis.

By explaining both the technical details and the strategic considerations, you will demonstrate a comprehensive understanding of what it means to build and operate reliable data pipelines.
