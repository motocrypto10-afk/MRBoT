# BotMR - Bot Meeting Recorder

## Project Overview

BotMR is a premium mobile-first meeting recording and AI-powered summarization application built with React Native (Expo) and FastAPI backend. The app provides offline-first recording capabilities with intelligent cloud fallback and comprehensive meeting analysis.

## Core Architecture

### Frontend (React Native + Expo)
- **Framework**: React Native with Expo Router for file-based routing
- **Navigation**: Bottom tab navigation with 5 main screens
- **State Management**: React Hooks with AsyncStorage for persistence
- **Audio**: expo-audio for high-quality recording (44.1kHz AAC)
- **UI**: Apple-style design language with premium animations

### Backend (FastAPI + MongoDB)
- **API Framework**: FastAPI with async/await patterns
- **Database**: MongoDB with Motor (async driver)
- **AI Integration**: Emergent LLM Universal Key for GPT-4/Claude/Gemini
- **Audio Processing**: Queue-based transcription and summarization
- **Recording Management**: Session-based recording with heartbeat monitoring

## Key Features

### 1. Navigation Structure
```
Summary (Home) → Meeting feed with status cards
Tasks → Action items from meetings
Record (Center) → Recording interface with controls
MoM → Full meeting minutes and transcripts
Settings → App configuration and integrations
```

### 2. Recording System
- **Local Mode**: On-device recording with background support
- **Cloud Fallback**: Automatic failover if device recording fails
- **Session Management**: Unique session tracking with heartbeat monitoring
- **Queue Processing**: Non-blocking upload and processing pipeline
- **Marker Support**: Time-stamped annotations during recording

### 3. AI Processing Pipeline
```
Audio Recording → Chunked Upload → Transcription → 
AI Analysis → Summary + Tasks + Decisions → 
Database Storage → Push Notifications
```

## Technical Implementation

### Recording Flow (Refined)
1. **Start Recording**: Permission check → Backend session → Local recording
2. **Active Recording**: Heartbeat every 10s → Waveform animation → Marker support
3. **Stop Recording**: Haptic feedback → Queue for processing → Auto-return to Summary
4. **Background Processing**: Upload → Transcribe → Analyze → Notify user

### Database Schema
```javascript
// Meetings Collection
{
  id: string,
  title: string,
  date: string,
  summary: string,
  transcript: string,
  action_items: string[],
  decisions: string[],
  status: 'pending' | 'processing' | 'completed',
  created_at: DateTime
}

// Recording Sessions Collection
{
  session_id: string,
  device_id: string,
  mode: 'local' | 'cloud',
  status: 'active' | 'stopped' | 'failed',
  started_at: DateTime,
  last_heartbeat: DateTime,
  markers: { time: number, label: string }[]
}

// Tasks Collection
{
  id: string,
  meeting_id: string,
  title: string,
  assignee: string,
  priority: 'low' | 'medium' | 'high',
  status: 'pending' | 'completed'
}
```

### API Endpoints
```
POST /api/recordings/start     → Start recording session
POST /api/recordings/heartbeat → Session heartbeat
POST /api/recordings/stop      → Stop and queue processing
GET  /api/recordings/{id}/status → Session status

GET  /api/meetings             → Meeting list
POST /api/meetings             → Create meeting
POST /api/meetings/{id}/process → Trigger AI processing

GET  /api/tasks               → Task list
POST /api/tasks               → Create task

GET  /api/settings            → User settings
POST /api/settings            → Update settings
```

## UI/UX Design Principles

