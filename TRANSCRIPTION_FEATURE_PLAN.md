# BotMR Transcription & Analysis Feature Implementation Plan

## Overview
This document outlines the comprehensive implementation plan for the Transcription & Analysis feature, building upon the modularized codebase structure.

---

## Feature Architecture

### Queue-First Pipeline Design

```
Audio Recording → Queue Job → Processing Pipeline → Notification
     ↓              ↓              ↓                  ↓
  Local/Cloud → TranscriptionJob → AI Analysis → Push/Badge Update
```

### Processing Stages
1. **Ingest**: Fetch uploaded audio chunks
2. **Pre-process**: Denoise, VAD trim, normalization
3. **ASR**: Multilingual speech-to-text (Whisper)
4. **Diarization**: Speaker segmentation
5. **Formatting**: Punctuation, casing, formatting
6. **NLP**: Summaries, decisions, action items extraction
7. **Redaction**: Optional PII masking
8. **Persist**: Store results and index for search
9. **Notify**: Push notifications and UI updates

---

## Database Schema Extensions

### New Collections

#### TranscriptionJobs
```typescript
interface TranscriptionJob {
  job_id: string;           // UUID
  session_id: string;       // Recording session ID
  meeting_id: string;       // Associated meeting
  state: 'queued' | 'running' | 'failed' | 'completed';
  mode: 'local' | 'cloud';  // Processing mode
  attempts: number;         // Retry counter
  last_error?: string;      // Error message if failed
  started_at?: Date;        // Processing start time
  finished_at?: Date;       // Processing completion time
  progress_percent: number; // 0-100 completion percentage
  settings: {
    languages: string[];    // Allowed languages
    redaction_enabled: boolean;
    offline_mode: boolean;
    quality_preference: 'fast' | 'accurate';
  };
  created_at: Date;
  updated_at: Date;
}
```

#### Transcripts
```typescript
interface Transcript {
  transcript_id: string;    // UUID
  meeting_id: string;       // Associated meeting
  job_id: string;          // Source transcription job
  language: string;         // Detected primary language
  duration: number;         // Total duration in seconds
  confidence_avg: number;   // Average confidence score
  segments: TranscriptSegment[];
  speakers: Speaker[];
  created_at: Date;
  updated_at: Date;
}

interface TranscriptSegment {
  start: number;           // Start time in seconds
  end: number;             // End time in seconds
  speaker: string;         // Speaker ID (S0, S1, etc.)
  text: string;            // Segment text
  confidence: number;      // Confidence score 0-1
  words?: WordTimestamp[]; // Optional word-level timestamps
}

interface WordTimestamp {
  word: string;
  start: number;
  end: number;
  confidence: number;
}

interface Speaker {
  id: string;              // S0, S1, S2, etc.
  name?: string;           // Optional human-readable name
  total_duration: number;  // Total speaking time
  segment_count: number;   // Number of segments
}
```

#### Insights
```typescript
interface Insights {
  insights_id: string;     // UUID
  meeting_id: string;      // Associated meeting
  transcript_id: string;   // Source transcript
  summary_short: string;   // Tweet-length summary (≤240 chars)
  summary_detailed: string; // 3-6 bullet points
  decisions: Decision[];
  action_items: ActionItem[];
  highlights: Highlight[];
  entities: Entity[];
  created_at: Date;
  updated_at: Date;
}

interface Decision {
  text: string;            // Decision description
  span?: TimeSpan;         // Source location in transcript
  confidence: number;      // AI confidence
}

interface ActionItem {
  title: string;           // Action item title
  owner?: string;          // Assigned person (if detected)
  due_date?: Date;         // Due date (if detected)
  priority?: 'low' | 'medium' | 'high';
  span?: TimeSpan;         // Source location in transcript
  status: 'pending' | 'in_progress' | 'completed';
  confidence: number;      // AI confidence
}

interface Highlight {
  timestamp: number;       // Time in seconds
  text: string;            // Highlight text
  type: 'quote' | 'decision' | 'action' | 'insight';
}

interface Entity {
  text: string;            // Original text
  type: 'person' | 'date' | 'organization' | 'amount' | 'project';
  normalized_value?: any;  // Parsed/normalized value
  span?: TimeSpan;         // Source location
}

interface TimeSpan {
  start: number;           // Start time in seconds
  end: number;             // End time in seconds
}
```

---

## Backend Implementation

### 1. Modular Service Architecture

