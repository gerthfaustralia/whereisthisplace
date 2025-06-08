import argparse
import asyncio
import csv
import hashlib
import os
from pathlib import Path
from typing import Optional, Sequence

import asyncpg
import numpy as np
import requests
from pgvector.asyncpg import register_vector


async def _compute_embedding(image_path: Path, model_url: Optional[str] = None) -> Sequence[float]:
    """Return a 128-dim embedding for the given image.

    If ``model_url`` is provided, the image is sent to TorchServe's HTTP
    inference API and the returned embedding is used. Otherwise a deterministic
    embedding derived from the file contents is returned.
    """
    data = image_path.read_bytes()
    if model_url:
        try:
            resp = requests.post(f"{model_url.rstrip('/')}/predictions/where", data=data, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            if isinstance(result, dict) and "embedding" in result:
                return result["embedding"]
            if isinstance(result, list):
                return result
            print(f"Warning: Unexpected response from model server for {image_path.name}, using fallback")
        except Exception as e:
            print(f"Warning: TorchServe error for {image_path.name}: {e}, using fallback embedding")

    # Deterministic fallback embedding using SHA256 hash
    digest = hashlib.sha256(data).digest()
    arr = np.frombuffer(digest * 8, dtype=np.uint8)[:128].astype("float32")
    return arr.tolist()


async def init_connection(conn):
    """Initialize connection with pgvector and set correct schema."""
    await conn.execute("SET search_path TO whereisthisplace, public;")
    await register_vector(conn)

async def load_dataset(dataset_dir: Path, database_url: str, model_url: Optional[str] = None) -> int:
    """Load all CSV files in ``dataset_dir`` into the database.

    Returns the number of inserted rows.
    """
    pool = await asyncpg.create_pool(dsn=database_url, init=init_connection)
    inserted = 0
    try:
        for csv_path in dataset_dir.glob("*.csv"):
            print(f"Processing {csv_path.name}...")
            with csv_path.open(newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    img_path = dataset_dir / row["image"]
                    if not img_path.exists():
                        print(f"Warning: Image {img_path} not found, skipping...")
                        continue
                        
                    lat = float(row["lat"])
                    lon = float(row["lon"])
                    embedding = await _compute_embedding(img_path, model_url)
                    
                    # Convert embedding to numpy array and then to list for pgvector
                    if isinstance(embedding, list):
                        embedding_array = np.array(embedding, dtype=np.float32)
                    else:
                        embedding_array = np.array(embedding, dtype=np.float32)
                    
                    await pool.execute(
                        "INSERT INTO photos (lat, lon, vlad) VALUES ($1, $2, $3)",
                        lat,
                        lon,
                        embedding_array.tolist(),
                    )
                    inserted += 1
                    
                    if inserted % 10 == 0:
                        print(f"  Inserted {inserted} images...")
    finally:
        await pool.close()
    return inserted


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Load dataset into database")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=Path("datasets"),
        help="Directory containing CSV files and images",
    )
    parser.add_argument(
        "--model-url",
        help="TorchServe inference URL. If omitted, use local embedding stub",
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL"),
        help="Database connection string",
    )

    args = parser.parse_args(argv)
    if not args.database_url:
        raise SystemExit("DATABASE_URL must be provided via --database-url or environment")

    count = asyncio.run(load_dataset(args.dataset_dir, args.database_url, args.model_url))
    print(f"Inserted {count} rows")


if __name__ == "__main__":
    main()
