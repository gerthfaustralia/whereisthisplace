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


def load_test_image() -> bytes:
    with open(ROOT / "eiffel.jpg", "rb") as f:
        return f.read()


@patch("routes.predict.OPENAI_API_KEY", None)
@patch("routes.predict.nearest", new_callable=AsyncMock)
@patch("routes.predict.requests.post")
def test_eiffel_bias_detection(mock_post, mock_nearest):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"embedding": [0.0] * 128}
    mock_nearest.return_value = {"lat": 40.75, "lon": -73.99, "score": 0.95}

    image_data = load_test_image()
    file = DummyUploadFile(image_data, filename="eiffel.jpg")

    result = asyncio.run(predict(photo=file))
    prediction = result["prediction"]

    assert prediction["bias_warning"] is not None
    assert prediction["score"] < 0.4
