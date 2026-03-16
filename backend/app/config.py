from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application configuration settings.
    Load from environment variables or .env file.
    """
    
    # ==================== APP SETTINGS ====================
    PROJECT_NAME: str = "AI Text Classification API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # ==================== SECURITY ====================
    SECRET_KEY: str = "change-this-secret-key-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ==================== DATABASE ====================
    DATABASE_URL: str = "sqlite:///./backend/app/database/app.db"
    # For PostgreSQL in production:
    # DATABASE_URL: str = "postgresql://user:password@localhost:5432/dbname"
    
    # ==================== ML MODEL PATHS ====================
    MODEL_PATH: str = "backend/app/ml/models/text_classifier.joblib"
    LABEL_MAPPING_PATH: str = "backend/app/ml/models/label_mapping.json"
    TRAINING_DATA_PATH: str = "backend/app/ml/artifacts/combined_dataset.csv"
    
    # ==================== CORS ====================
    CORS_ORIGINS: list = ["*"]  # Configure properly in production
    # Example: ["http://localhost:3000", "https://yourdomain.com"]
    
    # ==================== RATE LIMITING ====================
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # ==================== LOGGING ====================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # ==================== PREDICTION LIMITS ====================
    MAX_TEXT_LENGTH: int = 10000
    MIN_TEXT_LENGTH: int = 5
    MAX_BATCH_SIZE: int = 100
    
    # ==================== PAGINATION ====================
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Ensures settings are loaded once per application lifecycle.
    """
    return Settings()


# Global settings instance
settings = get_settings()