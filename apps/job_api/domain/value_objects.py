"""Domain value objects."""

from enum import Enum
from typing import Any, Dict
from pydantic import BaseModel, Field


class ScrapEndpoint(str, Enum):
    """Available scraping endpoints."""

    LEAGUES = "leagues"
    TEAMS = "teams"
    EVENTS = "events"
    LIVE = "live"
    PREDICTIONS = "predictions"


class JobParams(BaseModel):
    """Job parameters value object."""

    endpoint: ScrapEndpoint
    filters: Dict[str, Any] = Field(default_factory=dict)

    def to_celery_kwargs(self) -> Dict[str, Any]:
        """Convert to Celery task kwargs."""
        kwargs = {}
        if self.endpoint == ScrapEndpoint.TEAMS and "country" in self.filters:
            kwargs["country"] = self.filters["country"]
        elif self.endpoint == ScrapEndpoint.EVENTS:
            kwargs.update(
                {
                    k: v
                    for k, v in self.filters.items()
                    if k in ["date_from", "date_to", "league", "status"]
                }
            )
        elif self.endpoint == ScrapEndpoint.PREDICTIONS:
            kwargs["upcoming"] = self.filters.get("upcoming", True)
        return kwargs
