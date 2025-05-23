from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    MODEL_PATH: str | None = None
    MAPBOX_TOKEN: str | None = None
    IMAGE_TTL_HOURS: int = 24

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
