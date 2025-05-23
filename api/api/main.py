from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.predict import router as predict_router
from .core.config import settings

app = FastAPI(
    title="WhereIsThisPlace API",
    version="0.1.0",
    description="AI-powered photo geolocation",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router, prefix="/api/v1/predict", tags=["predict"])


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "WhereIsThisPlace API"}
