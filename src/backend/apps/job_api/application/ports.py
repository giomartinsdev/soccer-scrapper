"""Application ports (interfaces)."""

from typing import List, Optional
from abc import ABC, abstractmethod

from apps.job_api.domain.entities import Job


class JobRepositoryPort(ABC):
    """Port for job repository operations."""

    @abstractmethod
    async def save(self, job: Job) -> Job:
        """Save a job."""
        pass

    @abstractmethod
    async def get_by_id(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        pass

    @abstractmethod
    async def list_jobs(self, skip: int = 0, limit: int = 50) -> List[Job]:
        """List jobs with pagination."""
        pass


class JobQueuePort(ABC):
    """Port for job queue operations."""

    @abstractmethod
    def publish_job(self, job: Job) -> None:
        """Publish job to queue."""
        pass
