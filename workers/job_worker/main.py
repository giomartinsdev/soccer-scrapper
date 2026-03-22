"""Job worker main module - exposes Celery app."""

from workers.job_worker.slices.scrap.tasks import celery_app as celery

__all__ = ["celery"]
