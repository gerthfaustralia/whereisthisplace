import sys
from pathlib import Path
import importlib
import asyncio

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "api"))

import api.main
from routes.predict import predict
from unittest.mock import patch
import json


def get_fresh_client():
    importlib.reload(api.main)
    return TestClient(api.main.app)


class DummyUploadFile:
    def __init__(self, data: bytes, filename: str = "test.jpg", content_type: str = "image/jpeg"):
        self.data = data
        self.filename = filename
        self.content_type = content_type

    async def read(self) -> bytes:
        return self.data


def test_health_endpoint_returns_200():
    client = get_fresh_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("fastapi_status") == "healthy"
    assert "torchserve_status" in data


@patch("api.routes.predict.requests.post")
def test_predict_returns_expected_data(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"lat": 1, "lon": 2}
    file = DummyUploadFile(b"dummy")
    result = asyncio.run(predict(photo=file))
    assert result == {
        "status": "success",
        "filename": "test.jpg",
        "prediction": {"lat": 1, "lon": 2},
        "message": "Prediction completed successfully",
    }


def test_rate_limit_returns_429_after_limit_exceeded():
    client = get_fresh_client()
    for _ in range(10):
        resp = client.get("/health")
        assert resp.status_code == 200
    resp = client.get("/health")
    assert resp.status_code == 429

