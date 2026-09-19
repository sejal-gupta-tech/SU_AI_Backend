from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import validator


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:3000"
    PORT: int = 8000

    # MongoDB Configuration
    MONGO_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "sevenunique_ai_db"

    # Security Configuration
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    from pydantic import model_validator

    @model_validator(mode="after")
    def validate_jwt_secret(self) -> 'Settings':
        if not self.JWT_SECRET_KEY or self.JWT_SECRET_KEY == "your-super-secret-key-here":
            if self.ENVIRONMENT == "development":
                self.JWT_SECRET_KEY = "development-secret-key-unsafe"
            else:
                raise ValueError("JWT_SECRET_KEY must be set in production environment!")
        return self
        
    @property
    def JWT_SECRET(self) -> str:
        return self.JWT_SECRET_KEY

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # AI Configuration
    AI_PROVIDER: str = "mock"
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