#### TranscriptionService
```python
# services/transcription_service.py
from typing import Optional
from models.transcription import TranscriptionJob, Transcript
from integrations.whisper_integration import WhisperIntegration
from integrations.diarization_integration import DiarizationIntegration

class TranscriptionService:
    def __init__(
        self,
        job_repo: TranscriptionJobRepository,
        transcript_repo: TranscriptRepository,
        whisper: WhisperIntegration,
        diarization: DiarizationIntegration,
        queue: TranscriptionQueue
    ):
        self.job_repo = job_repo
        self.transcript_repo = transcript_repo
        self.whisper = whisper
        self.diarization = diarization
        self.queue = queue
    
    async def enqueue_transcription(self, session_id: str, settings: dict) -> str:
        """Enqueue a transcription job"""
        job = TranscriptionJob(
            session_id=session_id,
            state='queued',
            settings=settings
        )
        await self.job_repo.create(job)
        await self.queue.enqueue(job.job_id)
        return job.job_id
    
    async def process_transcription_job(self, job_id: str):
        """Process a transcription job through the complete pipeline"""
        job = await self.job_repo.get_by_id(job_id)
        
        try:
            # Update job to running
            await self.job_repo.update_state(job_id, 'running')
            
            # Stage 1: Ingest and validate audio
            audio_data = await self._ingest_audio(job.session_id)
            
            # Stage 2: Pre-process audio
            processed_audio = await self._preprocess_audio(audio_data, job.settings)
            
            # Stage 3: Speech-to-text
            raw_transcript = await self.whisper.transcribe(
                processed_audio, 
                languages=job.settings.get('languages', ['en'])
            )
            
            # Stage 4: Speaker diarization
            diarized_segments = await self.diarization.process(
                processed_audio, 
                raw_transcript
            )
            
            # Stage 5: Format and clean transcript
            formatted_transcript = await self._format_transcript(
                diarized_segments, 
                job.settings
            )
            
            # Stage 6: Store transcript
            transcript = await self.transcript_repo.create(formatted_transcript)
            
            # Stage 7: Trigger NLP processing
            await self._trigger_nlp_processing(transcript.transcript_id)
            
            # Update job to completed
            await self.job_repo.update_state(job_id, 'completed')
            
        except Exception as e:
            await self.job_repo.update_state(job_id, 'failed', str(e))
            await self._schedule_retry(job_id)
```

#### NLPService
```python
# services/nlp_service.py
class NLPService:
    def __init__(self, ai_service: AIService, insights_repo: InsightsRepository):
        self.ai_service = ai_service
        self.insights_repo = insights_repo
    
    async def generate_insights(self, transcript_id: str) -> Insights:
        """Generate comprehensive insights from transcript"""
        transcript = await self.transcript_repo.get_by_id(transcript_id)
        
        # Generate summaries
        summary_short = await self._generate_short_summary(transcript)
        summary_detailed = await self._generate_detailed_summary(transcript)
        
        # Extract structured data
        decisions = await self._extract_decisions(transcript)
        action_items = await self._extract_action_items(transcript)
        highlights = await self._extract_highlights(transcript)
        entities = await self._extract_entities(transcript)
        
        insights = Insights(
            meeting_id=transcript.meeting_id,
            transcript_id=transcript_id,
            summary_short=summary_short,
            summary_detailed=summary_detailed,
            decisions=decisions,
            action_items=action_items,
            highlights=highlights,
            entities=entities
        )
        
        return await self.insights_repo.create(insights)
```

### 2. Queue System Implementation

#### TranscriptionQueue
```python
# queue/transcription_queue.py
import asyncio
from typing import Dict, List
import json

class TranscriptionQueue:
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.workers: Dict[str, TranscriptionWorker] = {}
        self.max_concurrent_jobs = 3
    
    async def enqueue(self, job_id: str, priority: int = 0):
        """Add job to processing queue"""
        job_data = {
            'job_id': job_id,
            'priority': priority,
            'enqueued_at': datetime.utcnow().isoformat()
        }
        
        if self.redis:
            await self.redis.lpush('transcription_queue', json.dumps(job_data))
        else:
            # Fallback to in-memory queue for development
            await self._process_immediately(job_id)
    
    async def start_workers(self):
        """Start background workers to process queue"""
        for i in range(self.max_concurrent_jobs):
            worker = TranscriptionWorker(
                worker_id=f"worker_{i}",
                transcription_service=self.transcription_service
            )
            self.workers[worker.worker_id] = worker
            asyncio.create_task(worker.start())
    
    async def get_job_status(self, job_id: str) -> dict:
        """Get current status of a job"""
        job = await self.job_repo.get_by_id(job_id)
        return {
            'state': job.state,
            'progress': job.progress_percent,
            'error': job.last_error
        }
```

