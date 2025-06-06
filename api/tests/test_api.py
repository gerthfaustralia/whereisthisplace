import sys
from pathlib import Path
from unittest.mock import patch, Mock, AsyncMock
import asyncio

API_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = API_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(1, str(API_ROOT))

from fastapi import FastAPI

from api.main import app


def test_app_is_fastapi_instance():
    assert isinstance(app, FastAPI)
    route_paths = {route.path for route in app.router.routes}
    assert "/health" in route_paths
    assert "/predict" in route_paths


class DummyUploadFile:
    def __init__(self, data: bytes):
        self.data = data
        self.filename = "test.jpg"
        self.content_type = "image/jpeg"

    async def read(self) -> bytes:
        return self.data


def test_predict_endpoint_returns_location():
    from routes.predict import predict

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"embedding": [0.0] * 128}

    with patch('routes.predict.requests.post', return_value=mock_response), \
        patch('routes.predict.nearest', new_callable=AsyncMock) as mock_nearest:
        mock_nearest.return_value = {"lat": 0.0, "lon": 0.0, "score": 0.1}
        file = DummyUploadFile(b"dummy")
        data = asyncio.run(predict(photo=file))

        assert data["status"] == "success"
        assert data["filename"] == "test.jpg"
        assert data["message"] == "Prediction completed successfully"

        prediction = data["prediction"]
        assert prediction["lat"] == 0.0
        assert prediction["lon"] == 0.0
        assert prediction["score"] == 0.1
        assert prediction["confidence_level"] == "very_low"
        assert "bias_warning" in prediction
        assert prediction["source"] == "model"


def test_rate_limit_middleware_added():
    from api.middleware import RateLimitMiddleware
    middleware_classes = {m.cls for m in app.user_middleware}
    assert RateLimitMiddleware in middleware_classes

