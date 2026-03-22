"""MongoDB repository."""

from typing import Any, Dict, List, Optional

from apps.common.logging import setup_logging
from apps.persist_api.infrastructure.mongodb import MongoDBClient


logger = setup_logging(__name__)


class MongoScrapedDataRepository:
    """Repository for querying scraped data from MongoDB."""

    @staticmethod
    async def get_by_type(
        collection_name: str, skip: int = 0, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get documents by collection name."""
        db = MongoDBClient.get_db()
        collection = db[collection_name]

        cursor = collection.find().skip(skip).limit(limit).sort("scraped_at", -1)
        documents = await cursor.to_list(length=limit)

        return documents

    @staticmethod
    async def get_by_source_id(
        collection_name: str, source_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get single document by source ID."""
        db = MongoDBClient.get_db()
        collection = db[collection_name]

        return await collection.find_one({"source_id": source_id})

    @staticmethod
    async def count(collection_name: str) -> int:
        """Count documents in collection."""
        db = MongoDBClient.get_db()
        collection = db[collection_name]

        return await collection.count_documents({})
