"""Application configuration"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Google AI
    google_api_key: str
    google_project_id: Optional[str] = None
    
    # Application
    app_name: str = "health_triage_system"
    environment: str = "development"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./health_triage.db"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Model configuration
    model_name: str = "gemini-2.0-flash-exp"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
