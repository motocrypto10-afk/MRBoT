"""
Settings API endpoints
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from ...models.settings import UserSettings, UserSettingsUpdate
from ...models.common import BaseResponse
from ...core.db import get_database
from ...core.errors import map_exception_to_http
from ...core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/", response_model=UserSettings)
async def get_settings():
    """Get user settings (legacy implementation)"""
    try:
        db = await get_database()
        settings = await db.settings.find_one() or {}
        
        return UserSettings(
            id=settings.get('id', ''),
            openai_api_key=settings.get('openai_api_key'),
            preferred_language=settings.get('preferred_language', 'en'),
            auto_delete_days=settings.get('auto_delete_days'),
            cloud_sync_enabled=settings.get('cloud_sync_enabled', True),
            privacy_mode=settings.get('privacy_mode', False),
            enable_redaction=settings.get('enable_redaction', False),
            retention_policy_days=settings.get('retention_policy_days', 30)
        )
        
    except Exception as e:
        logger.error("Failed to get settings via API", error=str(e))
        raise map_exception_to_http(e)

@router.post("/")
async def update_settings(settings: UserSettings) -> BaseResponse:
    """Update user settings (legacy implementation)"""
    try:
        db = await get_database()
        
        await db.settings.update_one(
            {},
            {"$set": settings.dict()},
            upsert=True
        )
        
        logger.info("Settings updated via API")
        return BaseResponse(
            success=True,
            message="Settings updated successfully"
        )
        
    except Exception as e:
        logger.error("Failed to update settings via API", error=str(e))
        raise map_exception_to_http(e)

@router.patch("/", response_model=UserSettings)
async def patch_settings(update_data: UserSettingsUpdate):
    """Partially update user settings"""
    try:
        db = await get_database()
        
        # Filter out None values
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        
        if not update_dict:
            # Return current settings if no updates
            settings = await db.settings.find_one() or {}
            return UserSettings(**settings)
        
        # Update settings
        await db.settings.update_one(
            {},
            {"$set": update_dict},
            upsert=True
        )
        
        # Return updated settings
        settings = await db.settings.find_one() or {}
        
        logger.info("Settings partially updated via API", fields=list(update_dict.keys()))
        return UserSettings(**settings)
        
    except Exception as e:
        logger.error("Failed to patch settings via API", error=str(e))
        raise map_exception_to_http(e)