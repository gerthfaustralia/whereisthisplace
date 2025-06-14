from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
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
from api.repositories.photos import insert_prediction


async def query_geo(vec: np.ndarray) -> "GeoResult":
    """Return geographic coordinates for a PatchNetVLAD embedding."""
    row = await nearest(vec)
    if row is None:
        raise HTTPException(status_code=404, detail="No match found")
    return GeoResult(lat=row["lat"], lon=row["lon"], score=row.get("score", 0.0))


def detect_geographic_bias(geo_result: "GeoResult", filename: str = "") -> "GeoResult":
    """Detect and adjust for known geographic bias patterns."""
    lat, lon, score = geo_result.lat, geo_result.lon, geo_result.score
    
    # NYC coordinates: roughly 40.4-41.0 latitude, -74.5 to -73.5 longitude
    is_nyc_prediction = (40.4 <= lat <= 41.0) and (-74.5 <= lon <= -73.5)
    
    # Check for suspicious patterns
    bias_detected = False
    bias_reason = ""
    
    if is_nyc_prediction:
        # Common European landmark filenames that shouldn't predict NYC
        european_keywords = [
            'eiffel', 'tower', 'brandenburg', 'gate', 'buckingham', 'palace', 
            'big_ben', 'london', 'paris', 'berlin', 'europe', 'colosseum',
            'arc_de_triomphe', 'notre_dame', 'louvre', 'westminster'
        ]
        
        filename_lower = filename.lower() if filename else ""
        if any(keyword in filename_lower for keyword in european_keywords):
            bias_detected = True
            bias_reason = f"European landmark filename '{filename}' predicted as NYC"
        
        # High confidence NYC predictions are often suspicious for user uploads
        elif score > 0.9:
            bias_detected = True
            bias_reason = "Very high confidence NYC prediction may indicate model bias"
    
    # Apply bias corrections
    if bias_detected:
        # Reduce confidence significantly for biased predictions
        adjusted_score = score * 0.3
        return GeoResult(
            lat=lat, 
            lon=lon, 
            score=adjusted_score,
            bias_warning=bias_reason,
            original_score=score
        )
    
    return geo_result


def should_use_openai_fallback(geo_result: "GeoResult", filename: str = "") -> bool:
    """Determine if we should fallback to OpenAI due to low confidence or bias."""
    # Use OpenAI fallback for:
    # 1. Very low confidence scores
    if geo_result.score < 0.4:
        return True
    
    # 2. Bias-adjusted predictions (they have bias_warning attribute)
    if hasattr(geo_result, 'bias_warning'):
        return True
    
    # 3. Suspicious NYC predictions with moderate confidence
    is_nyc = (40.4 <= geo_result.lat <= 41.0) and (-74.5 <= geo_result.lon <= -73.5)
    if is_nyc and geo_result.score < 0.7:
        return True
    
    return False


try:
    import openai as _openai
except Exception:
    _openai = types.SimpleNamespace()

openai = _openai

# Configure OpenAI credentials from environment if available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

router = APIRouter()

TORCHSERVE_URL = os.getenv('TORCHSERVE_URL', 'http://localhost:8080')


async def get_db_pool(request: Request):
    """Dependency to get database pool from app state."""
    return getattr(request.app.state, "pool", None)


@dataclass
class GeoResult:
    lat: float
    lon: float
    score: float
    bias_warning: Optional[str] = None
    original_score: Optional[float] = None
    source: str = "model"  # "model" or "openai"


@router.post("/predict")
async def predict(photo: UploadFile = File(...), mode: Optional[str] = None, db_pool=Depends(get_db_pool)):
    """
    Make prediction using the uploaded photo with bias detection and fallback.
    
    FEATURE BRANCH: OpenAI-Default Mode
    - OpenAI is now the default prediction method
    - Model is only used when mode="model" is explicitly specified
    - This allows testing OpenAI responses while the model/database matures
    """
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
            
            # Apply bias detection
            geo = detect_geographic_bias(geo, photo.filename)
            
            # FEATURE BRANCH: OpenAI is now the default mode
            # Always use OpenAI unless explicitly disabled with mode="model"
            use_openai = (mode != "model") and OPENAI_API_KEY
            
            if use_openai:
                try:
                    b64 = base64.b64encode(image_data).decode()
                    # Using modern OpenAI v1.x syntax
                    client = openai.OpenAI(api_key=OPENAI_API_KEY)
                    resp = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Where was this photo taken? Reply with ONLY the city and country name, like 'Paris, France' or 'New York, USA'. If you cannot identify the location, reply with 'Unknown'.",
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:{photo.content_type};base64,{b64}"},
                                },
                            ],
                        }],
                        max_tokens=50
                    )
                    place = resp.choices[0].message.content.strip()
                    
                    # Skip if OpenAI couldn't identify the location
                    if any(phrase in place.lower() for phrase in ['unknown', 'i cannot', 'i\'m sorry', 'unable to determine']):
                        raise Exception("OpenAI could not identify location")
                    g = requests.get(
                        "https://nominatim.openstreetmap.org/search",
                        params={"q": place, "format": "json", "limit": 1},
                                                headers={"User-Agent": "WhereIsThisPlace/1.0 (https://github.com/whereisthisplace)"},
                        timeout=10,
                    )
                    if g.status_code == 200:
                        data = g.json()
                        if isinstance(data, list) and data:
                            # Use OpenAI result, but preserve original for comparison
                            original_geo = geo
                            geo = GeoResult(
                                lat=float(data[0]["lat"]),
                                lon=float(data[0]["lon"]),
                                score=0.95,  # High confidence for OpenAI
                                source="openai",
                                bias_warning=getattr(original_geo, 'bias_warning', None),
                                original_score=original_geo.score  # Preserve model score for comparison
                            )
                except Exception as openai_error:
                    # If OpenAI fails, continue with model prediction but add warning
                    print(f"OpenAI request failed: {str(openai_error)}")
                    # Add failure warning to the model prediction
                    if hasattr(geo, 'bias_warning') and geo.bias_warning:
                        geo.bias_warning += f" (OpenAI unavailable: {str(openai_error)})"
                    else:
                        geo.bias_warning = f"OpenAI unavailable: {str(openai_error)}"

            # Prepare response with enhanced information
            prediction_dict = asdict(geo)
            
            # Add confidence category for user-friendly display
            if geo.score >= 0.8:
                confidence_level = "high"
            elif geo.score >= 0.5:
                confidence_level = "medium"
            elif geo.score >= 0.3:
                confidence_level = "low"
            else:
                confidence_level = "very_low"
            
            prediction_dict["confidence_level"] = confidence_level
            
            # Add warning message for UI
            if hasattr(geo, 'bias_warning') and geo.bias_warning:
                prediction_dict["warning"] = "Location prediction may be inaccurate due to model bias"

            # Persist prediction in the database if a pool is available
            if db_pool:
                try:
                    await insert_prediction(
                        db_pool,
                        geo.lat,
                        geo.lon,
                        geo.score,
                        getattr(geo, "bias_warning", None),
                        geo.source,
                    )
                except Exception as db_error:
                    print(f"DB insert failed: {db_error}")

            return {
                "status": "success",
                "filename": photo.filename,
                "prediction": prediction_dict,
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
