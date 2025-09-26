"""
Recording session API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from ...models.recording import RecordingStart, RecordingHeartbeat, RecordingStop
from ...models.common import BaseResponse
from ...services.recordings import RecordingService, RecordingRepository
from ...core.db import get_database
from ...core.errors import map_exception_to_http
from ...core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

async def get_recording_service():
    """Dependency to get recording service"""
    db = await get_database()
    repo = RecordingRepository(db)
    return RecordingService(repo)

@router.post("/start")
async def start_recording(
    recording: RecordingStart,
    service: RecordingService = Depends(get_recording_service)
) -> Dict[str, Any]:
    """Start a new recording session"""
    try:
        result = await service.start_recording(recording)
        logger.info("Recording started via API", session_id=result.get("sessionId"))
        return result
    except Exception as e:
        logger.error("Failed to start recording via API", error=str(e))
        raise map_exception_to_http(e)

@router.post("/heartbeat")
async def recording_heartbeat(
    heartbeat: RecordingHeartbeat,
    service: RecordingService = Depends(get_recording_service)
) -> Dict[str, bool]:
    """Update recording session heartbeat"""
    try:
        result = await service.update_heartbeat(heartbeat)
        return result
    except Exception as e:
        logger.error("Failed to update heartbeat via API", 
                    session_id=heartbeat.session_id, error=str(e))
        raise map_exception_to_http(e)

@router.post("/stop")
async def stop_recording(
    stop_data: RecordingStop,
    service: RecordingService = Depends(get_recording_service)
) -> Dict[str, Any]:
    """Stop recording session and trigger processing"""
    try:
        result = await service.stop_recording(stop_data)
        logger.info("Recording stopped via API", session_id=stop_data.session_id)
        return result
    except Exception as e:
        logger.error("Failed to stop recording via API", 
                    session_id=stop_data.session_id, error=str(e))
        raise map_exception_to_http(e)

@router.get("/{session_id}/status")
async def get_recording_status(
    session_id: str,
    service: RecordingService = Depends(get_recording_service)
) -> Dict[str, Any]:
    """Get recording session status"""
    try:
        result = await service.get_recording_status(session_id)
        return result
    except Exception as e:
        logger.error("Failed to get recording status via API", 
                    session_id=session_id, error=str(e))
        raise map_exception_to_http(e)

# TODO: Add upload endpoint for audio chunks
@router.post("/{session_id}/upload/chunk")
async def upload_audio_chunk(
    session_id: str,
    # chunk_data: UploadFile = File(...),
    service: RecordingService = Depends(get_recording_service)
) -> BaseResponse:
    """Upload audio chunk for recording session"""
    # This is a placeholder for chunked file upload
    return BaseResponse(
        success=True,
        message="Audio chunk upload endpoint (placeholder)"
    )