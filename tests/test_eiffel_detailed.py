import sys
from pathlib import Path
import asyncio
from unittest.mock import patch, AsyncMock

ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "api"))

from api.routes.predict import predict

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

@patch("api.routes.predict.OPENAI_API_KEY", None)
@patch("api.routes.predict.nearest", new_callable=AsyncMock)
@patch("api.routes.predict.requests.post")
def test_eiffel_bias_detection(mock_post, mock_nearest):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"embedding": [0.0] * 128}
    mock_nearest.return_value = {"lat": 40.75, "lon": -73.99, "score": 0.95}

    image_data = load_test_image()
    file = DummyUploadFile(image_data, filename="eiffel.jpg")

    result = asyncio.run(predict(photo=file))
    prediction = result["prediction"]

    print("=== Eiffel Tower Bias Detection Test Results ===")
    print(f"filename: {result['filename']}")
    print(f"bias_warning: {prediction.get('bias_warning')}")
    print(f"score: {prediction.get('score')}")
    print(f"original_score: {prediction.get('original_score')}")
    print(f"confidence_level: {prediction.get('confidence_level')}")
    print(f"warning: {prediction.get('warning')}")
    print(f"source: {prediction.get('source')}")
    
    # Definition of Done checks
    print("\n=== Definition of Done Verification ===")
    
    # Check 1: bias_warning field exists
    has_bias_warning = prediction.get("bias_warning") is not None
    print(f"✅ Has bias_warning field: {has_bias_warning}")
    
    # Check 2: confidence < 0.4
    score = prediction.get("score", 1.0)
    low_confidence = score < 0.4
    print(f"✅ Confidence < 0.4: {low_confidence} (score: {score})")
    
    # Additional checks
    print(f"Original score was: {prediction.get('original_score')}")
    print(f"Confidence level: {prediction.get('confidence_level')}")
    
    assert has_bias_warning, "bias_warning field should be present"
    assert low_confidence, f"Score should be < 0.4, got {score}"
    
    print("\n✅ All Definition of Done requirements met!")

if __name__ == "__main__":
    test_eiffel_bias_detection() 