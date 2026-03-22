"""Domain entities."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    """Job aggregate root."""

    id: str
    type: str = "scrap"
    endpoint: str
    params: Dict[str, Any] = Field(default_factory=dict)
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def mark_running(self) -> None:
        """Mark job as running."""
        self.status = JobStatus.RUNNING
        self.updated_at = datetime.utcnow()

    def mark_completed(self, result: Dict[str, Any]) -> None:
        """Mark job as completed."""
        self.status = JobStatus.COMPLETED
        self.result = result
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        """Mark job as failed."""
        self.status = JobStatus.FAILED
        self.error = error
        self.updated_at = datetime.utcnow()
