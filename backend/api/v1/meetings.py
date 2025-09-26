"""
Meeting API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any

from ...models.meeting import Meeting, MeetingCreate, MeetingUpdate
from ...models.common import BaseResponse
from ...services.meetings import MeetingService, MeetingRepository
from ...core.db import get_database
from ...core.errors import map_exception_to_http
from ...core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

async def get_meeting_service():
    """Dependency to get meeting service"""
    db = await get_database()
    repo = MeetingRepository(db)
    return MeetingService(repo)

@router.get("/", response_model=List[Meeting])
async def get_meetings(
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    service: MeetingService = Depends(get_meeting_service)
):
    """Get all meetings with pagination"""
    try:
        meetings = await service.get_all_meetings(limit=limit, skip=skip)
        logger.info("Meetings fetched via API", count=len(meetings))
        return meetings
    except Exception as e:
        logger.error("Failed to get meetings via API", error=str(e))
        raise map_exception_to_http(e)

@router.post("/", response_model=Meeting)
async def create_meeting(
    meeting: MeetingCreate,
    service: MeetingService = Depends(get_meeting_service)
):
    """Create a new meeting"""
    try:
        created_meeting = await service.create_meeting(meeting)
        logger.info("Meeting created via API", 
                   meeting_id=created_meeting.id, title=created_meeting.title)
        return created_meeting
    except Exception as e:
        logger.error("Failed to create meeting via API", error=str(e))
        raise map_exception_to_http(e)

@router.get("/{meeting_id}", response_model=Meeting)
async def get_meeting(
    meeting_id: str,
    service: MeetingService = Depends(get_meeting_service)
):
    """Get a specific meeting"""
    try:
        meeting = await service.get_meeting(meeting_id)
        return meeting
    except Exception as e:
        logger.error("Failed to get meeting via API", 
                    meeting_id=meeting_id, error=str(e))
        raise map_exception_to_http(e)

@router.patch("/{meeting_id}", response_model=Meeting)
async def update_meeting(
    meeting_id: str,
    update_data: MeetingUpdate,
    service: MeetingService = Depends(get_meeting_service)
):
    """Update a meeting"""
    try:
        updated_meeting = await service.update_meeting(meeting_id, update_data)
        logger.info("Meeting updated via API", meeting_id=meeting_id)
        return updated_meeting
    except Exception as e:
        logger.error("Failed to update meeting via API", 
                    meeting_id=meeting_id, error=str(e))
        raise map_exception_to_http(e)

@router.post("/{meeting_id}/process")
async def process_meeting(
    meeting_id: str,
    service: MeetingService = Depends(get_meeting_service)
) -> Dict[str, str]:
    """Process meeting for AI summarization (legacy endpoint)"""
    try:
        result = await service.process_meeting(meeting_id)
        logger.info("Meeting processing started via API", meeting_id=meeting_id)
        return result
    except Exception as e:
        logger.error("Failed to process meeting via API", 
                    meeting_id=meeting_id, error=str(e))
        raise map_exception_to_http(e)

@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: str,
    service: MeetingService = Depends(get_meeting_service)
) -> BaseResponse:
    """Delete a meeting"""
    try:
        await service.delete_meeting(meeting_id)
        logger.info("Meeting deleted via API", meeting_id=meeting_id)
        return BaseResponse(
            success=True,
            message="Meeting deleted successfully"
        )
    except Exception as e:
        logger.error("Failed to delete meeting via API", 
                    meeting_id=meeting_id, error=str(e))
        raise map_exception_to_http(e)

@router.get("/search/")
async def search_meetings(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    service: MeetingService = Depends(get_meeting_service)
) -> List[Meeting]:
    """Search meetings by title or content"""
    try:
        results = await service.search_meetings(q, limit)
        logger.info("Meeting search completed via API", 
                   query=q, results=len(results))
        return results
    except Exception as e:
        logger.error("Failed to search meetings via API", 
                    query=q, error=str(e))
        raise map_exception_to_http(e)