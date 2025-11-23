"""
data_ingestion.py
------------------

This module downloads New York City taxi trip data (if possible) or
generates a synthetic dataset that mirrors the real TLC schema.  The
generated or downloaded data are stored in CSV format under the
``data/raw`` directory.  Other parts of the pipeline operate on this
CSV file.

Because some environments restrict network access and the ability to
install third‑party packages for reading Parquet files, this script is
defensive.  It attempts to download Parquet data and convert it to
CSV when possible, but gracefully falls back to generating synthetic
data when either the download fails or the required Parquet
dependencies are missing.

Usage:

.. code-block:: bash

   python src/data_ingestion.py \
       --url https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet \
       --output data/raw/yellow_tripdata_2025-01.csv

   # Generate a synthetic dataset instead of downloading
   python src/data_ingestion.py --generate-synthetic --num-records 50000

"""

import argparse
import csv
import datetime
import os
import random
import sys
import time


def try_import_pandas():
    """Return the pandas module if available, otherwise None."""
    try:
        import pandas as pd  # type: ignore
        return pd
    except ImportError:
        return None


def download_file(url: str, dest_path: str) -> bool:
    """Download a file from a URL to the given destination path.

    Returns True if the download succeeds, False otherwise.  This function
    uses only the standard library (`urllib`) so that it works in
    restricted environments.
    """
    from urllib.request import urlopen, Request
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req) as response, open(dest_path, "wb") as out_file:
            chunk_size = 8192
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
        return True
    except Exception as exc:
        print(f"[WARN] Failed to download {url}: {exc}")
        return False


def convert_parquet_to_csv(parquet_path: str, csv_path: str) -> bool:
    """Convert a Parquet file to CSV using pandas if available.

    Returns True on success, False on failure.  This function will
    gracefully handle missing dependencies by returning False and
    printing a message.
    """
    pd = try_import_pandas()
    if pd is None:
        print("[WARN] pandas (with pyarrow or fastparquet) is not installed; cannot convert Parquet to CSV.")
        return False
    try:
        # Attempt to read with pyarrow if available; pandas will choose the
        # appropriate engine.  We read only a subset of columns for memory
        # efficiency.  Modify the list as needed.
        df = pd.read_parquet(parquet_path)
        df.to_csv(csv_path, index=False)
        return True
    except Exception as exc:
        print(f"[WARN] Failed to convert {parquet_path} to CSV: {exc}")
        return False


def generate_synthetic_data(csv_path: str, num_records: int = 100000) -> None:
    """Generate a synthetic taxi trip dataset and write it to CSV.

    The synthetic data closely follows the schema of the NYC TLC
    ``yellow_tripdata`` files.  Fields include vendor ID, pickup and
    dropoff timestamps, passenger count, trip distance, fare and total
    amounts.  Values are randomly generated within realistic ranges.
    """
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    start_date = datetime.datetime(2025, 1, 1)
    vendors = [1, 2]
    payment_types = [1, 2, 3, 4, 5]  # cash, credit card, etc.
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow([
            "vendor_id",
            "tpep_pickup_datetime",
            "tpep_dropoff_datetime",
            "passenger_count",
            "trip_distance",
            "fare_amount",
            "total_amount",
            "payment_type",
        ])
        for _ in range(num_records):
            vendor_id = random.choice(vendors)
            # Generate a pickup time within the month of January 2025
            minutes_offset = random.randint(0, 31 * 24 * 60)
            pickup = start_date + datetime.timedelta(minutes=minutes_offset)
            # Trip duration between 5 and 60 minutes
            duration = random.uniform(5, 60)
            dropoff = pickup + datetime.timedelta(minutes=duration)
            passenger_count = random.randint(1, 4)
            trip_distance = round(random.uniform(0.2, 20.0), 2)
            base_fare_per_mile = random.uniform(2.0, 3.0)
            fare_amount = round(trip_distance * base_fare_per_mile + 2.5, 2)
            # total_amount includes surcharges and tips (~20% of fare)
            total_amount = round(fare_amount * random.uniform(1.15, 1.30), 2)
            payment_type = random.choice(payment_types)
            writer.writerow([
                vendor_id,
                pickup.isoformat(),
                dropoff.isoformat(),
                passenger_count,
                trip_distance,
                fare_amount,
                total_amount,
                payment_type,
            ])
    print(f"[INFO] Generated synthetic dataset with {num_records} records at {csv_path}")


def main(args: argparse.Namespace) -> None:
    output_csv = args.output
    if args.generate_synthetic:
        generate_synthetic_data(output_csv, args.num_records)
        return
    # Attempt to download Parquet data if a URL is provided
    if args.url:
        parquet_path = os.path.join(os.path.dirname(output_csv), "temp.parquet")
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        print(f"[INFO] Downloading Parquet data from {args.url}…")
        ok = download_file(args.url, parquet_path)
        if ok:
            print(f"[INFO] Converting Parquet to CSV…")
            ok = convert_parquet_to_csv(parquet_path, output_csv)
            # Clean up temporary file
            try:
                os.remove(parquet_path)
            except OSError:
                pass
            if ok:
                print(f"[INFO] Successfully saved CSV to {output_csv}")
                return
        print("[WARN] Falling back to synthetic data generation.")
    # Fallback: generate synthetic data
    generate_synthetic_data(output_csv, args.num_records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest NYC taxi trip data.")
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="URL of the Parquet file to download. If omitted, synthetic data will be generated.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/raw/yellow_tripdata_2025-01.csv",
        help="Path to the output CSV file.",
    )
    parser.add_argument(
        "--generate-synthetic",
        action="store_true",
        help="Force generation of synthetic data instead of downloading.",
    )
    parser.add_argument(
        "--num-records",
        type=int,
        default=100_000,
        help="Number of synthetic records to generate.",
    )
    arguments = parser.parse_args()
    main(arguments)