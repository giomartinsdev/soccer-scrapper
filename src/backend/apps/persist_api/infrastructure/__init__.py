"""Infrastructure package."""

from apps.persist_api.infrastructure.mongodb import MongoDBClient
from apps.persist_api.infrastructure.repositories import MongoScrapedDataRepository


__all__ = ["MongoDBClient", "MongoScrapedDataRepository"]
