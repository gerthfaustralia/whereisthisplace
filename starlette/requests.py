class Client:
    def __init__(self, host="test"):
        self.host = host


class Request:
    def __init__(self, body=b"", client=None):
        self._body = body
        self.client = client or Client()

    async def body(self):
        return self._body


