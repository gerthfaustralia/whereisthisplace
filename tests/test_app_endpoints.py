import importlib
import asyncio

from fastapi.testclient import TestClient

import api.main
from api.routes.predict import predict_location


def get_fresh_client():
    importlib.reload(api.main)
    return TestClient(api.main.app)


class DummyUploadFile:
    def __init__(self, data: bytes):
        self.data = data

    async def read(self) -> bytes:
        return self.data


def test_predict_returns_expected_data():
    file = DummyUploadFile(b"dummy")
    result = asyncio.run(predict_location(photo=file))
    assert result == {"latitude": 0.0, "longitude": 0.0, "confidence": 0.1}
