import sys
import asyncio
from unittest.mock import AsyncMock, patch

# Fix import paths
sys.path.insert(0, '.')

# Mock the repositories before importing predict
with patch.dict('sys.modules', {
    'api.repositories.match': AsyncMock(),
    'api.repositories.photos': AsyncMock()
}):
    from routes.predict import predict

class DummyUploadFile:
    def __init__(self, data: bytes, filename: str = "test.jpg", content_type: str = "image/jpeg"):
        self.data = data
        self.filename = filename
        self.content_type = content_type

    async def read(self) -> bytes:
        return self.data

@patch("routes.predict.insert_prediction", new_callable=AsyncMock)
@patch("routes.predict.nearest", new_callable=AsyncMock)
@patch("routes.predict.requests.post")
def test_prediction_logged(mock_post, mock_nearest, mock_insert):
    """Test that predictions are logged to the database."""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"embedding": [0.0]*128}
    mock_nearest.return_value = {"lat": 5.0, "lon": 6.0, "score": 0.7}

    file = DummyUploadFile(b"dummy")
    mock_db_pool = "mock_pool"
    result = asyncio.run(predict(photo=file, db_pool=mock_db_pool))

    assert result["status"] == "success"
    # Verify that insert_prediction was called
    mock_insert.assert_awaited_once()
    
    # Check the arguments passed to insert_prediction
    call_args = mock_insert.call_args
    assert call_args[0][0] == "mock_pool"  # db_pool
    assert call_args[0][1] == 5.0  # lat
    assert call_args[0][2] == 6.0  # lon
    assert call_args[0][3] == 0.7  # score
    assert call_args[0][4] is None  # bias_warning (no bias for this case)
    assert call_args[0][5] == "model"  # source
    
    print("✅ Database insertion test passed!")
    return True

@patch("routes.predict.insert_prediction", new_callable=AsyncMock)
@patch("routes.predict.nearest", new_callable=AsyncMock)
@patch("routes.predict.requests.post")
def test_no_db_pool_case(mock_post, mock_nearest, mock_insert):
    """Test that the function works when no database pool is provided."""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"embedding": [0.0]*128}
    mock_nearest.return_value = {"lat": 5.0, "lon": 6.0, "score": 0.7}

    file = DummyUploadFile(b"dummy")
    result = asyncio.run(predict(photo=file, db_pool=None))

    assert result["status"] == "success"
    # Verify that insert_prediction was NOT called
    mock_insert.assert_not_awaited()
    
    print("✅ No database pool test passed!")
    return True

if __name__ == "__main__":
    test_prediction_logged()
    test_no_db_pool_case()
    print("🎉 All database insertion tests passed!") 