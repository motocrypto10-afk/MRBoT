"""
Transcription-related Pydantic models
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class TranscriptionJobCreate(BaseModel):
    """Create transcription job request"""
    meeting_id: str
    audio_file_path: str
    language: str = "en"
    enable_diarization: bool = True
    enable_redaction: bool = False

class TranscriptionJob(BaseModel):
    """Transcription job model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    meeting_id: str
    audio_file_path: str
    language: str = "en"
    enable_diarization: bool = True
    enable_redaction: bool = False
    status: str = "pending"  # pending, processing, completed, failed
    progress: float = 0.0
    stages_completed: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SpeakerSegment(BaseModel):
    """Speaker segment in transcription"""
    speaker_id: str
    speaker_name: Optional[str] = None
    start_time: float
    end_time: float
    text: str
    confidence: float

class TranscriptionResult(BaseModel):
    """Transcription job result"""
    job_id: str
    raw_transcript: str
    segments: List[SpeakerSegment] = Field(default_factory=list)
    summary: Optional[str] = None
    action_items: List[str] = Field(default_factory=list)
    decisions: List[str] = Field(default_factory=list)
    key_topics: List[str] = Field(default_factory=list)
    speakers: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    redacted_content: Optional[str] = None

    class Config:
        from_attributes = True