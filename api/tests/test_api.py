import asyncio

from fastapi import FastAPI

from api.main import app


def test_app_is_fastapi_instance():
    assert isinstance(app, FastAPI)
    route_paths = {route.path for route in app.router.routes}
    assert "/api/v1/predict/" in route_paths


class DummyUploadFile:
    def __init__(self, data: bytes):
        self.data = data

    async def read(self) -> bytes:
        return self.data


def test_predict_endpoint_returns_location():
    from api.routes.predict import predict_location

    file = DummyUploadFile(b"dummy")
    data = asyncio.run(predict_location(photo=file))
    assert data == {"latitude": 0.0, "longitude": 0.0, "confidence": 0.1}


def test_no_custom_middleware():
    """The application should start without extra middleware by default."""
    assert app.user_middleware == []

