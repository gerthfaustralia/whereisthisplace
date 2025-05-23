from pydantic import BaseModel


class LocationData(BaseModel):
    """Latitude and longitude pair."""

    latitude: float
    longitude: float


class PredictionResponse(LocationData):
    """Prediction result returned by the API."""

    confidence: float
