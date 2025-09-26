# BotMR API Documentation

## Overview
BotMR is a comprehensive meeting recording and AI-powered summarization API built with FastAPI. This API provides endpoints for meeting management, audio recording sessions, task management, and AI-powered transcription and analysis.

**Base URL**: `http://localhost:8001/api`
**Version**: 1.0.0

---

## Authentication
Currently, the API does not require authentication for development purposes. In production, implement JWT-based authentication.

---

## Core Endpoints

### 1. Health Check

#### GET `/`
Check if the API is running.

**Response:**
```json
{
  "message": "BotMR API is running",
  "version": "1.0.0"
}
```

---

## Meeting Management

### 2. Get All Meetings

#### GET `/meetings`
Retrieve all meetings sorted by creation date (newest first).

**Response:**
```json
[
  {
    "id": "uuid-string",
    "title": "Project Sync Meeting",
    "date": "2025-01-24 14:30",
    "audio_data": "base64-encoded-audio-or-null",
    "transcript": "Full meeting transcript...",
    "summary": "Brief meeting summary",
    "action_items": ["Task 1", "Task 2"],
    "decisions": ["Decision 1", "Decision 2"],
    "participants": ["John", "Sarah", "Mike"],
    "status": "completed",
    "created_at": "2025-01-24T14:30:00",
    "updated_at": "2025-01-24T15:45:00"
  }
]
```

**Status Codes:**
- `200 OK`: Success
- `500 Internal Server Error`: Database error

### 3. Create Meeting

#### POST `/meetings`
Create a new meeting.

**Request Body:**
```json
{
  "title": "Meeting Title",
  "audio_data": "optional-base64-audio-data"
}
```

**Response:**
```json
{
  "id": "uuid-string",
  "title": "Meeting Title",
  "date": "2025-01-24 14:30",
  "status": "pending",
  "created_at": "2025-01-24T14:30:00",
  "updated_at": "2025-01-24T14:30:00"
}
```

**Status Codes:**
- `200 OK`: Meeting created successfully
- `500 Internal Server Error`: Creation failed

### 4. Get Meeting by ID

#### GET `/meetings/{meeting_id}`
Retrieve a specific meeting by its ID.

**Parameters:**
- `meeting_id` (string, required): UUID of the meeting

**Response:**
```json
{
  "id": "uuid-string",
  "title": "Meeting Title",
  "transcript": "Full transcript...",
  "summary": "AI-generated summary",
  "action_items": ["Item 1", "Item 2"],
  "decisions": ["Decision 1"],
  "status": "completed"
}
```

**Status Codes:**
- `200 OK`: Meeting found
- `404 Not Found`: Meeting not found
- `500 Internal Server Error`: Database error

### 5. Process Meeting

#### POST `/meetings/{meeting_id}/process`
Trigger AI processing for transcription and summarization.

**Parameters:**
- `meeting_id` (string, required): UUID of the meeting

**Response:**
```json
{
  "message": "Meeting processed successfully"
}
```

**Status Codes:**
- `200 OK`: Processing completed successfully
- `404 Not Found`: Meeting not found
- `400 Bad Request`: No audio data found
- `500 Internal Server Error`: Processing failed

---

## Recording Session Management

### 6. Start Recording Session

#### POST `/recordings/start`
Initialize a new recording session with backend tracking.

**Request Body:**
```json
{
  "mode": "local",
  "allow_fallback": true,
  "metadata": {
    "deviceId": "device_123",
    "platform": "ios",
    "userId": "optional-user-id"
  },
  "meeting_id": "optional-existing-meeting-id"
}
```

**Response:**
```json
{
  "sessionId": "session-uuid",
  "uploadUrls": [],
  "status": "active"
}
```

**Status Codes:**
- `200 OK`: Session started successfully
- `500 Internal Server Error`: Failed to start recording

### 7. Recording Heartbeat

#### POST `/recordings/heartbeat`
Send periodic heartbeat to maintain session and enable cloud fallback.

**Request Body:**
```json
{
  "session_id": "session-uuid",
  "device_id": "device_123",
  "ts": "2025-01-24T14:30:00Z"
}
```

**Response:**
```json
{
  "ok": true
}
```

**Status Codes:**
- `200 OK`: Heartbeat received
- `500 Internal Server Error`: Heartbeat update failed

