"""FastAPI application for persist-api."""

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Query, status
from pydantic import BaseModel

from apps.common.logging import setup_logging
from apps.persist_api.application.services import PersistApplicationService
from apps.persist_api.config import settings
from apps.persist_api.infrastructure.mongodb import MongoDBClient
from apps.persist_api.infrastructure.repositories import MongoScrapedDataRepository


logger = setup_logging(__name__)

repository = MongoScrapedDataRepository()
service = PersistApplicationService(repository)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting persist-api...")
    await MongoDBClient.connect()
    yield
    logger.info("Shutting down persist-api...")
    await MongoDBClient.disconnect()


app = FastAPI(
    title="Persist API",
    description="API for querying persisted scraping data",
    version="1.0.0",
    lifespan=lifespan,
)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str


class DataListResponse(BaseModel):
    """Generic data list response."""

    items: List[Any]
    total: int
    skip: int
    limit: int


class DataItemResponse(BaseModel):
    """Single data item response."""

    data: Dict[str, Any]


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", service="persist-api")


@app.get("/api/v1/leagues", response_model=DataListResponse, tags=["leagues"])
async def get_leagues(
    skip: int = Query(default=0, ge=0), limit: int = Query(default=50, ge=1, le=100)
):
    """Get all persisted leagues."""
    items = await service.get_leagues(skip=skip, limit=limit)
    total = await repository.count("leagues")

    return DataListResponse(
        items=[item.get("data", {}) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@app.get("/api/v1/teams", response_model=DataListResponse, tags=["teams"])
async def get_teams(
    country: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """Get all persisted teams."""
    items = await service.get_teams(country=country, skip=skip, limit=limit)
    total = await repository.count("teams")

    return DataListResponse(
        items=[item.get("data", {}) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@app.get("/api/v1/events", response_model=DataListResponse, tags=["events"])
async def get_events(
    date_from: Optional[str] = Query(
        default=None, description="Filter by start date (YYYY-MM-DD)"
    ),
    date_to: Optional[str] = Query(
        default=None, description="Filter by end date (YYYY-MM-DD)"
    ),
    league: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """Get all persisted events with optional filters."""
    items = await service.get_events(
        date_from=date_from,
        date_to=date_to,
        league=league,
        status=status,
        skip=skip,
        limit=limit,
    )
    total = await repository.count("events")

    return DataListResponse(
        items=[item.get("data", {}) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@app.get("/api/v1/predictions", response_model=DataListResponse, tags=["predictions"])
async def get_predictions(
    upcoming: Optional[bool] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """Get all persisted predictions."""
    items = await service.get_predictions(upcoming=upcoming, skip=skip, limit=limit)
    total = await repository.count("predictions")

    return DataListResponse(
        items=[item.get("data", {}) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@app.get("/api/v1/live", response_model=DataListResponse, tags=["live"])
async def get_live(
    sport: Optional[str] = Query(
        default=None, description="Filter by sport (football, tennis, etc.)"
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """Get all live matches."""
    items = await service.get_live(sport=sport, skip=skip, limit=limit)
    total = await repository.count("events")

    return DataListResponse(
        items=[item.get("data", {}) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@app.get(
    "/api/v1/{collection}/{source_id}", response_model=DataItemResponse, tags=["data"]
)
async def get_by_source_id(collection: str, source_id: str):
    """Get single item by source ID."""
    item = await service.get_by_id(collection, source_id)

    if not item:
        return DataItemResponse(data={})

    return DataItemResponse(data=item.get("data", {}))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "apps.persist_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
