"""
pipeline.py
-----------

This script orchestrates the complete data pipeline end to end.  It
invokes the ingestion, processing, loading and dashboard stages in
sequence.  It is designed to be executed from the root of the
repository.  Running this script will produce a SQLite database and
several chart images in the `reports/plots` directory.

Usage:

.. code-block:: bash

   python src/pipeline.py

Optionally you can override the number of synthetic records or force
synthetic data generation by modifying the arguments in the ``main``
function below.
"""

import subprocess
import sys
from pathlib import Path


def run_stage(description: str, command: list[str]) -> None:
    print(f"[PIPELINE] {description}…")
    result = subprocess.run([sys.executable] + command)
    if result.returncode != 0:
        raise RuntimeError(f"Stage '{description}' failed with exit code {result.returncode}")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    data_raw = repo_root / "data" / "raw" / "yellow_tripdata_2025-01.csv"
    data_processed = repo_root / "data" / "processed"
    database_file = repo_root / "database" / "taxi_trips.db"
    plots_dir = repo_root / "reports" / "plots"
    # Stage 1: Ingestion (download or generate synthetic)
    run_stage(
        "Ingesting data",
        [str((repo_root / "src" / "data_ingestion.py")), "--output", str(data_raw)],
    )
    # Stage 2: Processing (clean and aggregate)
    run_stage(
        "Processing data",
        [str((repo_root / "src" / "data_processing.py")), "--input", str(data_raw)],
    )
    # Stage 3: Load into SQLite
    run_stage(
        "Loading data into SQLite",
        [
            str((repo_root / "src" / "database_loader.py")),
            "--trips",
            str(data_processed / "cleaned_trips.csv"),
            "--summary",
            str(data_processed / "trip_summary.csv"),
            "--db",
            str(database_file),
        ],
    )
    # Stage 4: Generate dashboard
    run_stage(
        "Generating charts",
        [
            str((repo_root / "src" / "dashboard.py")),
            "--cleaned",
            str(data_processed / "cleaned_trips.csv"),
            "--summary",
            str(data_processed / "trip_summary.csv"),
            "--output-dir",
            str(plots_dir),
        ],
    )
    print("[PIPELINE] Pipeline completed successfully.")


if __name__ == "__main__":
    main()