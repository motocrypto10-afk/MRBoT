"""
Database connection and migration utilities
"""
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DatabaseClient:
    _instance: Optional['DatabaseClient'] = None
    _client: Optional[AsyncIOMotorClient] = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self):
        """Initialize MongoDB connection"""
        if self._client is None:
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://127.0.0.1:27017')
            db_name = os.environ.get('DB_NAME', 'emergent')
            
            self._client = AsyncIOMotorClient(mongo_url)
            self._db = self._client[db_name]
            
            logger.info(f"Connected to MongoDB at {mongo_url}")
            
            # Verify connection
            try:
                await self._client.admin.command('ping')
                logger.info("MongoDB connection verified")
            except Exception as e:
                logger.error(f"MongoDB connection failed: {e}")
                raise

    async def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")

    @property
    def db(self):
        """Get database instance"""
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._db

    @property
    def client(self):
        """Get MongoDB client instance"""
        if self._client is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._client

# Global database instance
db_client = DatabaseClient()

async def get_database():
    """Get database instance"""
    return db_client.db

async def init_db():
    """Initialize database connection"""
    await db_client.connect()

async def close_db():
    """Close database connection"""
    await db_client.close()