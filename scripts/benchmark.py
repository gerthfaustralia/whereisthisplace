#!/usr/bin/env python3
"""Benchmark harness for WhereIsThisPlace API.

Loads gold-label images and evaluates model predictions.
"""
import argparse
import csv
import sys
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path
from typing import Iterable, Tuple

import requests


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in kilometers between two lat/lon coordinates."""
    r = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c


def iter_dataset(dataset_dir: Path) -> Iterable[Tuple[Path, float, float]]:
    """Yield (image_path, lat, lon) for all CSV files under dataset_dir."""
    for csv_path in dataset_dir.rglob("*.csv"):
        with csv_path.open(newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                img = csv_path.parent / row["image"]
                yield img, float(row["lat"]), float(row["lon"])


def evaluate(dataset_dir: Path, api_url: str, threshold_km: float) -> Tuple[float, float]:
    distances = []
    correct = 0
    total = 0
    for img_path, lat, lon in iter_dataset(dataset_dir):
        with open(img_path, "rb") as f:
            files = {"photo": (img_path.name, f, "image/jpeg")}
            try:
                resp = requests.post(f"{api_url.rstrip('/')}/predict", files=files, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                prediction = data.get("prediction", data)
                pred_lat = float(prediction["lat"])
                pred_lon = float(prediction["lon"])
            except Exception as exc:
                print(f"Error on {img_path.name}: {exc}", file=sys.stderr)
                continue
        dist = haversine(lat, lon, pred_lat, pred_lon)
        distances.append(dist)
        if dist <= threshold_km:
            correct += 1
        total += 1
    if not total:
        return 0.0, float("inf")
    mean_error = sum(distances) / total
    accuracy = (correct / total) * 100
    return accuracy, mean_error


def main() -> None:
    parser = argparse.ArgumentParser(description="Run benchmark against API")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=Path("datasets"),
        help="Directory containing gold-label datasets",
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Base URL of the API",
    )
    parser.add_argument(
        "--threshold-km",
        type=float,
        default=1.0,
        help="Distance threshold in km for Top-1 accuracy",
    )
    args = parser.parse_args()

    acc, mean_err = evaluate(args.dataset_dir, args.api_url, args.threshold_km)
    print(f"Top-1 Accuracy: {acc:.2f}%")
    print(f"Mean Error: {mean_err:.2f} km")

    if acc < 70.0:
        sys.exit(1)


if __name__ == "__main__":
    main()
