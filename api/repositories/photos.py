import asyncpg
from typing import Optional, Any

async def insert_prediction(pool: Any, lat: float, lon: float, score: float,
                            bias_warning: Optional[str], source: str) -> None:
    """Insert a prediction record into the photos table."""
    await pool.execute(
        "INSERT INTO photos (lat, lon, score, bias_warning, source) VALUES ($1, $2, $3, $4, $5)",
        lat, lon, score, bias_warning, source
    )
