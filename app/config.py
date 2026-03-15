# ----------------------------------------------------------------------------
# FILE: auth-service/app/config.py
# ----------------------------------------------------------------------------
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    SERVICE_NAME: str = "auth-service"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_SECONDS: int = 3600
    JWT_REFRESH_EXPIRY_SECONDS: int = 2592000  # 30 days
    
    # API Keys
    API_KEY_PREFIX: str = "sk_"
    API_KEY_LENGTH: int = 32
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_LOGIN: int = 5
    RATE_LIMIT_REGISTER: int = 3
    RATE_LIMIT_TOKEN: int = 10
    
    # Password Policy
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
