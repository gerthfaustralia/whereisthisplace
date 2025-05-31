import sys
from pathlib import Path
import csv
import asyncio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.load_dataset import load_dataset

class DummyPool:
    def __init__(self):
        self.rows = []
    async def execute(self, query, *args):
        self.rows.append(args)
    async def close(self):
        pass


def create_dataset(tmpdir, count=100):
    d = Path(tmpdir)
    img = d / "img.jpg"
    img.write_bytes(b"x")
    csv_path = d / "data.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "lat", "lon"])
        for i in range(count):
            writer.writerow(["img.jpg", i, i + 1])
    return d


def test_load_dataset_inserts_rows(monkeypatch, tmp_path):
    dataset_dir = create_dataset(tmp_path, 110)
    pool = DummyPool()
    async def create_pool(dsn):
        return pool
    monkeypatch.setattr("asyncpg.create_pool", create_pool)
    inserted = asyncio.run(load_dataset(dataset_dir, "postgresql://"))
    assert inserted >= 100
    assert len(pool.rows) >= 100
