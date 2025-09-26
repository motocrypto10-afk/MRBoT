"""
Message API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ...models.message import Message, MessageCreate
from ...models.common import BaseResponse
from ...core.db import get_database
from ...core.errors import map_exception_to_http
from ...core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/", response_model=List[Message])
async def get_messages():
    """Get all messages (legacy implementation)"""
    try:
        db = await get_database()
        messages_cursor = db.messages.find().sort("created_at", -1)
        messages = await messages_cursor.to_list(100)
        
        result = []
        for message in messages:
            message.pop('_id', None)
            if 'id' not in message:
                continue
            
            message_obj = Message(
                id=message['id'],
                meeting_id=message.get('meeting_id', ''),
                content=message.get('content', ''),
                type=message.get('type', 'highlight'),
                created_at=message.get('created_at'),
                updated_at=message.get('updated_at')
            )
            result.append(message_obj)
        
        logger.info("Messages fetched via API", count=len(result))
        return result
        
    except Exception as e:
        logger.error("Failed to get messages via API", error=str(e))
        raise map_exception_to_http(e)

@router.post("/", response_model=Message)
async def create_message(message: MessageCreate):
    """Create a new message"""
    try:
        db = await get_database()
        
        # Create message object
        message_obj = Message(
            meeting_id=message.meeting_id,
            content=message.content,
            type=message.type
        )
        
        result = await db.messages.insert_one(message_obj.dict())
        logger.info("Message created via API", message_id=message_obj.id)
        return message_obj
        
    except Exception as e:
        logger.error("Failed to create message via API", error=str(e))
        raise map_exception_to_http(e)

@router.get("/{message_id}", response_model=Message)
async def get_message(message_id: str):
    """Get a specific message"""
    try:
        db = await get_database()
        message_data = await db.messages.find_one({"id": message_id})
        
        if not message_data:
            raise HTTPException(status_code=404, detail="Message not found")
        
        message_data.pop('_id', None)
        return Message(**message_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get message via API", message_id=message_id, error=str(e))
        raise map_exception_to_http(e)

@router.delete("/{message_id}")
async def delete_message(message_id: str) -> BaseResponse:
    """Delete a message"""
    try:
        db = await get_database()
        result = await db.messages.delete_one({"id": message_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Message not found")
        
        logger.info("Message deleted via API", message_id=message_id)
        return BaseResponse(
            success=True,
            message="Message deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete message via API", message_id=message_id, error=str(e))
        raise map_exception_to_http(e)