try:
    from starlette.requests import Client as StarletteClient
except Exception:  # pragma: no cover - fallback for tests without starlette stub
    class StarletteClient:
        def __init__(self, host: str = "test"):
            self.host = host


class Request:
    def __init__(self, body: bytes = b"", client: StarletteClient | None = None):
        self._body = body
        self.client = client or StarletteClient()

    async def body(self) -> bytes:
        return self._body


class FastAPI:
    def __init__(self, *args, **kwargs):
        self.router = type('Router', (), {'routes': []})()
        self.user_middleware = []
        self._routes = {}

    def add_middleware(self, cls, **options):
        self.user_middleware.append(type('MW', (), {'cls': cls}))

    def get(self, path):
        def decorator(func):
            self._routes[path] = func
            self.router.routes.append(type('Route', (), {'path': path}))
            return func
        return decorator

    def post(self, path):
        def decorator(func):
            self._routes[path] = func
            self.router.routes.append(type('Route', (), {'path': path}))
            return func
        return decorator

    def include_router(self, router):
        for route in getattr(router, 'routes', []):
            self.router.routes.append(route)

class APIRouter:
    def __init__(self):
        self.routes = []
    def post(self, path):
        def decorator(func):
            self.routes.append(type("Route", (), {"path": path}))
            return func
        return decorator

def File(default):
    return default

class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str = ""):
        self.status_code = status_code
        self.detail = detail


class UploadFile:
    def __init__(self, data: bytes, filename="file"):
        self.data = data
        self.filename = filename
        self.content_type = "application/octet-stream"

    async def read(self) -> bytes:
        return self.data


from .testclient import TestClient


