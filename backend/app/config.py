from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Text Classification API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str  # no default — forces it to be set in .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    DATABASE_URL: str = "sqlite:///./backend/app/database/app.db"
    
    MODEL_PATH: str = "backend/app/ml/models/text_classifier.joblib"
    LABEL_MAPPING_PATH: str = "backend/app/ml/models/label_mapping.json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()