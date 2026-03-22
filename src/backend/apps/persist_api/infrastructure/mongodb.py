"""MongoDB client."""

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from apps.common.logging import setup_logging
from apps.persist_api.config import settings


logger = setup_logging(__name__)


class MongoDBClient:
    """MongoDB client singleton."""

    _client: Optional[AsyncIOMotorClient] = None
    _db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls):
        """Connect to MongoDB."""
        if cls._client is None:
            cls._client = AsyncIOMotorClient(settings.mongodb_url)
            cls._db = cls._client[settings.mongodb_db]
            logger.info(f"Connected to MongoDB: {settings.mongodb_db}")

    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB."""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("Disconnected from MongoDB")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if cls._db is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return cls._db