### Visual Design
- **Design Language**: Apple iOS design with SF Pro typography
- **Color Palette**: Primary blue (#007AFF), success green (#34C759), warning orange (#FF9500)
- **Layout**: 8pt grid system with consistent spacing
- **Shadows**: Soft shadows (0.08 opacity, 12px radius)
- **Animations**: Smooth transitions with native driver optimization

### Recording Interface
- **Dark Theme**: #1C1C1E background for professional recording environment
- **Status Banner**: Pill-style status indicator with color coding
- **Central Mic**: Large mic icon with pulse animation and glow effects
- **Waveform**: Real-time animated bars responding to audio input
- **Controls**: Marker, Pause/Resume, Stop in accessible row layout

### Meeting Cards (Summary Screen)
```
Card States:
🟡 Pending Upload → "Awaiting network..."
🔵 Processing → "Transcribing & analyzing..."
🟢 Completed → "X Action Items • Summary Ready"
```

## Environment Configuration

### Frontend (.env)
```
EXPO_PUBLIC_BACKEND_URL=http://localhost:3000
EXPO_PACKAGER_PROXY_URL=http://localhost:3000
EXPO_PACKAGER_HOSTNAME=localhost
```

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017
EMERGENT_LLM_KEY=sk-emergent-[key]
DB_NAME=test_database
```

## Development Workflow

1. **Setup**: Expo + FastAPI + MongoDB running locally
2. **Frontend Development**: expo start --tunnel for mobile testing
3. **Backend Development**: uvicorn server:app --reload --host 0.0.0.0 --port 8001
4. **Testing**: Comprehensive API testing with curl + Frontend UI testing
5. **Deployment**: Expo builds + FastAPI containerization

## File Structure
```
/app
├── frontend/                 # Expo React Native app
│   ├── app/                 # Expo Router file-based routing
│   │   ├── index.tsx        # Main navigation with bottom tabs
│   │   └── screens/         # Individual screen components
│   ├── assets/              # Images, icons, fonts
│   └── package.json         # Dependencies and scripts
├── backend/                 # FastAPI server
│   ├── server.py           # Main API with all endpoints
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
└── README_BOTMR_CONTEXT.md # This documentation file
```

## Dependencies

### Frontend Key Packages
- expo-router: File-based navigation
- expo-audio: High-quality audio recording
- @react-navigation/bottom-tabs: Tab navigation
- react-native-safe-area-context: Safe area handling
- @expo/vector-icons: Icon library
- @react-native-async-storage/async-storage: Local storage

### Backend Key Packages
- fastapi: Modern Python API framework
- motor: Async MongoDB driver
- emergentintegrations: Universal LLM integration
- python-multipart: File upload support
- uvicorn: ASGI server

## AI Integration Details

### Emergent LLM Universal Key
- **Providers**: OpenAI GPT-4, Anthropic Claude, Google Gemini
- **Usage**: Text generation for meeting summarization
- **Installation**: `pip install emergentintegrations`
- **Implementation**: LlmChat class with session management

### Processing Pipeline
1. **Audio Upload**: Chunked upload with retry logic
2. **Transcription**: Mock transcription (Whisper integration ready)
3. **AI Analysis**: Emergent LLM for summary, decisions, action items
4. **Data Extraction**: Structured parsing of AI response
5. **Storage**: MongoDB with proper indexing and relationships

## Future Enhancements

### Phase 1 (Current)
- ✅ Core recording functionality
- ✅ Basic AI processing
- ✅ Queue-based architecture
- ✅ Premium UI/UX

### Phase 2 (Next)
- [ ] Background service implementation
- [ ] Chunked audio upload with encryption
- [ ] Real Whisper API integration
- [ ] Push notification system
- [ ] Cloud Bot Mode for server-side recording

### Phase 3 (Advanced)
- [ ] External integrations (Zoho, Google Drive, Notion)
- [ ] Export functionality (PDF, DOCX, Email)
- [ ] Multi-language transcription
- [ ] Speaker diarization
- [ ] Meeting scheduling and auto-join

## Security Considerations

- **Audio Encryption**: AES-256 encryption for local storage
- **API Keys**: Secure storage in device keychain/keystore
- **Data Privacy**: Local-first with optional cloud sync
- **Transport Security**: TLS 1.3 for all API communications
- **Session Security**: JWT tokens with refresh mechanism

## Testing Strategy

### Backend Testing
- API endpoint validation with curl
- Database operations testing
- AI integration testing
- Error handling and edge cases

### Frontend Testing  
- UI component testing with Expo Go
- Navigation flow testing
- Audio recording functionality
- Cross-platform compatibility (iOS/Android)

## Deployment Architecture

### Mobile App
- Expo managed workflow for development
- Expo Application Services (EAS) for production builds
- App Store/Google Play distribution

### Backend Service
- Docker containerization with multi-stage builds
- MongoDB Atlas for production database
- Cloud deployment (AWS/Google Cloud/Azure)
- Auto-scaling based on processing queue length

---

This context document provides comprehensive information for any future development work on BotMR. The architecture is designed for scalability, maintainability, and premium user experience.