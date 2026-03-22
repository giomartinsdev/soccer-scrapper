"""Celery tasks for scraping."""

from celery import Celery
from celery.schedules import crontab

from workers.common.logging import setup_logging
from workers.common.utils import generate_uuid
from workers.job_worker.config import settings
from workers.job_worker.slices.scrap.schemas import ScrapResult
from workers.job_worker.slices.scrap.services import ScrapingService


logger = setup_logging(__name__)

celery_app = Celery("job_worker", broker=settings.rabbitmq_url, backend=None)

celery_app.conf.task_queues = {
    settings.job_queue_name: {},
}

celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]

celery_app.conf.beat_schedule = {
    "scrape-live-football": {
        "task": "scrap.live",
        "schedule": 60.0,
        "args": (),
        "kwargs": {"params": {"sport": "football"}},
        "options": {"queue": settings.job_queue_name},
    },
    "scrape-live-tennis": {
        "task": "scrap.live",
        "schedule": 60.0,
        "args": (),
        "kwargs": {"params": {"sport": "tennis"}},
        "options": {"queue": settings.job_queue_name},
    },
    "scrape-live-hockey": {
        "task": "scrap.live",
        "schedule": 120.0,
        "args": (),
        "kwargs": {"params": {"sport": "hockey"}},
        "options": {"queue": settings.job_queue_name},
    },
    "scrape-events-hourly": {
        "task": "scrap.events",
        "schedule": 3600.0,
        "args": (),
        "kwargs": {"params": {}},
        "options": {"queue": settings.job_queue_name},
    },
    "scrape-predictions-quarter-hourly": {
        "task": "scrap.predictions",
        "schedule": 900.0,
        "args": (),
        "kwargs": {"params": {"upcoming": True}},
        "options": {"queue": settings.job_queue_name},
    },
    "scrape-leagues-daily": {
        "task": "scrap.leagues",
        "schedule": crontab(hour=6, minute=20),
        "args": (),
        "kwargs": {"params": {}},
        "options": {"queue": settings.job_queue_name},
    },
    "scrape-teams-daily": {
        "task": "scrap.teams",
        "schedule": crontab(hour=6, minute=30),
        "args": (),
        "kwargs": {"params": {}},
        "options": {"queue": settings.job_queue_name},
    },
}


@celery_app.task(bind=True, name="scrap.leagues")
def scrap_leagues(self, job_id: str = None, params: dict = None):
    """Task to scrape leagues."""
    job_id = job_id or generate_uuid()
    params = params or {}

    logger.info(f"Starting leagues scrap job {job_id}")

    service = ScrapingService()
    result = service.execute_job(
        {"id": job_id, "endpoint": "leagues", "params": params}
    )

    if result.success:
        publish_to_persist_queue(result)

    return {
        "job_id": job_id,
        "endpoint": "leagues",
        "items_count": result.items_count,
        "success": result.success,
        "error": result.error,
    }


@celery_app.task(bind=True, name="scrap.teams")
def scrap_teams(self, job_id: str = None, params: dict = None):
    """Task to scrape teams."""
    job_id = job_id or generate_uuid()
    params = params or {}
    country = params.get("country")

    logger.info(f"Starting teams scrap job {job_id} for country={country}")

    service = ScrapingService()
    result = service.execute_job(
        {
            "id": job_id,
            "endpoint": "teams",
            "params": {"country": country} if country else {},
        }
    )

    if result.success:
        publish_to_persist_queue(result)

    return {
        "job_id": job_id,
        "endpoint": "teams",
        "items_count": result.items_count,
        "success": result.success,
        "error": result.error,
    }


@celery_app.task(bind=True, name="scrap.events")
def scrap_events(self, job_id: str = None, params: dict = None):
    """Task to scrape events."""
    job_id = job_id or generate_uuid()
    params = params or {}

    logger.info(f"Starting events scrap job {job_id}")

    service = ScrapingService()
    result = service.execute_job({"id": job_id, "endpoint": "events", "params": params})

    if result.success:
        publish_to_persist_queue(result)

    return {
        "job_id": job_id,
        "endpoint": "events",
        "items_count": result.items_count,
        "success": result.success,
        "error": result.error,
    }


@celery_app.task(bind=True, name="scrap.live")
def scrap_live(self, job_id: str = None, params: dict = None):
    """Task to scrape live matches."""
    job_id = job_id or generate_uuid()
    params = params or {}

    logger.info(f"Starting live scrap job {job_id}")

    service = ScrapingService()
    result = service.execute_job({"id": job_id, "endpoint": "live", "params": params})

    if result.success:
        publish_to_persist_queue(result)

    return {
        "job_id": job_id,
        "endpoint": "live",
        "items_count": result.items_count,
        "success": result.success,
        "error": result.error,
    }


@celery_app.task(bind=True, name="scrap.predictions")
def scrap_predictions(self, job_id: str = None, params: dict = None):
    """Task to scrape predictions."""
    job_id = job_id or generate_uuid()
    params = params or {}

    upcoming = params.get("upcoming", True)
    logger.info(f"Starting predictions scrap job {job_id}, upcoming={upcoming}")

    service = ScrapingService()
    result = service.execute_job(
        {"id": job_id, "endpoint": "predictions", "params": params}
    )

    if result.success:
        publish_to_persist_queue(result)

    return {
        "job_id": job_id,
        "endpoint": "predictions",
        "items_count": result.items_count,
        "success": result.success,
        "error": result.error,
    }


@celery_app.task(name="scrap.generic")
def scrap_generic(job_data: dict):
    """Generic scraping task."""
    job_id = job_data.get("id", generate_uuid())
    endpoint = job_data.get("endpoint", "leagues")
    params = job_data.get("params", {})

    logger.info(f"Starting generic scrap job {job_id} for {endpoint}")

    service = ScrapingService()
    result = service.execute_job({"id": job_id, "endpoint": endpoint, "params": params})

    if result.success:
        publish_to_persist_queue(result)

    return {
        "job_id": job_id,
        "endpoint": endpoint,
        "items_count": result.items_count,
        "success": result.success,
        "error": result.error,
    }


def publish_to_persist_queue(result: ScrapResult):
    """Publish scraping result to persist queue."""
    from workers.persist_worker.main import persist_app
    from workers.job_worker.slices.scrap.services import ScrapingService as SS

    service = SS()
    persist_message = service.create_persist_message(result)

    persist_app.send_task(
        "persist.data",
        args=[],
        kwargs={
            "job_id": persist_message.job_id,
            "data_type": persist_message.data_type,
            "data": persist_message.data,
        },
        queue=settings.persist_queue_name,
    )

    logger.info(f"Published {len(persist_message.data)} items to persist queue")
