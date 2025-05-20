from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    MODEL_PATH: str
    MAPBOX_TOKEN: str
    IMAGE_TTL_HOURS: int = 24

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
