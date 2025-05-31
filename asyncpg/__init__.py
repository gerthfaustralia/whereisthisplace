class Record(dict):
    pass

class Connection:
    def __init__(self):
        self.queries = []

    async def fetchrow(self, query, vec):
        self.queries.append((query, vec))
        return Record(lat=0.0, lon=0.0, score=1.0)

    async def execute(self, query, *args):
        self.queries.append((query, args))

    async def close(self):
        pass


async def create_pool(dsn=None):
    return Connection()

async def connect(dsn=None):
    return Connection()

