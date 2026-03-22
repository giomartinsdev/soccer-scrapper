"""Domain entities."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class League(BaseModel):
    """League entity."""

    id: Optional[str] = None
    name: str
    country: Optional[str] = None
    logo_url: Optional[str] = None
    scraped_at: Optional[datetime] = None

    class Config:
        extra = "allow"


class Team(BaseModel):
    """Team entity."""

    id: Optional[str] = None
    name: str
    country: Optional[str] = None
    logo_url: Optional[str] = None
    league: Optional[str] = None
    scraped_at: Optional[datetime] = None

    class Config:
        extra = "allow"


class Event(BaseModel):
    """Event entity."""

    id: Optional[str] = None
    home_team: str
    away_team: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    league: Optional[str] = None
    scraped_at: Optional[datetime] = None

    class Config:
        extra = "allow"


class Prediction(BaseModel):
    """Prediction entity."""

    id: Optional[str] = None
    home_team: str
    away_team: str
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    odds: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    league: Optional[str] = None
    scraped_at: Optional[datetime] = None

    class Config:
        extra = "allow"
