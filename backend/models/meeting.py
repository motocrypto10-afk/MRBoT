"""
Meeting-related Pydantic models
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class MeetingBase(BaseModel):
    """Base meeting model"""
    title: str
    date: Optional[str] = None
    participants: List[str] = Field(default_factory=list)

class MeetingCreate(MeetingBase):
    """Create meeting request"""
    audio_data: Optional[str] = None  # base64 encoded audio
    recording_session_id: Optional[str] = None

class MeetingUpdate(BaseModel):
    """Update meeting request"""
    title: Optional[str] = None
    participants: Optional[List[str]] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    action_items: Optional[List[str]] = None
    decisions: Optional[List[str]] = None
    status: Optional[str] = None

class Meeting(MeetingBase):
    """Complete meeting model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audio_data: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    action_items: List[str] = Field(default_factory=list)
    decisions: List[str] = Field(default_factory=list)
    status: str = "pending"  # pending, processing, completed, error
    recording_session_id: Optional[str] = None
    transcription_job_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True