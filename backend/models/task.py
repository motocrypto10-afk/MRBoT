"""
Task-related Pydantic models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class TaskBase(BaseModel):
    """Base task model"""
    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    priority: str = "medium"  # low, medium, high
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    """Create task request"""
    meeting_id: str

class TaskUpdate(BaseModel):
    """Update task request"""
    title: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None

class Task(TaskBase):
    """Complete task model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    meeting_id: str
    status: str = "pending"  # pending, in_progress, completed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True