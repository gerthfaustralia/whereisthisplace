# api/api/core/config.py

from pydantic_settings import BaseSettings  # ← CHANGE THIS LINE
from typing import Optional, List


class Settings(BaseSettings):
    # API Settings
    app_name: str = "WhereIsThisPlace API"
    debug: bool = False
    api_version: str = "v1"
    
    # OpenAI Settings
    openai_api_key: Optional[str] = None
    
    # TorchServe Settings
    torchserve_url: str = "http://localhost:8080"
    torchserve_model_name: str = "where"
    torchserve_timeout: int = 60
    
    # Database Settings
    database_url: Optional[str] = None
    
    # CORS Settings
    cors_origins: List[str] = ["*"]
    
    # File Upload Settings
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = [".jpg", ".jpeg", ".png", ".webp"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()