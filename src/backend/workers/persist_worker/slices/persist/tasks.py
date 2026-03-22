"""Celery tasks for persistence."""

from typing import Any, Dict, List

from celery import Celery

from workers.common.logging import setup_logging
from workers.persist_worker.config import settings
from workers.persist_worker.slices.persist.services import PersistenceService


logger = setup_logging(__name__)

persist_app = Celery("persist_worker", broker=settings.rabbitmq_url, backend=None)

persist_app.conf.task_queues = {
    settings.persist_queue_name: {},
}

persist_app.conf.task_serializer = "json"
persist_app.conf.result_serializer = "json"
persist_app.conf.accept_content = ["json"]


@persist_app.task(bind=True, name="persist.data")
def persist_data(self, job_id: str, data_type: str, data: List[Dict[str, Any]]):
    """Task to persist scraped data."""
    logger.info(f"Starting persist task for job {job_id}, type {data_type}")

    service = PersistenceService()
    result = service.persist_data(data_type, data, job_id)

    return {
        "job_id": job_id,
        "data_type": data_type,
        "items_persisted": result.items_persisted,
        "items_updated": result.items_updated,
        "success": result.success,
        "error": result.error,
    }


@persist_app.task(name="persist.bulk")
def persist_bulk(batch_data: List[Dict[str, Any]]):
    """Task to persist multiple data types in bulk."""
    logger.info(f"Starting bulk persist task with {len(batch_data)} items")

    service = PersistenceService()
    results = []

    grouped = {}
    for item in batch_data:
        data_type = item.get("data_type", "unknown")
        if data_type not in grouped:
            grouped[data_type] = []
        grouped[data_type].append(item.get("data", {}))

    for data_type, items in grouped.items():
        job_id = f"bulk-{data_type}"
        result = service.persist_data(data_type, items, job_id)
        results.append(
            {
                "data_type": data_type,
                "items_persisted": result.items_persisted,
                "items_updated": result.items_updated,
                "success": result.success,
            }
        )

    return results
