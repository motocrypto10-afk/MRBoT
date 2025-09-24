from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import base64
import aiofiles
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="BotMR API", description="Meeting Recording and AI Summarization API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class Meeting(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    date: str
    audio_data: Optional[str] = None  # base64 encoded audio
    transcript: Optional[str] = None
    summary: Optional[str] = None
    action_items: List[str] = []
    decisions: List[str] = []
    participants: List[str] = []
    status: str = "pending"  # pending, processing, completed, error
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MeetingCreate(BaseModel):
    title: str
    audio_data: Optional[str] = None

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    meeting_id: str
    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    priority: str = "medium"  # low, medium, high
    status: str = "pending"  # pending, in_progress, completed
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    meeting_id: str
    content: str
    type: str = "highlight"  # highlight, decision, action_item
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    openai_api_key: Optional[str] = None
    preferred_language: str = "en"
    auto_delete_days: Optional[int] = None
    cloud_sync_enabled: bool = True
    privacy_mode: bool = False

# AI Chat Service
async def get_ai_chat():
    api_key = os.getenv('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="AI service not configured")
    
    return LlmChat(
        api_key=api_key,
        session_id="botmr_session",
        system_message="You are an AI assistant specialized in meeting transcription and summarization. Generate concise, actionable summaries with clear action items and key decisions."
    ).with_model("openai", "gpt-4o-mini")

# Routes
@api_router.get("/")
async def root():
    return {"message": "BotMR API is running", "version": "1.0.0"}

@api_router.get("/meetings", response_model=List[Meeting])
async def get_meetings():
    """Get all meetings"""
    try:
        meetings_cursor = db.meetings.find().sort("created_at", -1)
        meetings = await meetings_cursor.to_list(100)
        
        # Convert MongoDB documents to Meeting objects
        result = []
        for meeting in meetings:
            meeting['_id'] = str(meeting['_id'])
            meeting_obj = Meeting(
                id=meeting.get('id', meeting['_id']),
                title=meeting.get('title', 'Untitled Meeting'),
                date=meeting.get('date', meeting.get('created_at', datetime.utcnow()).strftime('%Y-%m-%d %H:%M')),
                summary=meeting.get('summary', 'Processing...'),
                status=meeting.get('status', 'pending'),
                audio_data=meeting.get('audio_data'),
                transcript=meeting.get('transcript'),
                action_items=meeting.get('action_items', []),
                decisions=meeting.get('decisions', []),
                participants=meeting.get('participants', []),
                created_at=meeting.get('created_at', datetime.utcnow()),
                updated_at=meeting.get('updated_at', datetime.utcnow())
            )
            result.append(meeting_obj)
        
        return result
    except Exception as e:
        logger.error(f"Error fetching meetings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch meetings")

@api_router.post("/meetings", response_model=Meeting)
async def create_meeting(meeting: MeetingCreate):
    """Create a new meeting"""
    try:
        # Create meeting object
        meeting_obj = Meeting(
            title=meeting.title,
            date=datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
            audio_data=meeting.audio_data,
            status="pending"
        )
        
        # Insert into database
        result = await db.meetings.insert_one(meeting_obj.dict())
        # Keep the original UUID, don't overwrite with MongoDB ObjectId
        
        # If audio data is provided, start processing
        if meeting.audio_data:
            await process_meeting_async(meeting_obj.id)
        
        return meeting_obj
    except Exception as e:
        logger.error(f"Error creating meeting: {e}")
        raise HTTPException(status_code=500, detail="Failed to create meeting")

@api_router.get("/meetings/{meeting_id}", response_model=Meeting)
async def get_meeting(meeting_id: str):
    """Get a specific meeting"""
    try:
        meeting = await db.meetings.find_one({"id": meeting_id})
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        meeting['_id'] = str(meeting['_id'])
        return Meeting(**meeting)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching meeting: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch meeting")

@api_router.post("/meetings/{meeting_id}/process")
async def process_meeting(meeting_id: str):
    """Process meeting audio for transcription and summarization"""
    try:
        meeting = await db.meetings.find_one({"id": meeting_id})
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        if not meeting.get('audio_data'):
            raise HTTPException(status_code=400, detail="No audio data found")
        
        # Update status to processing
        await db.meetings.update_one(
            {"id": meeting_id},
            {"$set": {"status": "processing", "updated_at": datetime.utcnow()}}
        )
        
        # Mock transcription (replace with actual Whisper API call)
        transcript = await mock_transcribe_audio(meeting.get('audio_data', ''))
        
        # Generate AI summary
        ai_chat = await get_ai_chat()
        summary_prompt = f"""
        Analyze this meeting transcript and provide:
        1. A brief summary (2-3 sentences)
        2. Key decisions made
        3. Action items with clear ownership if mentioned
        4. Important highlights
        
        Transcript: {transcript}
        
        Format your response as:
        SUMMARY: [brief summary]
        DECISIONS: [list of decisions]
        ACTION_ITEMS: [list of action items]
        """
        
        user_message = UserMessage(text=summary_prompt)
        ai_response = await ai_chat.send_message(user_message)
        
        # Parse AI response
        summary, decisions, action_items = parse_ai_response(ai_response)
        
        # Update meeting in database
        await db.meetings.update_one(
            {"id": meeting_id},
            {
                "$set": {
                    "transcript": transcript,
                    "summary": summary,
                    "decisions": decisions,
                    "action_items": action_items,
                    "status": "completed",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"message": "Meeting processed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing meeting: {e}")
        # Update status to error
        await db.meetings.update_one(
            {"id": meeting_id},
            {"$set": {"status": "error", "updated_at": datetime.utcnow()}}
        )
        raise HTTPException(status_code=500, detail="Failed to process meeting")

async def mock_transcribe_audio(audio_data: str) -> str:
    """Mock transcription service - replace with actual Whisper API"""
    return f"""
    Welcome everyone to today's project sync meeting. I'm John, the project manager.

    Sarah: Thanks John. Let me start with the development update. We've completed the user authentication module and the dashboard is 80% done. We're on track to finish by Friday.

    Mike: Great work Sarah. From the design side, I've finalized the mobile wireframes and shared them in Slack. I need feedback by Wednesday to proceed with the final designs.

    John: Perfect. Sarah, can you review Mike's wireframes by Wednesday? Also, we need to schedule the client demo for next week.

    Sarah: Absolutely, I'll review them by Wednesday. For the client demo, I suggest we do it on Tuesday or Wednesday next week.

    Mike: Tuesday works better for me. I'll prepare the presentation slides.

    John: Excellent. Let's confirm Tuesday at 2 PM for the client demo. Any other updates?

    Sarah: One more thing - we'll need to deploy the staging environment by Monday for internal testing.

    John: Got it. Let's make that a priority. Thanks everyone, see you next week.
    """

def parse_ai_response(response: str) -> tuple:
    """Parse AI response into summary, decisions, and action items"""
    try:
        lines = response.split('\n')
        summary = ""
        decisions = []
        action_items = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('SUMMARY:'):
                current_section = 'summary'
                summary = line.replace('SUMMARY:', '').strip()
            elif line.startswith('DECISIONS:'):
                current_section = 'decisions'
            elif line.startswith('ACTION_ITEMS:'):
                current_section = 'action_items'
            elif line and current_section == 'decisions' and line.startswith('-'):
                decisions.append(line[1:].strip())
            elif line and current_section == 'action_items' and line.startswith('-'):
                action_items.append(line[1:].strip())
        
        return summary or "Meeting summary generated", decisions, action_items
        
    except Exception as e:
        logger.error(f"Error parsing AI response: {e}")
        return "Summary processing completed", [], []

async def process_meeting_async(meeting_id: str):
    """Background processing function"""
    # This would be called asynchronously in a real implementation
    pass

@api_router.post("/tasks")
async def create_task(task: Task):
    """Create a new task"""
    try:
        result = await db.tasks.insert_one(task.dict())
        return task
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="Failed to create task")
    """Get all tasks"""
    try:
        tasks_cursor = db.tasks.find().sort("created_at", -1)
        tasks = await tasks_cursor.to_list(100)
        
        result = []
        for task in tasks:
            task['_id'] = str(task['_id'])
            task_obj = Task(
                id=task.get('id', task['_id']),
                meeting_id=task.get('meeting_id', ''),
                title=task.get('title', ''),
                description=task.get('description'),
                assignee=task.get('assignee'),
                priority=task.get('priority', 'medium'),
                status=task.get('status', 'pending'),
                due_date=task.get('due_date'),
                created_at=task.get('created_at', datetime.utcnow())
            )
            result.append(task_obj)
        
        return result
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tasks")

@api_router.get("/messages", response_model=List[Message])
async def get_messages():
    """Get all messages"""
    try:
        messages_cursor = db.messages.find().sort("created_at", -1)
        messages = await messages_cursor.to_list(100)
        
        result = []
        for message in messages:
            message['_id'] = str(message['_id'])
            message_obj = Message(
                id=message.get('id', message['_id']),
                meeting_id=message.get('meeting_id', ''),
                content=message.get('content', ''),
                type=message.get('type', 'highlight'),
                created_at=message.get('created_at', datetime.utcnow())
            )
            result.append(message_obj)
        
        return result
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch messages")

@api_router.get("/settings", response_model=UserSettings)
async def get_settings():
    """Get user settings"""
    try:
        settings = await db.settings.find_one() or {}
        return UserSettings(
            id=settings.get('id', str(uuid.uuid4())),
            openai_api_key=settings.get('openai_api_key'),
            preferred_language=settings.get('preferred_language', 'en'),
            auto_delete_days=settings.get('auto_delete_days'),
            cloud_sync_enabled=settings.get('cloud_sync_enabled', True),
            privacy_mode=settings.get('privacy_mode', False)
        )
    except Exception as e:
        logger.error(f"Error fetching settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch settings")

@api_router.post("/settings")
async def update_settings(settings: UserSettings):
    """Update user settings"""
    try:
        await db.settings.update_one(
            {},
            {"$set": settings.dict()},
            upsert=True
        )
        return {"message": "Settings updated successfully"}
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings")

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)