#### TranscriptionWorker
```python
# workers/transcription_worker.py
class TranscriptionWorker:
    def __init__(self, worker_id: str, transcription_service: TranscriptionService):
        self.worker_id = worker_id
        self.transcription_service = transcription_service
        self.running = False
    
    async def start(self):
        """Start processing jobs from queue"""
        self.running = True
        
        while self.running:
            try:
                # Get next job from queue
                job_data = await self._get_next_job()
                
                if job_data:
                    job_id = job_data['job_id']
                    
                    # Process the transcription job
                    await self.transcription_service.process_transcription_job(job_id)
                    
                    # Mark job as completed in queue
                    await self._mark_job_completed(job_id)
                else:
                    # No jobs available, wait before checking again
                    await asyncio.sleep(5)
                    
            except Exception as e:
                logger.error(f"Worker {self.worker_id} error: {e}")
                await asyncio.sleep(10)  # Wait longer on error
```

### 3. Integration Services

#### WhisperIntegration
```python
# integrations/whisper_integration.py
import openai
from typing import List, Dict

class WhisperIntegration:
    def __init__(self, api_key: str, model: str = "whisper-1"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def transcribe(
        self, 
        audio_data: bytes, 
        languages: List[str] = None,
        enable_timestamps: bool = True
    ) -> Dict:
        """Transcribe audio using OpenAI Whisper"""
        
        # Prepare request parameters
        params = {
            'model': self.model,
            'response_format': 'verbose_json',
            'timestamp_granularities': ['word', 'segment']
        }
        
        if languages:
            # Convert language codes to Whisper format
            whisper_languages = self._convert_language_codes(languages)
            params['language'] = whisper_languages[0]  # Primary language
        
        try:
            # Create temporary file for Whisper API
            with tempfile.NamedTemporaryFile(suffix='.m4a') as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                
                # Call Whisper API
                response = await self.client.audio.transcriptions.create(
                    file=open(temp_file.name, 'rb'),
                    **params
                )
                
                return {
                    'text': response.text,
                    'language': response.language,
                    'segments': response.segments,
                    'words': response.words if hasattr(response, 'words') else []
                }
                
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            raise TranscriptionError(f"Failed to transcribe audio: {str(e)}")
    
    def _convert_language_codes(self, languages: List[str]) -> List[str]:
        """Convert ISO language codes to Whisper format"""
        mapping = {
            'en': 'english',
            'ta': 'tamil',
            'hi': 'hindi',
            'fr': 'french',
            'it': 'italian'
        }
        return [mapping.get(lang, lang) for lang in languages]
```

---

## Frontend Implementation

### 1. State Management Updates

#### TranscriptionStore
```typescript
// src/store/transcription-store.ts
import { create } from 'zustand';
import { TranscriptionJob, Transcript, Insights } from '../types/transcription';

interface TranscriptionStore {
  // Job tracking
  activeJobs: Map<string, TranscriptionJob>;
  jobProgress: Map<string, number>;
  
  // Results
  transcripts: Map<string, Transcript>;
  insights: Map<string, Insights>;
  
  // Actions
  startTranscription: (sessionId: string, settings: any) => Promise<string>;
  getJobStatus: (jobId: string) => Promise<TranscriptionJob>;
  getTranscript: (meetingId: string) => Promise<Transcript | null>;
  getInsights: (meetingId: string) => Promise<Insights | null>;
  
  // Real-time updates
  subscribeToJobUpdates: (jobId: string, callback: (progress: number) => void) => void;
  unsubscribeFromJobUpdates: (jobId: string) => void;
}

export const useTranscriptionStore = create<TranscriptionStore>((set, get) => ({
  activeJobs: new Map(),
  jobProgress: new Map(),
  transcripts: new Map(),
  insights: new Map(),
  
  startTranscription: async (sessionId: string, settings: any) => {
    const response = await fetch(`${API_BASE}/transcription/enqueue`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId, settings })
    });
    
    const { jobId } = await response.json();
    
    // Start polling for updates
    get().subscribeToJobUpdates(jobId, (progress) => {
      set((state) => ({
        jobProgress: new Map(state.jobProgress.set(jobId, progress))
      }));
    });
    
    return jobId;
  },
  
  getJobStatus: async (jobId: string) => {
    const response = await fetch(`${API_BASE}/transcription/${jobId}/status`);
    return response.json();
  },
  
  // ... other implementations
}));
```

