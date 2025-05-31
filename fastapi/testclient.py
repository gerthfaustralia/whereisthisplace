from . import Request
from starlette.responses import Response as StarletteResponse


class Response:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json


class TestClient:
    def __init__(self, app):
        self.app = app
        self._middleware = [mw.cls(app) for mw in app.user_middleware]

    def _apply_middleware(self, handler):
        import inspect

        async def call(req):
            async def run_next(r):
                if inspect.signature(handler).parameters:
                    res = handler(r)
                else:
                    res = handler()
                if hasattr(res, '__await__'):
                    import asyncio
                    res = await res
                return res

            next_call = run_next
            for mw_instance in reversed(self._middleware):
                current = next_call
                if hasattr(mw_instance, 'dispatch'):
                    async def wrapper(r, mw_instance=mw_instance, next_call=current):
                        return await mw_instance.dispatch(r, next_call)

                    next_call = wrapper
            
            return await next_call(req)

        return call

    def post(self, path, data=None):
        handler = self.app._routes.get(path)
        if not handler:
            return Response(None, 404)
        req = Request(data or b"")
        call = self._apply_middleware(handler)
        import asyncio
        result = asyncio.run(call(req))
        if isinstance(result, StarletteResponse):
            return Response(result.body, result.status_code)
        return Response(result)

    def get(self, path):
        handler = self.app._routes.get(path)
        if not handler:
            return Response(None, 404)
        req = Request()
        call = self._apply_middleware(handler)
        import asyncio
        result = asyncio.run(call(req))
        if isinstance(result, StarletteResponse):
            return Response(result.body, result.status_code)
        return Response(result)


