import sys
from pathlib import Path
from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from api.main import app


def test_app_is_fastapi_instance():
    assert isinstance(app, FastAPI)
    route_paths = {route.path for route in app.router.routes}
    assert "/health" in route_paths
