class Response:
    def __init__(self, json_data=None, status_code=200):
        self._json = json_data or {}
        self.status_code = status_code
        self.text = str(json_data)

    def json(self):
        return self._json


class _Exceptions:
    class ConnectionError(Exception):
        pass

    class Timeout(Exception):
        pass


exceptions = _Exceptions()


def post(url, data=None, timeout=None):
    return Response({"embedding": [0.0]*128})


def get(url, timeout=None):
    return Response({})

