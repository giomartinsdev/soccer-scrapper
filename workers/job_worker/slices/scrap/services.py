"""Business logic for scraping (sync version for Celery)."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from workers.common.logging import setup_logging
from workers.common.utils import generate_uuid, utc_now
from workers.job_worker.config import settings
from workers.job_worker.slices.scrap.clients import BzzoiroClient, BzzoiroApiError
from workers.job_worker.slices.scrap.schemas import (
    PersistMessage,
    ScrapEndpoint,
    ScrapJob,
    ScrapResult,
)


logger = setup_logging(__name__)


class ScrapingService:
    """Service for executing scraping jobs."""

    def __init__(self):
        self.client = BzzoiroClient()
        self.max_retries = settings.max_retries
        self.retry_delay = settings.retry_delay

    def execute_job(self, job_data: Dict[str, Any]) -> ScrapResult:
        """Execute a scraping job."""
        job_id = job_data.get("id", generate_uuid())
        endpoint = job_data.get("endpoint", "leagues")
        params = job_data.get("params", {})

        logger.info(f"Executing scrap job {job_id} for endpoint {endpoint}")

        result = ScrapResult(
            job_id=job_id,
            endpoint=ScrapEndpoint(endpoint),
            data=[],
            items_count=0,
            success=True,
        )

        try:
            data = self.client.fetch(endpoint, params)
            result.data = data
            result.items_count = len(data)
            logger.info(f"Scrap job {job_id} completed: {result.items_count} items")
        except BzzoiroApiError as e:
            result.success = False
            result.error = str(e)
            logger.error(f"Scrap job {job_id} failed: {e}")
        except Exception as e:
            result.success = False
            result.error = f"Unexpected error: {str(e)}"
            logger.error(f"Scrap job {job_id} failed with unexpected error: {e}")

        return result

    def create_persist_message(self, result: ScrapResult) -> PersistMessage:
        """Create a persist message from scrap result."""
        data_type_map = {
            ScrapEndpoint.LEAGUES: "league",
            ScrapEndpoint.TEAMS: "team",
            ScrapEndpoint.EVENTS: "event",
            ScrapEndpoint.LIVE: "event",
            ScrapEndpoint.PREDICTIONS: "prediction",
        }

        return PersistMessage(
            job_id=result.job_id,
            data_type=data_type_map.get(result.endpoint, "unknown"),
            data=result.data,
            created_at=result.scraped_at,
        )
