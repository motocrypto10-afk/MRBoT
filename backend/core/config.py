"""
Configuration and environment variable management
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

class Settings(BaseSettings):
    # Database settings
    mongo_url: str = "mongodb://127.0.0.1:27017"
    db_name: str = "emergent"
    
    # AI Integration
    emergent_llm_key: Optional[str] = None
    
    # Service settings
    app_name: str = "BotMR API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Queue settings
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    
    # Upload settings
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    allowed_audio_types: list = ["audio/wav", "audio/mp3", "audio/m4a", "audio/mpeg"]
    
    # Feature flags
    enable_local_transcription: bool = False
    enable_cloud_fallback: bool = True
    enable_encryption: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @classmethod
    def load(cls) -> 'Settings':
        return cls()

# Global settings instance
settings = Settings.load()

def get_settings() -> Settings:
    """Get application settings"""
    return settings