### 2. Enhanced Recording Hook

#### useRecording Enhancement
```typescript
// src/hooks/useRecording.ts
import { useTranscriptionStore } from '../store/transcription-store';

export const useRecording = () => {
  const { startTranscription } = useTranscriptionStore();
  
  const stopRecording = async () => {
    // ... existing stop logic
    
    // Queue for transcription after recording stops
    if (recordingState.sessionId) {
      const transcriptionSettings = {
        languages: ['en', 'ta', 'hi'], // From user preferences
        redaction_enabled: userSettings.redactionEnabled,
        offline_mode: userSettings.offlineMode,
        quality_preference: userSettings.qualityPreference
      };
      
      const jobId = await startTranscription(
        recordingState.sessionId, 
        transcriptionSettings
      );
      
      // Show processing notification
      showStatusToast('Transcription queued for processing...');
      
      // Navigate back to summary
      setTimeout(() => {
        navigation.navigate('Summary');
      }, 1000);
    }
  };
  
  return {
    // ... existing returns
    stopRecording,
  };
};
```

### 3. Real-time Progress Updates

#### WebSocket Integration
```typescript
// src/services/websocket-service.ts
class WebSocketService {
  private ws: WebSocket | null = null;
  private subscribers: Map<string, Set<Function>> = new Map();
  
  connect() {
    this.ws = new WebSocket(`${WS_BASE}/transcription/updates`);
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'job_progress') {
        const callbacks = this.subscribers.get(data.jobId);
        callbacks?.forEach(callback => callback(data.progress));
      }
      
      if (data.type === 'job_completed') {
        // Trigger store updates
        this.notifyJobCompletion(data.jobId, data.results);
      }
    };
  }
  
  subscribeToJob(jobId: string, callback: Function) {
    if (!this.subscribers.has(jobId)) {
      this.subscribers.set(jobId, new Set());
    }
    this.subscribers.get(jobId)?.add(callback);
  }
}
```

---

## API Endpoints

### New Transcription Endpoints

```python
# routes/transcription.py
from fastapi import APIRouter, Depends, HTTPException
from services.transcription_service import TranscriptionService

router = APIRouter(prefix="/transcription", tags=["transcription"])

@router.post("/enqueue")
async def enqueue_transcription(
    request: TranscriptionRequest,
    service: TranscriptionService = Depends()
):
    """Enqueue transcription job for processing"""
    job_id = await service.enqueue_transcription(
        request.session_id,
        request.settings
    )
    return {"jobId": job_id}

@router.get("/{job_id}/status")
async def get_transcription_status(
    job_id: str,
    service: TranscriptionService = Depends()
):
    """Get transcription job status and progress"""
    status = await service.get_job_status(job_id)
    return status

@router.get("/meetings/{meeting_id}/insights")
async def get_meeting_insights(
    meeting_id: str,
    insights_service: InsightsService = Depends()
):
    """Get comprehensive meeting insights"""
    insights = await insights_service.get_by_meeting_id(meeting_id)
    if not insights:
        raise HTTPException(404, "Insights not found")
    return insights

@router.patch("/meetings/{meeting_id}/speakers")
async def update_speaker_names(
    meeting_id: str,
    speaker_mapping: dict,
    transcript_service: TranscriptService = Depends()
):
    """Update speaker names in transcript"""
    await transcript_service.update_speaker_names(meeting_id, speaker_mapping)
    return {"message": "Speaker names updated"}

@router.post("/reprocess")
async def reprocess_meeting(
    request: ReprocessRequest,
    nlp_service: NLPService = Depends()
):
    """Reprocess only NLP parts without re-transcribing"""
    if 'nlp' in request.steps:
        await nlp_service.reprocess_insights(request.meeting_id)
    return {"message": "Reprocessing initiated"}
```

---

## Performance Targets & Monitoring

### Performance Goals
- **P95 end-to-end (1-hour meeting)**: ≤ 8-12 minutes to "Completed"
- **Local transcription**: ≤ 1.5× real-time on modern devices
- **Memory usage**: <200MB peak on device
- **Queue throughput**: 10 concurrent jobs minimum

