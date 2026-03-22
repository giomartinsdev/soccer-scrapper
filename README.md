# Soccer Scraper

Event-driven job processing system for scraping football data with DDD and Vertical Slice Architecture.

## Architecture

```
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌────────────┐
│  User   │────▶│ job-api │────▶│ job.queue   │────▶│ job-worker │
└─────────┘     └─────────┘     └─────────────┘     └────────────┘
                                                              │
                                                              ▼
                                                      ┌─────────────┐
                                                      │persist.queue│
                                                      └─────────────┘
                                                              │
                    ┌─────────┐     ┌─────────────┐          │
                    │  User   │◀────│ persist-api │◀─────────┤
                    └─────────┘     └─────────────┘          ▼
                                                         ┌────────────┐
                                                         │persist-worker│
                                                         └────────────┘
                                                              │
                                                              ▼
                                                           ┌────────┐
                                                           │MongoDB │
                                                           └────────┘
```

## Components

- **job-api**: FastAPI service for creating scraping jobs (DDD)
- **job-worker**: Celery worker for executing scrap tasks (Vertical Slice)
- **persist-worker**: Celery worker for persisting data to MongoDB (Vertical Slice)
- **persist-api**: FastAPI service for querying persisted data (DDD)

## Quick Start

### 1. Start Infrastructure

```bash
docker-compose up -d
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Copy Environment File

```bash
cp .env.example .env
```

### 4. Start APIs

```bash
# Terminal 1: Job API
uvicorn apps.job-api.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2: Persist API
uvicorn apps.persist-api.main:app --host 0.0.0.0 --port 8002 --reload
```

### 5. Start Workers

```bash
# Terminal 3: Job Worker
celery -A workers.job_worker.main worker --loglevel=info -Q job.queue

# Terminal 4: Persist Worker
celery -A workers.persist_worker.main worker --loglevel=info -Q persist.queue
```

## API Endpoints

### Job API (Port 8001)

- `POST /api/v1/scrap/jobs` - Create a scraping job
- `GET /api/v1/scrap/jobs/{job_id}` - Get job status
- `GET /api/v1/scrap/jobs` - List all jobs

### Persist API (Port 8002)

- `GET /api/v1/leagues` - List leagues
- `GET /api/v1/teams` - List teams (filter by country)
- `GET /api/v1/events` - List events (filter by date, league, status)
- `GET /api/v1/predictions` - List predictions

## Usage Example

```bash
# Create a job to scrape leagues
curl -X POST http://localhost:8001/api/v1/scrap/jobs \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "leagues"}'

# Query persisted data
curl http://localhost:8002/api/v1/leagues
```

## Scraping Endpoints

Available endpoints for scraping:
- `leagues` - All football leagues
- `teams` - Teams (filter by country)
- `events` - Events (filter by date_from, date_to, league, status)
- `live` - Live matches
- `predictions` - ML predictions (filter by upcoming)
