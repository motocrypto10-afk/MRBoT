"""
Settings-related Pydantic models
"""
from pydantic import BaseModel, Field
from typing import Optional
import uuid

class UserSettingsUpdate(BaseModel):
    """Update user settings request"""
    openai_api_key: Optional[str] = None
    preferred_language: Optional[str] = None
    auto_delete_days: Optional[int] = None
    cloud_sync_enabled: Optional[bool] = None
    privacy_mode: Optional[bool] = None
    enable_redaction: Optional[bool] = None
    retention_policy_days: Optional[int] = None

class UserSettings(BaseModel):
    """User settings model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    openai_api_key: Optional[str] = None
    preferred_language: str = "en"
    auto_delete_days: Optional[int] = None
    cloud_sync_enabled: bool = True
    privacy_mode: bool = False
    enable_redaction: bool = False
    retention_policy_days: Optional[int] = 30

    class Config:
        from_attributes = True