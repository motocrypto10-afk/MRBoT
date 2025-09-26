"""
Modern modular FastAPI server for BotMR
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from core.config import get_settings
from core.db import init_db, close_db
from core.queue import init_queue, close_queue
from core.logging import setup_logging
from api.router import create_api_router

# Get settings
settings = get_settings()

# Setup logging
setup_logging(level="DEBUG" if settings.debug else "INFO")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting BotMR application", version=settings.app_version)
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Initialize job queue
        await init_queue()
        logger.info("Job queue initialized successfully")
        
        # Register job handlers (TODO: implement job handlers)
        # await register_job_handlers()
        
        logger.info("BotMR application started successfully")
        
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down BotMR application")
        
        try:
            await close_queue()
            logger.info("Job queue closed")
        except Exception as e:
            logger.error("Error closing queue", error=str(e))
        
        try:
            await close_db()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error("Error closing database", error=str(e))
        
        logger.info("BotMR application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Modern Meeting Recording and AI Summarization API with modular architecture",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # Configure based on environment
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API routes
api_router = create_api_router()
app.include_router(api_router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.exception("Unhandled error in request", url=str(request.url))
    return HTTPException(
        status_code=500,
        detail={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {}
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server_new:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )