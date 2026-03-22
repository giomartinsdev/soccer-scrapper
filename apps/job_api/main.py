"""FastAPI application for job-api."""

from contextlib import asynccontextmanager
from typing import List, Optional

from celery import Celery
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

from apps.common.logging import setup_logging
from apps.job_api.application.services import JobApplicationService
from apps.job_api.config import settings
from apps.job_api.domain.entities import Job, JobStatus
from apps.job_api.domain.value_objects import ScrapEndpoint
from apps.job_api.infrastructure.repositories import InMemoryJobRepository


logger = setup_logging(__name__)

celery_app = Celery("job_api", broker=settings.rabbitmq_url, backend=None)
celery_app.conf.task_queues = {settings.job_queue_name: {}}

repository = InMemoryJobRepository()
service = JobApplicationService(repository, None)


def publish_to_queue(job: Job) -> None:
    """Publish job to RabbitMQ via Celery."""
    task_map = {
        "leagues": "scrap.leagues",
        "teams": "scrap.teams",
        "events": "scrap.events",
        "live": "scrap.live",
        "predictions": "scrap.predictions",
    }
    task_name = task_map.get(job.endpoint, "scrap.generic")

    celery_app.send_task(
        task_name,
        args=[job.id],
        kwargs={"params": job.params},
        queue=settings.job_queue_name,
    )
    logger.info(f"Published job {job.id} to queue with task {task_name}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting job-api...")
    yield
    logger.info("Shutting down job-api...")


app = FastAPI(
    title="Job API",
    description="API for managing scraping jobs",
    version="1.0.0",
    lifespan=lifespan,
)


class CreateJobRequest(BaseModel):
    """Request model for creating a job."""

    endpoint: str = Field(
        ..., description="Scraping endpoint (leagues, teams, events, live, predictions)"
    )
    params: Optional[dict] = Field(
        default_factory=dict, description="Optional filters/parameters"
    )


class JobResponse(BaseModel):
    """Response model for a job."""

    id: str
    type: str
    endpoint: str
    params: dict
    status: str
    created_at: str
    updated_at: str
    result: Optional[dict] = None
    error: Optional[str] = None


class JobListResponse(BaseModel):
    """Response model for job list."""

    items: List[JobResponse]
    total: int
    skip: int
    limit: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", service="job-api")


@app.post(
    "/api/v1/scrap/jobs",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["jobs"],
)
async def create_job(request: CreateJobRequest):
    """Create a new scraping job."""
    valid_endpoints = [e.value for e in ScrapEndpoint]
    if request.endpoint not in valid_endpoints:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid endpoint. Must be one of: {valid_endpoints}",
        )

    try:
        job = await service.create_scrap_job(
            endpoint=request.endpoint, params=request.params
        )

        publish_to_queue(job)

        return JobResponse(
            id=job.id,
            type=job.type,
            endpoint=job.endpoint,
            params=job.params,
            status=job.status.value,
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat(),
        )
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/api/v1/scrap/jobs/{job_id}", response_model=JobResponse, tags=["jobs"])
async def get_job(job_id: str):
    """Get a job by ID."""
    job = await service.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found"
        )

    return JobResponse(
        id=job.id,
        type=job.type,
        endpoint=job.endpoint,
        params=job.params,
        status=job.status.value,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
        result=job.result,
        error=job.error,
    )


@app.get("/api/v1/scrap/jobs", response_model=JobListResponse, tags=["jobs"])
async def list_jobs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    status: Optional[str] = None,
):
    """List all jobs with optional filtering."""
    jobs = await service.list_jobs(skip=skip, limit=limit, status=status)

    return JobListResponse(
        items=[
            JobResponse(
                id=j.id,
                type=j.type,
                endpoint=j.endpoint,
                params=j.params,
                status=j.status.value,
                created_at=j.created_at.isoformat(),
                updated_at=j.updated_at.isoformat(),
                result=j.result,
                error=j.error,
            )
            for j in jobs
        ],
        total=len(jobs),
        skip=skip,
        limit=limit,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "apps.job_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
