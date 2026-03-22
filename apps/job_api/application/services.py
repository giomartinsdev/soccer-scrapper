"""Application services (use cases)."""

from typing import Dict, List, Optional

from apps.common.logging import setup_logging
from apps.common.utils import generate_uuid
from apps.job_api.application.ports import JobQueuePort, JobRepositoryPort
from apps.job_api.domain.entities import Job, JobStatus
from apps.job_api.domain.value_objects import ScrapEndpoint


logger = setup_logging(__name__)


class JobApplicationService:
    """Application service for job operations."""

    def __init__(
        self, repository: JobRepositoryPort, queue: Optional[JobQueuePort] = None
    ):
        self.repository = repository
        self.queue = queue

    async def create_scrap_job(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Job:
        """Create and enqueue a scraping job."""
        job_id = generate_uuid()
        endpoint_enum = ScrapEndpoint(endpoint)

        logger.info(f"Creating scrap job {job_id} for endpoint {endpoint}")

        job = Job(
            id=job_id, endpoint=endpoint, params=params or {}, status=JobStatus.PENDING
        )

        saved_job = await self.repository.save(job)

        if self.queue:
            self.queue.publish_job(saved_job)

        logger.info(f"Job {job_id} created and queued")

        return saved_job

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        return await self.repository.get_by_id(job_id)

    async def list_jobs(
        self, skip: int = 0, limit: int = 50, status: Optional[str] = None
    ) -> List[Job]:
        """List jobs with optional status filter."""
        jobs = await self.repository.list_jobs(skip, limit)

        if status:
            jobs = [j for j in jobs if j.status.value == status]

        return jobs

    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
    ) -> Optional[Job]:
        """Update job status."""
        job = await self.repository.get_by_id(job_id)
        if not job:
            return None

        if status == JobStatus.RUNNING:
            job.mark_running()
        elif status == JobStatus.COMPLETED:
            job.mark_completed(result or {})
        elif status == JobStatus.FAILED:
            job.mark_failed(error or "Unknown error")

        return await self.repository.save(job)
