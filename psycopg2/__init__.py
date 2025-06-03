class Cursor:
    def execute(self, query, *args, **kwargs):
        pass
    def fetchone(self):
        return [0]
    def fetchall(self):
        return []
    def close(self):
        pass

class Connection:
    def __init__(self, *args, **kwargs):
        self._cursor = Cursor()
    def cursor(self):
        return self._cursor
    def close(self):
        pass

def connect(*args, **kwargs):
    return Connection(*args, **kwargs)
