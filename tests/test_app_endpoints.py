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
import types
import json
class DummyUploadFile:
    def __init__(self, data: bytes, filename: str = "test.jpg", content_type: str = "image/jpeg"):
        self.data = data
        self.filename = filename
        self.content_type = content_type

    async def read(self) -> bytes:
        return self.data


class DummyRequest:
    def __init__(self):
        self.app = types.SimpleNamespace(state=types.SimpleNamespace(pool="pool"))


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


@patch("routes.predict.insert_prediction", new_callable=AsyncMock)
@patch("routes.predict.nearest", new_callable=AsyncMock)
@patch("routes.predict.requests.post")
def test_predict_returns_expected_data(mock_post, mock_nearest, mock_insert):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"embedding": [0.0] * 128}
    mock_nearest.return_value = {"lat": 1.0, "lon": 2.0, "score": 0.5}
    file = DummyUploadFile(b"dummy")
    req = DummyRequest()
    result = asyncio.run(predict(photo=file, request=req))
    
    # Check main structure
    assert result["status"] == "success"
    assert result["filename"] == "test.jpg"
    assert result["message"] == "Prediction completed successfully"
    
    # Check prediction structure with new fields
    prediction = result["prediction"]
    assert prediction["lat"] == 1.0
    assert prediction["lon"] == 2.0
    assert prediction["score"] == 0.5
    assert prediction["confidence_level"] == "medium"  # 0.5 score = medium confidence
    assert "bias_warning" in prediction
    assert "source" in prediction
    assert prediction["source"] == "model"
    mock_insert.assert_awaited_once()


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

