from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any

from ..models.schemas import PredictionResponse, LocationData
from ..core.config import settings
from ml import scene_classifier, retrieval, fuse

router = APIRouter()


@router.post("/", response_model=PredictionResponse)
async def predict_location(photo: UploadFile = File(...)) -> PredictionResponse:
    """Predict the location of an uploaded photo."""
    image_bytes = await photo.read()
    scene = scene_classifier.predict_topk(image_bytes, k=5)
    retrieval_results = retrieval.search(image_bytes, k=5)
    (lat, lon), confidence = fuse.fuse(scene=scene, retrieval=retrieval_results)
    return PredictionResponse(latitude=lat, longitude=lon, confidence=confidence)
