Motivation
The New York City Taxi & Limousine Commission publishes detailed trip records every month
nyc.gov
. These datasets include pick‑up and drop‑off times, passenger counts, trip distances, fares and payment types, and in 2025 they even introduced a congestion pricing fee column
nyc.gov
. Because the data is stored in large Parquet files
nyc.gov
, working with it requires some engineering know‑how.
Given my background in AWS, GCP, infrastructure automation and big‑data processing, I wanted to create a portfolio project that demonstrates my ability to build an end‑to‑end data pipeline on a realistic dataset. The NYC taxi data was the perfect choice because it’s public, voluminous and rich with temporal and financial attributes. Building a pipeline around it allowed me to showcase data ingestion, transformation, warehousing, orchestration, infrastructure‑as‑code and basic analytics.
What I built
Data ingestion – I wrote a script to download the January 2025 yellow‑cab Parquet file from the TLC’s official feed. Because I knew some environments wouldn’t have network access or the required Parquet libraries, I added a fallback that generates a synthetic dataset mimicking the real schema. This ensures the pipeline runs anywhere.
Data processing – I cleaned the raw data by removing invalid rows (e.g., trips with non‑positive distances) and derived a trip_duration_minutes column. I aggregated metrics such as number of trips, average passenger count, average distance, total fare amount and average duration by day and vendor. When pandas was available I used it; otherwise I implemented the logic with pure Python for portability.
Data warehousing – To simulate a warehouse, I loaded the cleaned and aggregated data into a SQLite database with two tables: trips (detailed records) and trip_summary (aggregated metrics). The structure is easily adaptable to a warehouse like Snowflake, Redshift or BigQuery.
Analytics and visualisation – Using Matplotlib, I produced charts showing daily trip volumes, the distribution of trip distances and the distribution of fare amounts. These visualisations help communicate key insights derived from the data.
Orchestration and IaC – I created an Airflow DAG to orchestrate the ingestion, processing, loading and visualisation steps, and I drafted Terraform scripts to provision an S3 bucket, an EMR cluster and an RDS database on AWS. Although I didn’t execute these in this environment, including them demonstrates my familiarity with production‑grade orchestration and cloud deployment.
Why I designed it this way
Realism and reproducibility – Targeting a public dataset and handling Parquet files mirrors real‑world challenges, while the synthetic fallback ensures the project can run in any environment.
Modularity – Each stage (ingest, process, load, visualise) lives in its own script, making the pipeline easier to understand, test and extend.
Minimal dependencies – I relied mostly on Python’s standard library and Matplotlib, with pandas and pyarrow being optional. This increases portability.
Cloud‑readiness – Including an Airflow DAG and Terraform scripts shows how the pipeline can be orchestrated and deployed in the cloud.
What I achieved
With this project I proved that I can ingest large, semi‑structured datasets, clean and transform them, design appropriate schemas, automate loading into a warehouse, produce meaningful analytics and communicate the results through charts and documentation. It also demonstrates my ability to use orchestration and infrastructure tools to transition from a local proof‑of‑concept to a cloud‑ready pipeline.

