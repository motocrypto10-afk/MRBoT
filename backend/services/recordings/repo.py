"""
Recording session repository for database operations
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.recording import RecordingSession
from core.errors import NotFoundError, StorageError
from core.logging import get_logger

logger = get_logger(__name__)

class RecordingRepository:
    """Repository for recording session data operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.recording_sessions

    async def create(self, session: RecordingSession) -> RecordingSession:
        """Create a new recording session"""
        try:
            session_data = session.dict()
            result = await self.collection.insert_one(session_data)
            logger.info("Recording session created", session_id=session.session_id)
            return session
        except Exception as e:
            logger.error("Failed to create recording session", error=str(e))
            raise StorageError(f"Failed to create recording session: {str(e)}")

    async def get_by_session_id(self, session_id: str) -> Optional[RecordingSession]:
        """Get recording session by session ID"""
        try:
            session_data = await self.collection.find_one({"session_id": session_id})
            if not session_data:
                return None
            
            session_data.pop('_id', None)
            return RecordingSession(**session_data)
        except Exception as e:
            logger.error("Failed to get recording session", session_id=session_id, error=str(e))
            raise StorageError(f"Failed to get recording session: {str(e)}")

    async def update_status(self, session_id: str, status: str, **kwargs) -> bool:
        """Update recording session status"""
        try:
            update_data = {"status": status, "updated_at": datetime.utcnow()}
            update_data.update(kwargs)
            
            result = await self.collection.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise NotFoundError(f"Recording session {session_id} not found")
            
            logger.info("Recording session status updated", 
                       session_id=session_id, status=status)
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error("Failed to update recording session", 
                        session_id=session_id, error=str(e))
            raise StorageError(f"Failed to update recording session: {str(e)}")

    async def update_heartbeat(self, session_id: str) -> bool:
        """Update recording session heartbeat"""
        return await self.update_status(
            session_id, 
            "active", 
            last_heartbeat=datetime.utcnow()
        )

    async def add_audio_file(self, session_id: str, file_path: str) -> bool:
        """Add audio file to recording session"""
        try:
            result = await self.collection.update_one(
                {"session_id": session_id},
                {"$push": {"audio_files": file_path}}
            )
            
            if result.matched_count == 0:
                raise NotFoundError(f"Recording session {session_id} not found")
            
            logger.info("Audio file added to session", 
                       session_id=session_id, file_path=file_path)
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error("Failed to add audio file", 
                        session_id=session_id, error=str(e))
            raise StorageError(f"Failed to add audio file: {str(e)}")

    async def link_meeting(self, session_id: str, meeting_id: str) -> bool:
        """Link recording session to meeting"""
        return await self.update_status(session_id, None, meeting_id=meeting_id)

    async def get_active_sessions(self, device_id: Optional[str] = None) -> List[RecordingSession]:
        """Get active recording sessions"""
        try:
            query = {"status": {"$in": ["active", "paused"]}}
            if device_id:
                query["device_id"] = device_id
            
            cursor = self.collection.find(query)
            sessions = []
            
            async for session_data in cursor:
                session_data.pop('_id', None)
                sessions.append(RecordingSession(**session_data))
            
            return sessions
            
        except Exception as e:
            logger.error("Failed to get active sessions", error=str(e))
            raise StorageError(f"Failed to get active sessions: {str(e)}")

    async def cleanup_old_sessions(self, days: int = 30) -> int:
        """Clean up old recording sessions"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = await self.collection.delete_many({
                "created_at": {"$lt": cutoff_date},
                "status": {"$in": ["stopped", "failed", "completed"]}
            })
            
            logger.info("Cleaned up old recording sessions", 
                       deleted_count=result.deleted_count)
            return result.deleted_count
            
        except Exception as e:
            logger.error("Failed to cleanup old sessions", error=str(e))
            raise StorageError(f"Failed to cleanup old sessions: {str(e)}")