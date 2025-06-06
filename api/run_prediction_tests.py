#!/usr/bin/env python3
"""
Simple test runner for prediction database logging functionality.
Avoids import path issues by properly setting up the environment.
"""

import sys
import asyncio
from unittest.mock import AsyncMock, patch

# Set up path
sys.path.insert(0, '.')

def test_prediction_logging():
    """Test that predictions are logged to the database."""
    
    class DummyUploadFile:
        def __init__(self, data: bytes, filename: str = "test.jpg", content_type: str = "image/jpeg"):
            self.data = data
            self.filename = filename
            self.content_type = content_type
        
        async def read(self) -> bytes:
            return self.data

    # Mock dependencies to avoid import issues
    with patch.dict('sys.modules', {
        'api.repositories.match': AsyncMock(),
        'api.repositories.photos': AsyncMock()
    }):
        from routes.predict import predict
        
        @patch('routes.predict.insert_prediction', new_callable=AsyncMock)
        @patch('routes.predict.nearest', new_callable=AsyncMock)
        @patch('routes.predict.requests.post')
        def run_test(mock_post, mock_nearest, mock_insert):
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"embedding": [0.0]*128}
            mock_nearest.return_value = {"lat": 5.0, "lon": 6.0, "score": 0.7}
            
            file = DummyUploadFile(b"dummy")
            mock_db_pool = "mock_pool"
            result = asyncio.run(predict(photo=file, db_pool=mock_db_pool))
            
            assert result["status"] == "success"
            mock_insert.assert_awaited_once()
            
            # Check the arguments passed to insert_prediction
            call_args = mock_insert.call_args
            assert call_args[0][0] == "mock_pool"  # db_pool
            assert call_args[0][1] == 5.0  # lat
            assert call_args[0][2] == 6.0  # lon
            assert call_args[0][3] == 0.7  # score
            assert call_args[0][4] is None  # bias_warning (no bias for this case)
            assert call_args[0][5] == "model"  # source
            
            print("✅ Prediction logging test passed!")
            return True
        
        return run_test()

def test_eiffel_bias_with_db():
    """Test Eiffel Tower bias detection with database logging."""
    
    class DummyUploadFile:
        def __init__(self, data: bytes, filename: str = "test.jpg", content_type: str = "image/jpeg"):
            self.data = data
            self.filename = filename
            self.content_type = content_type
        
        async def read(self) -> bytes:
            return self.data

    def load_test_image():
        try:
            with open('../eiffel.jpg', 'rb') as f:
                return f.read()
        except FileNotFoundError:
            return b"dummy_eiffel_data"

    # Mock dependencies to avoid import issues
    with patch.dict('sys.modules', {
        'api.repositories.match': AsyncMock(),
        'api.repositories.photos': AsyncMock()
    }):
        from routes.predict import predict
        
        @patch('routes.predict.insert_prediction', new_callable=AsyncMock)
        @patch('routes.predict.OPENAI_API_KEY', None)
        @patch('routes.predict.nearest', new_callable=AsyncMock)
        @patch('routes.predict.requests.post')
        def run_test(mock_post, mock_nearest, mock_insert):
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"embedding": [0.0] * 128}
            mock_nearest.return_value = {"lat": 40.75, "lon": -73.99, "score": 0.95}
            
            image_data = load_test_image()
            file = DummyUploadFile(image_data, filename="eiffel.jpg")
            mock_db_pool = "mock_pool"
            
            result = asyncio.run(predict(photo=file, db_pool=mock_db_pool))
            prediction = result["prediction"]
            
            assert prediction["bias_warning"] is not None
            assert prediction["score"] < 0.4
            mock_insert.assert_awaited_once()
            
            print("✅ Eiffel Tower bias detection with DB logging test passed!")
            return True
        
        return run_test()

def test_no_db_pool():
    """Test that the function works when no database pool is provided."""
    
    class DummyUploadFile:
        def __init__(self, data: bytes, filename: str = "test.jpg", content_type: str = "image/jpeg"):
            self.data = data
            self.filename = filename
            self.content_type = content_type
        
        async def read(self) -> bytes:
            return self.data

    # Mock dependencies to avoid import issues
    with patch.dict('sys.modules', {
        'api.repositories.match': AsyncMock(),
        'api.repositories.photos': AsyncMock()
    }):
        from routes.predict import predict
        
        @patch('routes.predict.insert_prediction', new_callable=AsyncMock)
        @patch('routes.predict.nearest', new_callable=AsyncMock)
        @patch('routes.predict.requests.post')
        def run_test(mock_post, mock_nearest, mock_insert):
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
        
        return run_test()

if __name__ == "__main__":
    print("🧪 Running prediction database logging tests...")
    print()
    
    try:
        test_prediction_logging()
        test_eiffel_bias_with_db()
        test_no_db_pool()
        
        print()
        print("🎉 All prediction database logging tests passed!")
        print()
        print("✅ Definition of Done VERIFIED:")
        print("  - POST /predict integrates database insertion")
        print("  - insert_prediction is called with correct parameters")
        print("  - Database logging works for both normal and bias-detected predictions")
        print("  - Function gracefully handles missing database pool")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1) 