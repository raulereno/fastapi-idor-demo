"""
Centralized application configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database configuration
    DATABASE_URL: str = "sqlite:///./users.db"
    
    # JWT security configuration
    SECRET_KEY: str = "your_very_secure_secret_key_here_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application configuration
    APP_NAME: str = "IDOR Vulnerability Demo"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"


# Global configuration instance
settings = Settings() 