"""
Recording session Pydantic models
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class RecordingStart(BaseModel):
    """Start recording request"""
    mode: str = "local"  # local, cloud, local_to_cloud
    allow_fallback: bool = True
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    meeting_id: Optional[str] = None

class RecordingHeartbeat(BaseModel):
    """Recording heartbeat request"""
    session_id: str
    device_id: str
    ts: str
    chunk_info: Optional[Dict[str, Any]] = None

class RecordingStop(BaseModel):
    """Stop recording request"""
    session_id: str
    final: bool = True
    stats: Optional[Dict[str, Any]] = Field(default_factory=dict)
    create_meeting: bool = True

class RecordingSession(BaseModel):
    """Recording session model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mode: str = "local"
    device_id: str
    user_id: Optional[str] = None
    meeting_id: Optional[str] = None
    status: str = "active"  # active, paused, stopped, failed, pending_sync
    allow_fallback: bool = True
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    audio_files: List[str] = Field(default_factory=list)
    markers: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    final_stats: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True