### 8. Stop Recording Session

#### POST `/recordings/stop`
Stop recording session and trigger processing pipeline.

**Request Body:**
```json
{
  "session_id": "session-uuid",
  "final": true,
  "stats": {
    "duration": 1800,
    "fileUri": "local-file-path",
    "markers": [
      {"time": 300, "label": "Important point"},
      {"time": 900, "label": "Decision made"}
    ]
  }
}
```

**Response:**
```json
{
  "message": "Recording stopped successfully",
  "meetingId": "meeting-uuid",
  "sessionId": "session-uuid"
}
```

**Status Codes:**
- `200 OK`: Recording stopped and queued for processing
- `404 Not Found`: Recording session not found
- `500 Internal Server Error`: Failed to stop recording

### 9. Get Recording Status

#### GET `/recordings/{session_id}/status`
Check the status of a recording session.

**Parameters:**
- `session_id` (string, required): UUID of the recording session

**Response:**
```json
{
  "sessionId": "session-uuid",
  "status": "stopped",
  "uploadedChunks": 3,
  "transcriptState": "pending",
  "startedAt": "2025-01-24T14:30:00",
  "lastHeartbeat": "2025-01-24T14:45:00"
}
```

**Status Codes:**
- `200 OK`: Status retrieved successfully
- `404 Not Found`: Session not found
- `500 Internal Server Error`: Failed to get status

---

## Task Management

### 10. Get All Tasks

#### GET `/tasks`
Retrieve all tasks sorted by creation date.

**Response:**
```json
[
  {
    "id": "task-uuid",
    "meeting_id": "meeting-uuid",
    "title": "Review wireframes by Wednesday",
    "description": "Check mobile designs shared in Slack",
    "assignee": "Sarah",
    "priority": "high",
    "status": "pending",
    "due_date": "2025-01-26T17:00:00",
    "created_at": "2025-01-24T14:30:00"
  }
]
```

**Status Codes:**
- `200 OK`: Tasks retrieved successfully
- `500 Internal Server Error`: Database error

### 11. Create Task

#### POST `/tasks`
Create a new task.

**Request Body:**
```json
{
  "meeting_id": "meeting-uuid",
  "title": "Task title",
  "description": "Optional task description",
  "assignee": "John Doe",
  "priority": "medium",
  "status": "pending",
  "due_date": "2025-01-26T17:00:00Z"
}
```

**Response:**
```json
{
  "id": "task-uuid",
  "meeting_id": "meeting-uuid",
  "title": "Task title",
  "priority": "medium",
  "status": "pending",
  "created_at": "2025-01-24T14:30:00"
}
```

**Status Codes:**
- `200 OK`: Task created successfully
- `500 Internal Server Error`: Failed to create task

---

## Message Management

### 12. Get All Messages

#### GET `/messages`
Retrieve all messages/highlights sorted by creation date.

**Response:**
```json
[
  {
    "id": "message-uuid",
    "meeting_id": "meeting-uuid",
    "content": "Key decision made about project timeline",
    "type": "decision",
    "created_at": "2025-01-24T14:30:00"
  }
]
```

**Message Types:**
- `highlight`: Important moment in meeting
- `decision`: Key decision made
- `action_item`: Task or action identified

**Status Codes:**
- `200 OK`: Messages retrieved successfully
- `500 Internal Server Error`: Database error

---

## Settings Management

### 13. Get User Settings

#### GET `/settings`
Retrieve user settings and preferences.

**Response:**
```json
{
  "id": "settings-uuid",
  "openai_api_key": "optional-user-provided-key",
  "preferred_language": "en",
  "auto_delete_days": 30,
  "cloud_sync_enabled": true,
  "privacy_mode": false
}
```

**Status Codes:**
- `200 OK`: Settings retrieved successfully
- `500 Internal Server Error`: Database error

### 14. Update User Settings

#### POST `/settings`
Update user settings and preferences.

**Request Body:**
```json
{
  "openai_api_key": "sk-...",
  "preferred_language": "ta",
  "auto_delete_days": 90,
  "cloud_sync_enabled": false,
  "privacy_mode": true
}
```

**Response:**
```json
{
  "message": "Settings updated successfully"
}
```

