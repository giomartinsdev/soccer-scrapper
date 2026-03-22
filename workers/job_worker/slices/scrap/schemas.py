"""Data schemas for scraping."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ScrapEndpoint(str, Enum):
    """Available scraping endpoints."""

    LEAGUES = "leagues"
    TEAMS = "teams"
    EVENTS = "events"
    LIVE = "live"
    PREDICTIONS = "predictions"


class JobStatus(str, Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScrapJob(BaseModel):
    """Scrap job model."""

    id: str
    type: str = "scrap"
    endpoint: ScrapEndpoint
    params: Dict[str, Any] = Field(default_factory=dict)
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ScrapResult(BaseModel):
    """Result from scraping operation."""

    job_id: str
    endpoint: ScrapEndpoint
    data: List[Dict[str, Any]]
    items_count: int
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    success: bool = True
    error: Optional[str] = None


class PersistMessage(BaseModel):
    """Message to send to persist queue."""

    job_id: str
    data_type: str
    data: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.utcnow)
