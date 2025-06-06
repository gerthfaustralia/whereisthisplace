import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import patch, AsyncMock
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "api"))

from routes.predict import predict

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

class DummyOpenAI:
    class ChatCompletion:
        @staticmethod
        def create(*args, **kwargs):
            return {"choices": [{"message": {"content": "Paris, France"}}]}

@patch("routes.predict.insert_prediction", new_callable=AsyncMock)
@patch("routes.predict.OPENAI_API_KEY", "test_key")  # Mock the OPENAI_API_KEY constant
@patch("routes.predict.requests.get")
@patch("routes.predict.openai", new=DummyOpenAI)
@patch("routes.predict.nearest", new_callable=AsyncMock)
@patch("routes.predict.requests.post")
def test_openai_mode_fallback(mock_post, mock_nearest, mock_get, mock_insert):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"embedding": [0.0] * 128}
    mock_nearest.return_value = {"lat": 0.0, "lon": 0.0, "score": 0.1}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"lat": "48.8", "lon": "2.3"}]

    file = DummyUploadFile(b"dummy")
    req = DummyRequest()
    result = asyncio.run(predict(photo=file, mode="openai", request=req))

    # Check main structure
    assert result["status"] == "success"
    assert result["filename"] == "test.jpg"
    assert result["message"] == "Prediction completed successfully"
    
    # The prediction should show OpenAI coordinates due to fallback
    prediction = result["prediction"]
    assert prediction["lat"] == 48.8
    assert prediction["lon"] == 2.3
    assert prediction["score"] == 0.95  # OpenAI result has high confidence
    assert prediction["source"] == "openai"
    assert prediction["confidence_level"] == "high"
    assert "bias_warning" in prediction
    mock_insert.assert_awaited_once()
