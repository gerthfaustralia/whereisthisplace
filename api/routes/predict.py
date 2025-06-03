from fastapi import APIRouter, UploadFile, File, HTTPException
import requests
from io import BytesIO
import os
import json
import base64
import types
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import numpy as np
from api.repositories.match import nearest


async def query_geo(vec: np.ndarray) -> "GeoResult":
    """Return geographic coordinates for a PatchNetVLAD embedding."""
    row = await nearest(vec)
    if row is None:
        raise HTTPException(status_code=404, detail="No match found")
    return GeoResult(lat=row["lat"], lon=row["lon"], score=row.get("score", 0.0))

try:
    import openai as _openai
except Exception:
    _openai = types.SimpleNamespace()

openai = _openai

router = APIRouter()

TORCHSERVE_URL = os.getenv('TORCHSERVE_URL', 'http://localhost:8080')


@dataclass
class GeoResult:
    lat: float
    lon: float
    score: float


@router.post("/predict")
async def predict(photo: UploadFile = File(...), mode: Optional[str] = None):
    """Make prediction using the uploaded photo."""
    try:
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if photo.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {allowed_types}"
            )

        image_data = await photo.read()
        files = {'data': (photo.filename, BytesIO(image_data), photo.content_type)}

        response = requests.post(
            f"{TORCHSERVE_URL}/predictions/where",
            files=files,
            timeout=30
        )

        if response.status_code == 200:
            try:
                model_result = response.json()
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Invalid model response")

            embedding = None
            if isinstance(model_result, dict):
                embedding = model_result.get("embedding")
            if embedding is None and isinstance(model_result, list):
                embedding = model_result
            if embedding is None:
                raise HTTPException(status_code=500, detail="No embedding returned from model")

            vec = np.array(embedding)
            geo = await query_geo(vec)

            if mode == "openai" and geo.score < 0.15:
                try:
                    b64 = base64.b64encode(image_data).decode()
                    resp = openai.ChatCompletion.create(
                        model="gpt-4o",
                        messages=[{
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Where was this photo taken? Reply with a location name.",
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:{photo.content_type};base64,{b64}"},
                                },
                            ],
                        }],
                    )
                    place = resp["choices"][0]["message"]["content"]
                    g = requests.get(
                        "https://nominatim.openstreetmap.org/search",
                        params={"q": place, "format": "json", "limit": 1},
                        timeout=10,
                    )
                    if g.status_code == 200:
                        data = g.json()
                        if isinstance(data, list) and data:
                            geo.lat = float(data[0]["lat"])
                            geo.lon = float(data[0]["lon"])
                except Exception:
                    pass

            return {
                "status": "success",
                "filename": photo.filename,
                "prediction": asdict(geo),
                "message": "Prediction completed successfully",
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"TorchServe error: {response.text}"
            )

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to TorchServe. Please ensure the inference service is running."
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="TorchServe request timed out. The model might be processing or unavailable."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )
