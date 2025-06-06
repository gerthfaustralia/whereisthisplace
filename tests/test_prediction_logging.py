import sys
from pathlib import Path
import asyncio
from unittest.mock import AsyncMock, patch
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

@patch("routes.predict.insert_prediction", new_callable=AsyncMock)
@patch("routes.predict.nearest", new_callable=AsyncMock)
@patch("routes.predict.requests.post")
def test_prediction_logged(mock_post, mock_nearest, mock_insert):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"embedding": [0.0]*128}
    mock_nearest.return_value = {"lat": 5.0, "lon": 6.0, "score": 0.7}

    file = DummyUploadFile(b"dummy")
    req = DummyRequest()
    result = asyncio.run(predict(photo=file, request=req))

    assert result["status"] == "success"
    mock_insert.assert_awaited_once()
