"""Data schemas for persistence."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DataType(str, Enum):
    """Data types for persistence."""

    LEAGUE = "league"
    TEAM = "team"
    EVENT = "event"
    PREDICTION = "prediction"


class ScrapedData(BaseModel):
    """Model for persisted scraped data."""

    type: DataType
    source_id: str
    data: Dict[str, Any]
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    job_id: Optional[str] = None
    content_hash: Optional[str] = None


class PersistResult(BaseModel):
    """Result of persistence operation."""

    job_id: str
    data_type: DataType
    items_persisted: int = 0
    items_updated: int = 0
    items_skipped: int = 0
    success: bool = True
    error: Optional[str] = None
    completed_at: datetime = Field(default_factory=datetime.utcnow)
