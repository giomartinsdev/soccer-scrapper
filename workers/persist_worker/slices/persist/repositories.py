"""MongoDB repository for scraped data."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pymongo import MongoClient, ReplaceOne

from workers.common.logging import setup_logging
from workers.persist_worker.config import settings
from workers.persist_worker.slices.persist.schemas import DataType


logger = setup_logging(__name__)


class MongoRepository:
    """Repository for MongoDB operations."""

    _client: Optional[MongoClient] = None
    _db = None

    @classmethod
    def connect(cls):
        """Connect to MongoDB."""
        if cls._client is None:
            cls._client = MongoClient(settings.mongodb_url)
            cls._db = cls._client[settings.mongodb_db]
            logger.info(f"Connected to MongoDB: {settings.mongodb_db}")
            cls._ensure_indexes()

    @classmethod
    def disconnect(cls):
        """Disconnect from MongoDB."""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("Disconnected from MongoDB")

    @classmethod
    def _ensure_indexes(cls):
        """Ensure required indexes exist."""
        if cls._db is None:
            return

        collections = ["leagues", "teams", "events", "predictions"]
        for coll_name in collections:
            collection = cls._db[coll_name]
            collection.create_index("source_id", unique=True)
            collection.create_index("scraped_at")
            collection.create_index("job_id")

    @classmethod
    def get_collection(cls, data_type: DataType) -> str:
        """Get collection name for data type."""
        mapping = {
            DataType.LEAGUE: "leagues",
            DataType.TEAM: "teams",
            DataType.EVENT: "events",
            DataType.PREDICTION: "predictions",
        }
        return mapping.get(data_type, "unknown")

    @classmethod
    def upsert_data(
        cls,
        data_type: DataType,
        source_id: str,
        data: Dict[str, Any],
        job_id: Optional[str] = None,
    ) -> bool:
        """Upsert a single document."""
        if cls._db is None:
            cls.connect()

        collection_name = cls.get_collection(data_type)
        collection = cls._db[collection_name]

        document = {
            "source_id": source_id,
            "data": data,
            "scraped_at": datetime.utcnow(),
            "job_id": job_id,
        }

        result = collection.update_one(
            {"source_id": source_id}, {"$set": document}, upsert=True
        )

        return result.acknowledged

    @classmethod
    def bulk_upsert(
        cls,
        data_type: DataType,
        items: List[Dict[str, Any]],
        job_id: Optional[str] = None,
    ) -> Dict[str, int]:
        """Bulk upsert documents."""
        if cls._db is None:
            cls.connect()

        if not items:
            return {"inserted": 0, "updated": 0, "skipped": 0}

        collection_name = cls.get_collection(data_type)
        collection = cls._db[collection_name]

        operations = []
        for item in items:
            source_id = str(item.get("id", item.get("source_id", "")))
            if not source_id:
                continue

            document = {
                "source_id": source_id,
                "data": item,
                "scraped_at": datetime.utcnow(),
                "job_id": job_id,
            }

            operations.append(
                ReplaceOne(
                    {"source_id": source_id},
                    document,
                    upsert=True,
                )
            )

        if operations:
            result = collection.bulk_write(operations, ordered=False)
            return {
                "inserted": result.upserted_count,
                "updated": result.modified_count,
                "skipped": 0,
            }

        return {"inserted": 0, "updated": 0, "skipped": 0}

    @classmethod
    def get_by_type(
        cls, data_type: DataType, skip: int = 0, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get documents by type."""
        if cls._db is None:
            cls.connect()

        collection_name = cls.get_collection(data_type)
        collection = cls._db[collection_name]

        cursor = collection.find().skip(skip).limit(limit).sort("scraped_at", -1)
        return list(cursor)

    @classmethod
    def get_by_source_id(
        cls, data_type: DataType, source_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get document by source ID."""
        if cls._db is None:
            cls.connect()

        collection_name = cls.get_collection(data_type)
        collection = cls._db[collection_name]

        return collection.find_one({"source_id": source_id})
