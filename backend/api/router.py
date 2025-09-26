"""
Main API router that mounts all versioned routes
"""
from fastapi import APIRouter
from .v1 import recordings, meetings, tasks, messages, settings, health

def create_api_router() -> APIRouter:
    """Create main API router with all endpoints"""
    
    # Create main router with /api prefix
    api_router = APIRouter(prefix="/api")
    
    # Mount v1 routes
    v1_router = APIRouter(prefix="/v1")
    
    # Health and system endpoints
    v1_router.include_router(health.router, tags=["health"])
    
    # Core business logic endpoints
    v1_router.include_router(recordings.router, prefix="/recordings", tags=["recordings"])
    v1_router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
    v1_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
    v1_router.include_router(messages.router, prefix="/messages", tags=["messages"])
    v1_router.include_router(settings.router, prefix="/settings", tags=["settings"])
    
    # Mount v1 router to main API router
    api_router.include_router(v1_router)
    
    # Also mount legacy routes directly to /api for backward compatibility
    api_router.include_router(health.router, tags=["health-legacy"])
    api_router.include_router(recordings.router, prefix="/recordings", tags=["recordings-legacy"])
    api_router.include_router(meetings.router, prefix="/meetings", tags=["meetings-legacy"])
    api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks-legacy"])
    api_router.include_router(messages.router, prefix="/messages", tags=["messages-legacy"])
    api_router.include_router(settings.router, prefix="/settings", tags=["settings-legacy"])
    
    return api_router