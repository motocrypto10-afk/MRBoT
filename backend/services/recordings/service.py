"""
Recording session business logic service
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from ...models.recording import RecordingSession, RecordingStart, RecordingHeartbeat, RecordingStop
from ...core.errors import NotFoundError, ValidationError, ConflictError
from ...core.logging import get_logger
from ...core.security import get_security_manager
from .repo import RecordingRepository

logger = get_logger(__name__)

class RecordingService:
    """Service for recording session management"""
    
    def __init__(self, repo: RecordingRepository):
        self.repo = repo
        self.security = get_security_manager()

    async def start_recording(self, recording_request: RecordingStart) -> Dict[str, Any]:
        """Start a new recording session"""
        try:
            # Validate request
            if not recording_request.metadata.get('deviceId'):
                raise ValidationError("Device ID is required")
            
            device_id = recording_request.metadata['deviceId']
            
            # Check for existing active sessions on device
            active_sessions = await self.repo.get_active_sessions(device_id)
            if active_sessions:
                # For now, allow multiple sessions but log warning
                logger.warning("Device has active recording sessions", 
                              device_id=device_id, 
                              active_count=len(active_sessions))
            
            # Create new recording session
            session = RecordingSession(
                mode=recording_request.mode,
                device_id=device_id,
                user_id=recording_request.metadata.get('userId'),
                meeting_id=recording_request.meeting_id,
                allow_fallback=recording_request.allow_fallback,
                metadata=recording_request.metadata,
                status="active"
            )
            
            # Save to database
            created_session = await self.repo.create(session)
            
            # Generate upload URLs (TODO: implement actual file upload endpoints)
            upload_urls = []
            if recording_request.mode in ["cloud", "local_to_cloud"]:
                upload_urls = [
                    f"/api/recordings/{created_session.session_id}/upload/chunk"
                ]
            
            logger.info("Recording session started", 
                       session_id=created_session.session_id,
                       mode=recording_request.mode,
                       device_id=device_id)
            
            return {
                "sessionId": created_session.session_id,
                "uploadUrls": upload_urls,
                "status": "active",
                "mode": created_session.mode,
                "allowFallback": created_session.allow_fallback
            }
            
        except (ValidationError, ConflictError):
            raise
        except Exception as e:
            logger.error("Failed to start recording", error=str(e))
            raise ProcessingError(f"Failed to start recording: {str(e)}")

    async def update_heartbeat(self, heartbeat: RecordingHeartbeat) -> Dict[str, bool]:
        """Update recording session heartbeat"""
        try:
            # Validate session exists and is active
            session = await self.repo.get_by_session_id(heartbeat.session_id)
            if not session:
                raise NotFoundError(f"Recording session {heartbeat.session_id} not found")
            
            if session.status not in ["active", "paused"]:
                raise ConflictError(f"Recording session is {session.status}, cannot update heartbeat")
            
            # Update heartbeat
            await self.repo.update_heartbeat(heartbeat.session_id)
            
            # TODO: Process chunk info if provided
            if heartbeat.chunk_info:
                logger.debug("Processing chunk info", 
                           session_id=heartbeat.session_id,
                           chunk_info=heartbeat.chunk_info)
            
            logger.debug("Heartbeat updated", session_id=heartbeat.session_id)
            
            return {"ok": True}
            
        except (NotFoundError, ConflictError):
            raise
        except Exception as e:
            logger.error("Failed to update heartbeat", 
                        session_id=heartbeat.session_id, error=str(e))
            raise ProcessingError(f"Failed to update heartbeat: {str(e)}")

    async def stop_recording(self, stop_data: RecordingStop) -> Dict[str, Any]:
        """Stop recording session and trigger processing"""
        try:
            # Get session
            session = await self.repo.get_by_session_id(stop_data.session_id)
            if not session:
                raise NotFoundError(f"Recording session {stop_data.session_id} not found")
            
            if session.status not in ["active", "paused"]:
                logger.warning("Attempting to stop non-active session", 
                              session_id=stop_data.session_id,
                              current_status=session.status)
            
            # Update session to stopped
            await self.repo.update_status(
                stop_data.session_id,
                "stopped",
                ended_at=datetime.utcnow(),
                final_stats=stop_data.stats
            )
            
            meeting_id = session.meeting_id
            
            # If no meeting linked and should create one
            if not meeting_id and stop_data.create_meeting:
                # Import here to avoid circular dependency
                from ..meetings.service import MeetingService
                from ..meetings.repo import MeetingRepository
                from ...core.db import get_database
                
                db = await get_database()
                meeting_repo = MeetingRepository(db)
                meeting_service = MeetingService(meeting_repo)
                
                meeting_title = f"Meeting {session.started_at.strftime('%m/%d/%Y, %H:%M:%S')}"
                meeting = await meeting_service.create_meeting_from_recording(
                    title=meeting_title,
                    recording_session_id=stop_data.session_id
                )
                meeting_id = meeting.id
                
                # Link meeting to recording session
                await self.repo.link_meeting(stop_data.session_id, meeting_id)
            
            logger.info("Recording session stopped", 
                       session_id=stop_data.session_id,
                       meeting_id=meeting_id)
            
            return {
                "message": "Recording stopped successfully",
                "sessionId": stop_data.session_id,
                "meetingId": meeting_id,
                "status": "stopped"
            }
            
        except (NotFoundError, ConflictError):
            raise
        except Exception as e:
            logger.error("Failed to stop recording", 
                        session_id=stop_data.session_id, error=str(e))
            raise ProcessingError(f"Failed to stop recording: {str(e)}")

    async def get_recording_status(self, session_id: str) -> Dict[str, Any]:
        """Get recording session status"""
        try:
            session = await self.repo.get_by_session_id(session_id)
            if not session:
                raise NotFoundError(f"Recording session {session_id} not found")
            
            return {
                "sessionId": session_id,
                "status": session.status,
                "mode": session.mode,
                "uploadedChunks": len(session.audio_files),
                "transcriptState": "pending",  # TODO: Get actual transcript status
                "startedAt": session.started_at,
                "endedAt": session.ended_at,
                "lastHeartbeat": session.last_heartbeat,
                "metadata": session.metadata
            }
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error("Failed to get recording status", 
                        session_id=session_id, error=str(e))
            raise ProcessingError(f"Failed to get recording status: {str(e)}")

    async def cleanup_old_sessions(self, days: int = 30) -> int:
        """Clean up old recording sessions"""
        return await self.repo.cleanup_old_sessions(days)