"""
Meeting business logic service
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...models.meeting import Meeting, MeetingCreate, MeetingUpdate
from ...core.errors import NotFoundError, ValidationError, ProcessingError
from ...core.logging import get_logger
from ...core.queue import get_queue
from .repo import MeetingRepository

logger = get_logger(__name__)

class MeetingService:
    """Service for meeting management"""
    
    def __init__(self, repo: MeetingRepository):
        self.repo = repo

    async def create_meeting(self, meeting_data: MeetingCreate) -> Meeting:
        """Create a new meeting"""
        try:
            # Validate input
            if not meeting_data.title.strip():
                raise ValidationError("Meeting title cannot be empty")
            
            # Create meeting object
            meeting = Meeting(
                title=meeting_data.title,
                date=meeting_data.date or datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
                participants=meeting_data.participants,
                audio_data=meeting_data.audio_data,
                recording_session_id=meeting_data.recording_session_id,
                status="pending"
            )
            
            # Save to database
            created_meeting = await self.repo.create(meeting)
            
            # If audio data is provided, enqueue for processing
            if meeting_data.audio_data:
                queue = await get_queue()
                await queue.enqueue(
                    topic="meeting.process",
                    payload={
                        "meeting_id": created_meeting.id,
                        "audio_data": meeting_data.audio_data
                    },
                    priority=2
                )
                
                # Update status to processing
                await self.repo.update_status(created_meeting.id, "processing")
                created_meeting.status = "processing"
            
            logger.info("Meeting created successfully", 
                       meeting_id=created_meeting.id,
                       title=created_meeting.title,
                       has_audio=bool(meeting_data.audio_data))
            
            return created_meeting
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error("Failed to create meeting", error=str(e))
            raise ProcessingError(f"Failed to create meeting: {str(e)}")

    async def create_meeting_from_recording(
        self, 
        title: str, 
        recording_session_id: str
    ) -> Meeting:
        """Create meeting from recording session"""
        try:
            meeting = Meeting(
                title=title,
                date=datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
                recording_session_id=recording_session_id,
                status="processing"  # Will be processed when transcription completes
            )
            
            created_meeting = await self.repo.create(meeting)
            
            logger.info("Meeting created from recording", 
                       meeting_id=created_meeting.id,
                       recording_session_id=recording_session_id)
            
            return created_meeting
            
        except Exception as e:
            logger.error("Failed to create meeting from recording", 
                        recording_session_id=recording_session_id, error=str(e))
            raise ProcessingError(f"Failed to create meeting from recording: {str(e)}")

    async def get_meeting(self, meeting_id: str) -> Meeting:
        """Get meeting by ID"""
        try:
            meeting = await self.repo.get_by_id(meeting_id)
            if not meeting:
                raise NotFoundError(f"Meeting {meeting_id} not found")
            
            return meeting
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error("Failed to get meeting", meeting_id=meeting_id, error=str(e))
            raise ProcessingError(f"Failed to get meeting: {str(e)}")

    async def get_all_meetings(self, limit: int = 100, skip: int = 0) -> List[Meeting]:
        """Get all meetings with pagination"""
        try:
            return await self.repo.get_all(limit=limit, skip=skip)
        except Exception as e:
            logger.error("Failed to get meetings", error=str(e))
            raise ProcessingError(f"Failed to get meetings: {str(e)}")

    async def update_meeting(self, meeting_id: str, update_data: MeetingUpdate) -> Meeting:
        """Update meeting"""
        try:
            # Validate that meeting exists
            existing_meeting = await self.repo.get_by_id(meeting_id)
            if not existing_meeting:
                raise NotFoundError(f"Meeting {meeting_id} not found")
            
            # Update meeting
            updated_meeting = await self.repo.update(meeting_id, update_data)
            if not updated_meeting:
                raise NotFoundError(f"Meeting {meeting_id} not found")
            
            logger.info("Meeting updated", meeting_id=meeting_id)
            return updated_meeting
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error("Failed to update meeting", meeting_id=meeting_id, error=str(e))
            raise ProcessingError(f"Failed to update meeting: {str(e)}")

    async def process_meeting(self, meeting_id: str) -> Dict[str, str]:
        """Process meeting for AI summarization (legacy method)"""
        try:
            meeting = await self.repo.get_by_id(meeting_id)
            if not meeting:
                raise NotFoundError(f"Meeting {meeting_id} not found")
            
            if not meeting.audio_data:
                raise ValidationError("No audio data found for processing")
            
            # Update status to processing
            await self.repo.update_status(meeting_id, "processing")
            
            # Enqueue for processing
            queue = await get_queue()
            await queue.enqueue(
                topic="meeting.process",
                payload={
                    "meeting_id": meeting_id,
                    "audio_data": meeting.audio_data
                },
                priority=2
            )
            
            logger.info("Meeting queued for processing", meeting_id=meeting_id)
            return {"message": "Meeting processing started"}
            
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error("Failed to process meeting", meeting_id=meeting_id, error=str(e))
            # Update status to error
            await self.repo.update_status(meeting_id, "error")
            raise ProcessingError(f"Failed to process meeting: {str(e)}")

    async def add_transcription_results(
        self,
        meeting_id: str,
        transcript: str,
        summary: str,
        action_items: List[str],
        decisions: List[str]
    ) -> bool:
        """Add transcription and AI analysis results to meeting"""
        try:
            await self.repo.add_transcription_results(
                meeting_id, transcript, summary, action_items, decisions
            )
            
            logger.info("Transcription results added to meeting", meeting_id=meeting_id)
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error("Failed to add transcription results", 
                        meeting_id=meeting_id, error=str(e))
            raise ProcessingError(f"Failed to add transcription results: {str(e)}")

    async def delete_meeting(self, meeting_id: str) -> bool:
        """Delete meeting"""
        try:
            deleted = await self.repo.delete(meeting_id)
            if not deleted:
                raise NotFoundError(f"Meeting {meeting_id} not found")
            
            logger.info("Meeting deleted", meeting_id=meeting_id)
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error("Failed to delete meeting", meeting_id=meeting_id, error=str(e))
            raise ProcessingError(f"Failed to delete meeting: {str(e)}")

    async def search_meetings(self, query: str, limit: int = 20) -> List[Meeting]:
        """Search meetings"""
        try:
            if not query.strip():
                raise ValidationError("Search query cannot be empty")
            
            return await self.repo.search_meetings(query, limit)
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error("Failed to search meetings", query=query, error=str(e))
            raise ProcessingError(f"Failed to search meetings: {str(e)}")