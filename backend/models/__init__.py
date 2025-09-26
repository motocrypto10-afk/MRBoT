"""
Pydantic models and DTOs for BotMR API
"""
from .meeting import Meeting, MeetingCreate, MeetingUpdate
from .recording import RecordingSession, RecordingStart, RecordingHeartbeat, RecordingStop
from .task import Task, TaskCreate, TaskUpdate
from .message import Message, MessageCreate
from .settings import UserSettings, UserSettingsUpdate
from .transcription import TranscriptionJob, TranscriptionResult
from .common import BaseResponse, HealthCheck

__all__ = [
    'Meeting', 'MeetingCreate', 'MeetingUpdate',
    'RecordingSession', 'RecordingStart', 'RecordingHeartbeat', 'RecordingStop',
    'Task', 'TaskCreate', 'TaskUpdate',
    'Message', 'MessageCreate',
    'UserSettings', 'UserSettingsUpdate',
    'TranscriptionJob', 'TranscriptionResult',
    'BaseResponse', 'HealthCheck'
]