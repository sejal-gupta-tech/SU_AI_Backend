from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = ["*"]
    PORT: int = 8000

    # MongoDB Configuration
    MONGO_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "sevenunique_ai_db"

    # Security Configuration
    JWT_SECRET: str = "your-super-secret-key-here"  # Default for local development
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # AI Configuration
    AI_PROVIDER: str = "mock"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
