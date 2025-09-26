"""
Health check and system status endpoints
"""
from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Dict, Any

from ...models.common import HealthCheck, BaseResponse
from ...core.config import get_settings
from ...core.db import get_database
from ...core.queue import get_queue
from ...core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/", response_model=BaseResponse)
async def root():
    """Root endpoint"""
    settings = get_settings()
    return BaseResponse(
        success=True,
        message=f"{settings.app_name} is running",
        data={"version": settings.app_version}
    )

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Comprehensive health check"""
    try:
        settings = get_settings()
        services = {}
        
        # Check database connection
        try:
            db = await get_database()
            await db.command("ping")
            services["database"] = "healthy"
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            services["database"] = "unhealthy"
        
        # Check job queue
        try:
            queue = await get_queue()
            stats = await queue.get_queue_stats()
            services["queue"] = "healthy"
            services["queue_stats"] = stats
        except Exception as e:
            logger.error("Queue health check failed", error=str(e))
            services["queue"] = "unhealthy"
        
        # Overall status
        overall_status = "healthy" if all(
            status == "healthy" for status in services.values() 
            if isinstance(status, str)
        ) else "degraded"
        
        return HealthCheck(
            status=overall_status,
            timestamp=datetime.utcnow(),
            services=services,
            version=settings.app_version
        )
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return HealthCheck(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            services={"error": str(e)},
            version="unknown"
        )

@router.get("/ready")
async def readiness_check():
    """Readiness probe for Kubernetes"""
    try:
        # Quick checks for readiness
        db = await get_database()
        await db.command("ping")
        
        return {"status": "ready"}
        
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        return {"status": "not ready", "error": str(e)}