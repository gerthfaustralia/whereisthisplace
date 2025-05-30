from fastapi import APIRouter, UploadFile, File, HTTPException
import requests
from io import BytesIO
import os
import json

router = APIRouter()

TORCHSERVE_URL = os.getenv('TORCHSERVE_URL', 'http://localhost:8080')


@router.post("/predict")
async def predict(photo: UploadFile = File(...)):
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
                prediction_result = response.json()
            except json.JSONDecodeError:
                prediction_result = response.text

            return {
                "status": "success",
                "filename": photo.filename,
                "prediction": prediction_result,
                "message": "Prediction completed successfully"
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
