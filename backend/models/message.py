"""
Message-related Pydantic models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class MessageBase(BaseModel):
    """Base message model"""
    content: str
    type: str = "highlight"  # highlight, decision, action_item, note

class MessageCreate(MessageBase):
    """Create message request"""
    meeting_id: str

class Message(MessageBase):
    """Complete message model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    meeting_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True