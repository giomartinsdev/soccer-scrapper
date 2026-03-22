"""In-memory job repository implementation."""

from typing import Dict, List, Optional

from apps.common.logging import setup_logging
from apps.job_api.application.ports import JobRepositoryPort
from apps.job_api.domain.entities import Job


logger = setup_logging(__name__)


class InMemoryJobRepository(JobRepositoryPort):
    """In-memory implementation of job repository."""

    _store: Dict[str, Job] = {}

    async def save(self, job: Job) -> Job:
        """Save job to memory."""
        self._store[job.id] = job
        logger.debug(f"Saved job {job.id}")
        return job

    async def get_by_id(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        return self._store.get(job_id)

    async def list_jobs(self, skip: int = 0, limit: int = 50) -> List[Job]:
        """List jobs sorted by created_at descending."""
        jobs = sorted(self._store.values(), key=lambda j: j.created_at, reverse=True)
        return jobs[skip : skip + limit]