**Status Codes:**
- `200 OK`: Settings updated successfully
- `500 Internal Server Error`: Failed to update settings

---

## Data Models

### Meeting Model
```typescript
interface Meeting {
  id: string;                    // UUID
  title: string;                 // Meeting title
  date: string;                  // "YYYY-MM-DD HH:MM" format
  audio_data?: string;           // Base64 encoded audio
  transcript?: string;           // Full transcript text
  summary?: string;              // AI-generated summary
  action_items: string[];        // List of action items
  decisions: string[];           // List of decisions made
  participants: string[];        // List of participant names
  status: "pending" | "processing" | "completed" | "error";
  created_at: string;           // ISO timestamp
  updated_at: string;           // ISO timestamp
}
```

### Recording Session Model
```typescript
interface RecordingSession {
  id: string;                   // UUID
  session_id: string;           // Session UUID
  mode: "local" | "cloud" | "local_to_cloud";
  device_id: string;            // Device identifier
  user_id?: string;             // Optional user ID
  meeting_id?: string;          // Optional meeting association
  status: "active" | "paused" | "stopped" | "failed" | "pending_sync";
  allow_fallback: boolean;      // Cloud fallback enabled
  started_at: string;           // ISO timestamp
  ended_at?: string;            // ISO timestamp
  audio_files: string[];        // List of audio file paths
  markers: Marker[];            // Time markers
  metadata: object;             // Additional metadata
  last_heartbeat: string;       // ISO timestamp
}

interface Marker {
  time: number;                 // Time in seconds
  label: string;                // Marker description
}
```

### Task Model
```typescript
interface Task {
  id: string;                   // UUID
  meeting_id: string;           // Associated meeting ID
  title: string;                // Task title
  description?: string;         // Optional description
  assignee?: string;            // Optional assignee name
  priority: "low" | "medium" | "high";
  status: "pending" | "in_progress" | "completed";
  due_date?: string;            // ISO timestamp
  created_at: string;           // ISO timestamp
}
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message description"
}
```

### Common Status Codes:
- `200 OK`: Request successful
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## Rate Limits
Currently no rate limits implemented. In production, implement:
- 100 requests per minute per IP
- 1000 requests per hour per user

---

## AI Integration

### Emergent LLM Integration
The API uses Emergent Universal LLM key for AI processing:

**Supported Models:**
- OpenAI GPT-4o-mini (default)
- Anthropic Claude
- Google Gemini

**AI Processing Pipeline:**
1. Audio → Mock Transcription (Whisper integration ready)
2. Transcript → AI Analysis using Emergent LLM
3. Extract: Summary, Decisions, Action Items
4. Store results in database

### AI Prompt Format
```
Analyze this meeting transcript and provide:
1. A brief summary (2-3 sentences)
2. Key decisions made
3. Action items with clear ownership if mentioned
4. Important highlights

Transcript: [transcript text]

Format your response as:
SUMMARY: [brief summary]
DECISIONS: [list of decisions]
ACTION_ITEMS: [list of action items]
```

---

## Database Schema

### Collections:
- **meetings**: Meeting documents
- **recording_sessions**: Recording session tracking
- **tasks**: Task management
- **messages**: Highlights and messages
- **settings**: User preferences

### Indexes:
- `meetings.created_at` (descending)
- `recording_sessions.session_id` (unique)
- `tasks.meeting_id`
- `tasks.created_at` (descending)

---

## Development Setup

### Environment Variables:
```bash
MONGO_URL=mongodb://localhost:27017
EMERGENT_LLM_KEY=sk-emergent-[key]
DB_NAME=test_database
```

### Running the API:
```bash
cd /app/backend
pip install -r requirements.txt
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### API Documentation:
- Interactive docs: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

---

## Future Enhancements

### Planned Features:
- JWT Authentication
- Rate limiting
- Webhook notifications
- Real Whisper API integration
- File upload for audio chunks
- Speaker diarization
- Multi-language transcription
- Export functionality (PDF, DOCX)

### API Versioning:
Future versions will be prefixed: `/api/v2/`, `/api/v3/`

---

## Support

For API support and issues:
- Check logs: `/var/log/supervisor/backend.err.log`
- Monitor health: `GET /api/`
- Database status: MongoDB connection logs

---

*Last Updated: January 24, 2025*
*API Version: 1.0.0*