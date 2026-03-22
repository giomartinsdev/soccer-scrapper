"""Application services."""

from typing import Any, Dict, List, Optional

from apps.common.logging import setup_logging
from apps.persist_api.infrastructure.repositories import MongoScrapedDataRepository


logger = setup_logging(__name__)


class PersistApplicationService:
    """Application service for querying persisted data."""

    def __init__(self, repository: MongoScrapedDataRepository):
        self.repository = repository

    async def get_leagues(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Get persisted leagues."""
        return await self.repository.get_by_type("leagues", skip, limit)

    async def get_teams(
        self, country: Optional[str] = None, skip: int = 0, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get persisted teams with optional country filter."""
        teams = await self.repository.get_by_type("teams", skip, limit)

        if country:
            teams = [t for t in teams if t.get("data", {}).get("country") == country]

        return teams

    async def get_events(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        league: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get persisted events with filters."""
        events = await self.repository.get_by_type("events", skip, limit)

        filtered = []
        for event in events:
            data = event.get("data", {})

            if date_from and data.get("date", "") < date_from:
                continue
            if date_to and data.get("date", "") > date_to:
                continue
            if league and data.get("league") != league:
                continue
            if status and data.get("status") != status:
                continue

            filtered.append(event)

        return filtered

    async def get_predictions(
        self, upcoming: Optional[bool] = None, skip: int = 0, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get persisted predictions."""
        predictions = await self.repository.get_by_type("predictions", skip, limit)

        if upcoming is True:
            predictions = [
                p for p in predictions if p.get("data", {}).get("status") == "upcoming"
            ]
        elif upcoming is False:
            predictions = [
                p for p in predictions if p.get("data", {}).get("status") != "upcoming"
            ]

        return predictions

    async def get_live(
        self, sport: Optional[str] = None, skip: int = 0, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get live matches from events."""
        events = await self.repository.get_by_type("events", skip, limit)
        live_statuses = [
            "1st_half",
            "2nd_half",
            "halftime",
            "extra_time",
            "penalty_shootout",
            "live",
            "in_progress",
            "playing",
            "1T",
            "2T",
            "ET",
            "PEN",
        ]
        live_events = [
            e
            for e in events
            if e.get("data", {}).get("status") in live_statuses
            or (
                e.get("data", {}).get("current_minute") is not None
                and e.get("data", {}).get("current_minute") > 0
            )
        ]

        if sport:
            live_events = [
                e
                for e in live_events
                if e.get("data", {}).get("league", {}).get("country", "").lower()
                == sport.lower()
            ]

        return live_events

    async def get_by_id(
        self, data_type: str, source_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get single document by source ID."""
        return await self.repository.get_by_source_id(data_type, source_id)
