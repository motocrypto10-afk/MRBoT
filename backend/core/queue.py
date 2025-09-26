"""
Job queue management for asynchronous processing
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
import json
from enum import Enum

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class Job:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    priority: int = 1  # Higher number = higher priority

class JobQueue:
    """Simple in-memory job queue - replace with Redis/RQ in production"""
    
    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._topics: Dict[str, Callable] = {}
        self._running = False
        self._workers = []

    async def enqueue(self, topic: str, payload: Dict[str, Any], priority: int = 1) -> str:
        """Add job to queue"""
        job = Job(
            topic=topic,
            payload=payload,
            priority=priority
        )
        self._jobs[job.id] = job
        
        logger.info(f"Job {job.id} enqueued for topic '{topic}'")
        return job.id

    def register_handler(self, topic: str, handler: Callable):
        """Register handler for topic"""
        self._topics[topic] = handler
        logger.info(f"Handler registered for topic '{topic}'")

    async def get_job_status(self, job_id: str) -> Optional[Job]:
        """Get job status"""
        return self._jobs.get(job_id)

    async def start_workers(self, num_workers: int = 2):
        """Start background workers"""
        self._running = True
        
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)
        
        logger.info(f"Started {num_workers} workers")

    async def stop_workers(self):
        """Stop background workers"""
        self._running = False
        
        for worker in self._workers:
            worker.cancel()
        
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        
        logger.info("All workers stopped")

    async def _worker(self, worker_id: str):
        """Background worker to process jobs"""
        logger.info(f"Worker {worker_id} started")
        
        while self._running:
            try:
                # Find highest priority pending job
                pending_jobs = [
                    job for job in self._jobs.values() 
                    if job.status == JobStatus.PENDING
                ]
                
                if not pending_jobs:
                    await asyncio.sleep(1)
                    continue
                
                # Sort by priority (highest first)
                job = max(pending_jobs, key=lambda j: j.priority)
                
                # Process job
                await self._process_job(job, worker_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
        
        logger.info(f"Worker {worker_id} stopped")

    async def _process_job(self, job: Job, worker_id: str):
        """Process a single job"""
        handler = self._topics.get(job.topic)
        if not handler:
            job.status = JobStatus.FAILED
            job.error = f"No handler for topic '{job.topic}'"
            logger.error(f"Job {job.id} failed: {job.error}")
            return

        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        
        logger.info(f"Worker {worker_id} processing job {job.id} (topic: {job.topic})")
        
        try:
            # Call handler
            result = await handler(job.payload)
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            logger.info(f"Job {job.id} completed successfully by {worker_id}")
            
        except Exception as e:
            job.error = str(e)
            job.retry_count += 1
            
            if job.retry_count <= job.max_retries:
                job.status = JobStatus.RETRYING
                logger.warning(f"Job {job.id} failed, retrying ({job.retry_count}/{job.max_retries}): {e}")
                
                # Reset to pending for retry
                await asyncio.sleep(2 ** job.retry_count)  # Exponential backoff
                job.status = JobStatus.PENDING
                
            else:
                job.status = JobStatus.FAILED
                logger.error(f"Job {job.id} failed permanently after {job.retry_count} retries: {e}")

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        status_counts = {}
        for status in JobStatus:
            status_counts[status.value] = len([
                job for job in self._jobs.values() 
                if job.status == status
            ])
        
        return {
            "total_jobs": len(self._jobs),
            "status_counts": status_counts,
            "registered_topics": list(self._topics.keys()),
            "workers_running": len(self._workers)
        }

# Global queue instance
job_queue = JobQueue()

async def get_queue() -> JobQueue:
    """Get job queue instance"""
    return job_queue

async def init_queue():
    """Initialize job queue"""
    await job_queue.start_workers(num_workers=2)

async def close_queue():
    """Close job queue"""
    await job_queue.stop_workers()