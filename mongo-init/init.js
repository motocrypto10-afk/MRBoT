// MongoDB initialization script
db = db.getSiblingDB('emergent');

// Create collections with indexes
db.createCollection('meetings');
db.createCollection('recording_sessions');
db.createCollection('tasks');
db.createCollection('messages');
db.createCollection('settings');
db.createCollection('transcription_jobs');

// Create indexes for better performance
db.meetings.createIndex({ "id": 1 }, { unique: true });
db.meetings.createIndex({ "created_at": -1 });
db.meetings.createIndex({ "status": 1 });
db.meetings.createIndex({ "title": "text", "summary": "text", "transcript": "text" });

db.recording_sessions.createIndex({ "session_id": 1 }, { unique: true });
db.recording_sessions.createIndex({ "device_id": 1 });
db.recording_sessions.createIndex({ "status": 1 });
db.recording_sessions.createIndex({ "created_at": -1 });

db.tasks.createIndex({ "id": 1 }, { unique: true });
db.tasks.createIndex({ "meeting_id": 1 });
db.tasks.createIndex({ "status": 1 });
db.tasks.createIndex({ "created_at": -1 });

db.messages.createIndex({ "id": 1 }, { unique: true });
db.messages.createIndex({ "meeting_id": 1 });
db.messages.createIndex({ "created_at": -1 });

db.transcription_jobs.createIndex({ "id": 1 }, { unique: true });
db.transcription_jobs.createIndex({ "meeting_id": 1 });
db.transcription_jobs.createIndex({ "status": 1 });
db.transcription_jobs.createIndex({ "created_at": -1 });

print('Database initialized successfully with indexes');