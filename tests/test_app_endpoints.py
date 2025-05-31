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
from unittest.mock import patch, AsyncMock
import json
class DummyUploadFile:
    def __init__(self, data: bytes, filename: str = "test.jpg", content_type: str = "image/jpeg"):
        self.data = data
        self.filename = filename
        self.content_type = content_type

    async def read(self) -> bytes:
        return self.data


def test_health_endpoint_returns_200():
    importlib.reload(api.main)
    with patch("api.main.init_db", new_callable=AsyncMock), patch(
        "api.main.close_db", new_callable=AsyncMock
    ):
        client = TestClient(api.main.app)
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("fastapi_status") == "healthy"
        assert "torchserve_status" in data


@patch("routes.predict.nearest", new_callable=AsyncMock)
@patch("routes.predict.requests.post")
def test_predict_returns_expected_data(mock_post, mock_nearest):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"embedding": [0.0] * 128}
    mock_nearest.return_value = {"lat": 1.0, "lon": 2.0, "score": 0.5}
    file = DummyUploadFile(b"dummy")
    result = asyncio.run(predict(photo=file))
    assert result == {
        "status": "success",
        "filename": "test.jpg",
        "prediction": {"lat": 1.0, "lon": 2.0, "score": 0.5},
        "message": "Prediction completed successfully",
    }


def test_rate_limit_returns_429_after_limit_exceeded():
    importlib.reload(api.main)
    with patch("api.main.init_db", new_callable=AsyncMock), patch(
        "api.main.close_db", new_callable=AsyncMock
    ):
        client = TestClient(api.main.app)
        for _ in range(10):
            resp = client.get("/health")
            assert resp.status_code == 200
        resp = client.get("/health")
        assert resp.status_code == 429

