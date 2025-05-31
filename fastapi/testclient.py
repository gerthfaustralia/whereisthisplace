from . import Request


class Response:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json


class TestClient:
    def __init__(self, app):
        self.app = app

    def post(self, path, data=None):
        handler = self.app._routes.get(path)
        if not handler:
            return Response(None, 404)
        req = Request(data or b"")
        result = handler(req)
        if hasattr(result, '__await__'):
            import asyncio
            result = asyncio.get_event_loop().run_until_complete(result)
        return Response(result)

    def get(self, path):
        handler = self.app._routes.get(path)
        if not handler:
            return Response(None, 404)
        result = handler()
        if hasattr(result, '__await__'):
            import asyncio
            result = asyncio.get_event_loop().run_until_complete(result)
        return Response(result)