### Monitoring Implementation
```python
# utils/performance_monitor.py
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    async def track_transcription_job(self, job_id: str):
        """Track performance metrics for transcription job"""
        start_time = time.time()
        
        try:
            # Job processing happens here
            yield
            
        finally:
            duration = time.time() - start_time
            await self._record_metric('transcription_duration', duration, {
                'job_id': job_id,
                'status': 'completed'
            })
```

---

## Security & Compliance

### Data Protection
```python
# utils/redaction.py
class RedactionService:
    def __init__(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'amount': r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        }
    
    def redact_transcript(self, text: str, rules: List[str]) -> str:
        """Apply redaction rules to transcript text"""
        redacted_text = text
        
        for rule in rules:
            if rule in self.patterns:
                pattern = self.patterns[rule]
                redacted_text = re.sub(pattern, '[REDACTED]', redacted_text)
        
        return redacted_text
```

### Encryption
```python
# utils/encryption.py
from cryptography.fernet import Fernet
import base64

class EncryptionService:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())
    
    def encrypt_transcript(self, transcript: str) -> str:
        """Encrypt transcript for storage"""
        encrypted = self.cipher.encrypt(transcript.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_transcript(self, encrypted_transcript: str) -> str:
        """Decrypt transcript for processing"""
        decoded = base64.b64decode(encrypted_transcript.encode())
        decrypted = self.cipher.decrypt(decoded)
        return decrypted.decode()
```

---

## Testing Strategy

### Backend Testing
```python
# tests/test_transcription_service.py
import pytest
from unittest.mock import AsyncMock
from services.transcription_service import TranscriptionService

class TestTranscriptionService:
    @pytest.fixture
    async def transcription_service(self):
        mock_repo = AsyncMock()
        mock_whisper = AsyncMock()
        mock_queue = AsyncMock()
        
        return TranscriptionService(
            job_repo=mock_repo,
            whisper=mock_whisper,
            queue=mock_queue
        )
    
    async def test_enqueue_transcription(self, transcription_service):
        # Test job enqueueing
        job_id = await transcription_service.enqueue_transcription(
            session_id="test-session",
            settings={"languages": ["en"]}
        )
        
        assert job_id is not None
        # Verify job was created and queued
```

### Frontend Testing
```typescript
// src/__tests__/hooks/useTranscription.test.ts
import { renderHook, act } from '@testing-library/react-hooks';
import { useTranscription } from '../../hooks/useTranscription';

describe('useTranscription', () => {
  it('should start transcription and track progress', async () => {
    const { result } = renderHook(() => useTranscription());
    
    await act(async () => {
      const jobId = await result.current.startTranscription(
        'test-session',
        { languages: ['en'] }
      );
      
      expect(jobId).toBeDefined();
      expect(result.current.jobProgress.get(jobId)).toBe(0);
    });
  });
});
```

---

## Deployment Strategy

### Docker Configuration
```dockerfile
# Dockerfile.transcription-worker
FROM python:3.9-slim

WORKDIR /app

# Install dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "workers.transcription_worker"]
```

### Kubernetes Deployment
```yaml
# k8s/transcription-worker.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: transcription-workers
spec:
  replicas: 3
  selector:
    matchLabels:
      app: transcription-worker
  template:
    metadata:
      labels:
        app: transcription-worker
    spec:
      containers:
      - name: transcription-worker
        image: botmr/transcription-worker:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: MONGO_URL
          value: "mongodb://mongo-service:27017"
```

---

## Migration Timeline

### Phase 1: Foundation (Week 1)
- [ ] Implement modular backend structure
- [ ] Create transcription job models and database schema
- [ ] Set up basic queue system (in-memory for testing)
- [ ] Implement mock transcription service

### Phase 2: Core Transcription (Week 2)
- [ ] Integrate OpenAI Whisper API
- [ ] Implement speaker diarization (basic)
- [ ] Add NLP processing pipeline
- [ ] Create transcription API endpoints

### Phase 3: Advanced Features (Week 3)
- [ ] Real-time progress updates (WebSocket)
- [ ] Redaction service implementation
- [ ] Performance optimization
- [ ] Error handling and retry logic

### Phase 4: Testing & Polish (Week 4)
- [ ] Comprehensive testing suite
- [ ] Performance benchmarking
- [ ] Security audit
- [ ] Documentation updates

---

This implementation plan provides a solid foundation for building the advanced Transcription & Analysis feature while maintaining the modular architecture and ensuring scalability for future enhancements.