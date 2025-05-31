import sys
from pathlib import Path
import asyncio
from unittest.mock import patch, AsyncMock

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

class DummyOpenAI:
    class ChatCompletion:
        @staticmethod
        def create(*args, **kwargs):
            return {"choices": [{"message": {"content": "Paris, France"}}]}

@patch("routes.predict.requests.get")
@patch("routes.predict.openai", new=DummyOpenAI)
@patch("routes.predict.nearest", new_callable=AsyncMock)
@patch("routes.predict.requests.post")
def test_openai_mode_fallback(mock_post, mock_nearest, mock_get):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"embedding": [0.0] * 128}
    mock_nearest.return_value = {"lat": 0.0, "lon": 0.0, "score": 0.1}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"lat": "48.8", "lon": "2.3"}]

    file = DummyUploadFile(b"dummy")
    result = asyncio.run(predict(photo=file, mode="openai"))

    assert result == {
        "status": "success",
        "filename": "test.jpg",
        "prediction": {"lat": 48.8, "lon": 2.3, "score": 0.1},
        "message": "Prediction completed successfully",
    }
