from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.middleware import RateLimitMiddleware

app = FastAPI()
app.add_middleware(RateLimitMiddleware)

@app.get('/limited')
async def limited():
    return {'ok': True}

client = TestClient(app)

def test_rate_limit_exceeded():
    for _ in range(10):
        resp = client.get('/limited')
        assert resp.status_code == 200
    resp = client.get('/limited')
    assert resp.status_code == 429
