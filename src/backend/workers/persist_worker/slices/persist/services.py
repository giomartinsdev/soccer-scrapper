"""Business logic for persistence."""

from typing import Any, Dict, List, Optional

from workers.common.logging import setup_logging
from workers.persist_worker.config import settings
from workers.persist_worker.slices.persist.repositories import MongoRepository
from workers.persist_worker.slices.persist.schemas import DataType, PersistResult


logger = setup_logging(__name__)


class PersistenceService:
    """Service for persisting scraped data."""

    def __init__(self):
        self.batch_size = settings.batch_size
        self.upsert_enabled = settings.upsert_enabled

    def persist_data(
        self, data_type: str, data: List[Dict[str, Any]], job_id: Optional[str] = None
    ) -> PersistResult:
        """Persist scraped data to MongoDB."""
        result = PersistResult(
            job_id=job_id or "unknown", data_type=DataType(data_type), success=True
        )

        try:
            data_type_enum = DataType(data_type)

            total_items = len(data)
            logger.info(
                f"Persisting {total_items} items of type {data_type} (job: {job_id})"
            )

            if total_items == 0:
                logger.info("No items to persist")
                return result

            if total_items <= self.batch_size:
                stats = MongoRepository.bulk_upsert(data_type_enum, data, job_id)
                result.items_persisted = stats.get("inserted", 0)
                result.items_updated = stats.get("updated", 0)
            else:
                for i in range(0, total_items, self.batch_size):
                    batch = data[i : i + self.batch_size]
                    stats = MongoRepository.bulk_upsert(data_type_enum, batch, job_id)
                    result.items_persisted += stats.get("inserted", 0)
                    result.items_updated += stats.get("updated", 0)
                    logger.info(
                        f"Batch {i // self.batch_size + 1}: "
                        f"{stats.get('inserted', 0)} inserted, "
                        f"{stats.get('updated', 0)} updated"
                    )

            logger.info(
                f"Persistence complete for job {job_id}: "
                f"{result.items_persisted} persisted, {result.items_updated} updated"
            )

        except Exception as e:
            result.success = False
            result.error = str(e)
            logger.error(f"Persistence failed for job {job_id}: {e}")

        return result

    def get_leagues(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Get persisted leagues."""
        documents = MongoRepository.get_by_type(DataType.LEAGUE, skip, limit)
        return [doc["data"] for doc in documents]

    def get_teams(
        self, country: Optional[str] = None, skip: int = 0, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get persisted teams."""
        documents = MongoRepository.get_by_type(DataType.TEAM, skip, limit)
        teams = [doc["data"] for doc in documents]
        if country:
            teams = [t for t in teams if t.get("country") == country]
        return teams

    def get_events(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        league: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get persisted events."""
        documents = MongoRepository.get_by_type(DataType.EVENT, skip, limit)
        events = [doc["data"] for doc in documents]

        if date_from:
            events = [e for e in events if e.get("date", "") >= date_from]
        if date_to:
            events = [e for e in events if e.get("date", "") <= date_to]
        if league:
            events = [e for e in events if e.get("league") == league]

        return events

    def get_predictions(
        self, upcoming: bool = True, skip: int = 0, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get persisted predictions."""
        documents = MongoRepository.get_by_type(DataType.PREDICTION, skip, limit)
        predictions = [doc["data"] for doc in documents]

        if upcoming:
            predictions = [p for p in predictions if p.get("status") == "upcoming"]

        return predictions
