"""
dashboard.py
------------

Generate simple charts from the processed taxi data.  This module uses
Matplotlib to create static PNG images that summarise daily trip
volumes and trip distance distributions.  Although the example is
rudimentary, it demonstrates how one might begin to explore and
visualise the data before handing it off to a BI tool.

Usage:

.. code-block:: bash

   python src/dashboard.py \
       --cleaned data/processed/cleaned_trips.csv \
       --summary data/processed/trip_summary.csv \
       --output-dir reports/plots
"""

import argparse
import os
from datetime import datetime

import matplotlib

# Use Agg backend for non‑interactive environments
matplotlib.use("Agg")  # type: ignore
import matplotlib.pyplot as plt


def try_import_pandas():
    try:
        import pandas as pd  # type: ignore
        return pd
    except ImportError:
        return None


def build_charts(cleaned_csv: str, summary_csv: str, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    pd = try_import_pandas()
    if pd is None:
        raise RuntimeError("pandas is required to build charts; please install pandas and try again.")
    # Read summary data for time series chart
    summary_df = pd.read_csv(summary_csv, parse_dates=["pickup_date"])
    # Sum across vendors per day
    daily = summary_df.groupby("pickup_date").agg(trips_count=("trips_count", "sum"))
    # Plot daily trip counts
    plt.figure(figsize=(10, 5))
    plt.plot(daily.index, daily["trips_count"], marker="o")
    plt.title("Daily Trip Volume (all vendors)")
    plt.xlabel("Date")
    plt.ylabel("Number of Trips")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    trips_plot_path = os.path.join(output_dir, "daily_trip_volume.png")
    plt.savefig(trips_plot_path)
    plt.close()
    # Read cleaned data for distribution charts
    cleaned_df = pd.read_csv(cleaned_csv)
    # Histogram of trip distances
    plt.figure(figsize=(8, 4))
    cleaned_df["trip_distance"].hist(bins=50, color="skyblue", edgecolor="black")
    plt.title("Distribution of Trip Distances")
    plt.xlabel("Trip Distance (miles)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    dist_plot_path = os.path.join(output_dir, "trip_distance_distribution.png")
    plt.savefig(dist_plot_path)
    plt.close()
    # Histogram of fare amounts
    plt.figure(figsize=(8, 4))
    cleaned_df["fare_amount"].hist(bins=50, color="salmon", edgecolor="black")
    plt.title("Distribution of Fare Amounts")
    plt.xlabel("Fare Amount (USD)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    fare_plot_path = os.path.join(output_dir, "fare_amount_distribution.png")
    plt.savefig(fare_plot_path)
    plt.close()
    print(f"[INFO] Saved charts to {output_dir}")


def main(args: argparse.Namespace) -> None:
    build_charts(args.cleaned, args.summary, args.output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate charts from processed taxi data.")
    parser.add_argument(
        "--cleaned",
        type=str,
        default="data/processed/cleaned_trips.csv",
        help="Path to the cleaned trips CSV file",
    )
    parser.add_argument(
        "--summary",
        type=str,
        default="data/processed/trip_summary.csv",
        help="Path to the trip summary CSV file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports/plots",
        help="Directory to store the generated charts",
    )
    args = parser.parse_args()
    main(args)