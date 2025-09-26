"""
Meeting repository for database operations
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...models.meeting import Meeting, MeetingCreate, MeetingUpdate
from ...core.errors import NotFoundError, StorageError
from ...core.logging import get_logger

logger = get_logger(__name__)

class MeetingRepository:
    """Repository for meeting data operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.meetings

    async def create(self, meeting: Meeting) -> Meeting:
        """Create a new meeting"""
        try:
            meeting_data = meeting.dict()
            result = await self.collection.insert_one(meeting_data)
            logger.info("Meeting created", meeting_id=meeting.id, title=meeting.title)
            return meeting
        except Exception as e:
            logger.error("Failed to create meeting", error=str(e))
            raise StorageError(f"Failed to create meeting: {str(e)}")

    async def get_by_id(self, meeting_id: str) -> Optional[Meeting]:
        """Get meeting by ID"""
        try:
            meeting_data = await self.collection.find_one({"id": meeting_id})
            if not meeting_data:
                return None
            
            meeting_data.pop('_id', None)
            return Meeting(**meeting_data)
        except Exception as e:
            logger.error("Failed to get meeting", meeting_id=meeting_id, error=str(e))
            raise StorageError(f"Failed to get meeting: {str(e)}")

    async def get_all(self, limit: int = 100, skip: int = 0) -> List[Meeting]:
        """Get all meetings with pagination"""
        try:
            cursor = self.collection.find().sort("created_at", -1).skip(skip).limit(limit)
            meetings = []
            
            async for meeting_data in cursor:
                meeting_data.pop('_id', None)
                # Handle legacy data structure
                meeting_obj = Meeting(
                    id=meeting_data.get('id', str(meeting_data.get('_id', ''))),
                    title=meeting_data.get('title', 'Untitled Meeting'),
                    date=meeting_data.get('date', meeting_data.get('created_at', datetime.utcnow()).strftime('%Y-%m-%d %H:%M')),
                    summary=meeting_data.get('summary', 'Processing...'),
                    status=meeting_data.get('status', 'pending'),
                    audio_data=meeting_data.get('audio_data'),
                    transcript=meeting_data.get('transcript'),
                    action_items=meeting_data.get('action_items', []),
                    decisions=meeting_data.get('decisions', []),
                    participants=meeting_data.get('participants', []),
                    recording_session_id=meeting_data.get('recording_session_id'),
                    transcription_job_id=meeting_data.get('transcription_job_id'),
                    created_at=meeting_data.get('created_at', datetime.utcnow()),
                    updated_at=meeting_data.get('updated_at', datetime.utcnow())
                )
                meetings.append(meeting_obj)
            
            return meetings
        except Exception as e:
            logger.error("Failed to get meetings", error=str(e))
            raise StorageError(f"Failed to get meetings: {str(e)}")

    async def update(self, meeting_id: str, update_data: MeetingUpdate) -> Optional[Meeting]:
        """Update meeting"""
        try:
            # Filter out None values
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            update_dict['updated_at'] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"id": meeting_id},
                {"$set": update_dict}
            )
            
            if result.matched_count == 0:
                return None
            
            logger.info("Meeting updated", meeting_id=meeting_id, 
                       updated_fields=list(update_dict.keys()))
            
            return await self.get_by_id(meeting_id)
            
        except Exception as e:
            logger.error("Failed to update meeting", meeting_id=meeting_id, error=str(e))
            raise StorageError(f"Failed to update meeting: {str(e)}")

    async def update_status(self, meeting_id: str, status: str) -> bool:
        """Update meeting status"""
        try:
            result = await self.collection.update_one(
                {"id": meeting_id},
                {"$set": {"status": status, "updated_at": datetime.utcnow()}}
            )
            
            if result.matched_count == 0:
                raise NotFoundError(f"Meeting {meeting_id} not found")
            
            logger.info("Meeting status updated", meeting_id=meeting_id, status=status)
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error("Failed to update meeting status", 
                        meeting_id=meeting_id, error=str(e))
            raise StorageError(f"Failed to update meeting status: {str(e)}")

    async def add_transcription_results(
        self, 
        meeting_id: str, 
        transcript: str, 
        summary: str, 
        action_items: List[str], 
        decisions: List[str]
    ) -> bool:
        """Add transcription results to meeting"""
        try:
            update_data = {
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "decisions": decisions,
                "status": "completed",
                "updated_at": datetime.utcnow()
            }
            
            result = await self.collection.update_one(
                {"id": meeting_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise NotFoundError(f"Meeting {meeting_id} not found")
            
            logger.info("Transcription results added", meeting_id=meeting_id)
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error("Failed to add transcription results", 
                        meeting_id=meeting_id, error=str(e))
            raise StorageError(f"Failed to add transcription results: {str(e)}")

    async def delete(self, meeting_id: str) -> bool:
        """Delete meeting"""
        try:
            result = await self.collection.delete_one({"id": meeting_id})
            
            if result.deleted_count == 0:
                return False
            
            logger.info("Meeting deleted", meeting_id=meeting_id)
            return True
            
        except Exception as e:
            logger.error("Failed to delete meeting", meeting_id=meeting_id, error=str(e))
            raise StorageError(f"Failed to delete meeting: {str(e)}")

    async def search_meetings(self, query: str, limit: int = 20) -> List[Meeting]:
        """Search meetings by title or content"""
        try:
            # Simple text search - could be enhanced with MongoDB text index
            search_query = {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"summary": {"$regex": query, "$options": "i"}},
                    {"transcript": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = self.collection.find(search_query).sort("created_at", -1).limit(limit)
            meetings = []
            
            async for meeting_data in cursor:
                meeting_data.pop('_id', None)
                meetings.append(Meeting(**meeting_data))
            
            logger.info("Meeting search completed", query=query, results=len(meetings))
            return meetings
            
        except Exception as e:
            logger.error("Failed to search meetings", query=query, error=str(e))
            raise StorageError(f"Failed to search meetings: {str(e)}")