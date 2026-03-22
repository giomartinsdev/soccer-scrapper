# Soccer Scraper - Job Processing & Persistence System

## Overview

Event-driven job processing system for scraping football/soccer data from the Bzzoiro Sports API with vertical slice architecture for workers and DDD for APIs.

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

### 1. job-api (FastAPI - DDD)
- **Location**: `apps/job-api/`
- **Responsibility**: Accept scraping job requests, enqueue to RabbitMQ
- **Endpoints**:
  - `POST /api/v1/scrap/jobs` - Create a scraping job
  - `GET /api/v1/scrap/jobs/{job_id}` - Get job status
  - `GET /api/v1/scrap/jobs` - List jobs

### 2. job-worker (Celery - Vertical Slice)
- **Location**: `workers/job_worker/`
- **Responsibility**: Execute scraping tasks against Bzzoiro API
- **Features**: Rate limiting, retry logic, error handling

### 3. persist-worker (Celery - Vertical Slice)
- **Location**: `workers/persist_worker/`
- **Responsibility**: Persist scraped data to MongoDB
- **Features**: Batch processing, upsert logic

### 4. persist-api (FastAPI - DDD)
- **Location**: `apps/persist-api/`
- **Responsibility**: Query persisted data
- **Endpoints**:
  - `GET /api/v1/leagues` - List leagues
  - `GET /api/v1/events` - List events (filterable)
  - `GET /api/v1/teams` - List teams

## Data Models

### Job
```python
{
    "id": "uuid",
    "type": "scrap",
    "status": "pending|running|completed|failed",
    "params": {
        "endpoint": "leagues|events|teams|predictions",
        "filters": {}
    },
    "created_at": "datetime",
    "updated_at": "datetime",
    "result": {} | null
}
```

### ScrapedData (MongoDB)
```python
{
    "_id": "ObjectId",
    "type": "league|team|event|prediction",
    "source_id": "string",
    "data": {},
    "scraped_at": "datetime",
    "job_id": "uuid"
}
```

## Configuration

Environment variables via `.env`:
```
# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672//

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=soccer_scrapper

# Bzzoiro API
BZZOIRO_API_URL=https://sports.bzzoiro.com/api
BZZOIRO_API_TOKEN=x

# Redis (Celery broker)
REDIS_URL=redis://localhost:6379/0

# API
JOB_API_HOST=0.0.0.0
JOB_API_PORT=8001
PERSIST_API_HOST=0.0.0.0
PERSIST_API_PORT=8002
```

## Vertical Slice Structure (Workers)

```
workers/
├── job_worker/
│   ├── __init__.py
│   ├── main.py              # Celery app entry
│   ├── config.py            # Configuration
│   └── slices/
│       └── scrap/
│           ├── __init__.py
│           ├── tasks.py     # Task definitions
│           ├── services.py  # Business logic
│           ├── clients.py   # External API client
│           └── schemas.py   # Data schemas
├── persist_worker/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   └── slices/
│       └── persist/
│           ├── __init__.py
│           ├── tasks.py
│           ├── services.py
│           ├── repositories.py
│           └── schemas.py
└── common/
    ├── __init__.py
    ├── logging.py
    └── utils.py
```

## DDD Structure (APIs)

```
apps/
├── job-api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities.py     # Job entity
│   │   └── value_objects.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services.py      # Use cases
│   │   └── ports.py        # Interfaces
│   └── infrastructure/
│       ├── __init__.py
│       ├── rabbitmq.py     # RabbitMQ adapter
│       └── repositories.py
├── persist-api/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities.py
│   │   └── value_objects.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services.py
│   │   └── ports.py
│   └── infrastructure/
│       ├── __init__.py
│       ├── mongodb.py
│       └── repositories.py
└── common/
    ├── __init__.py
    ├── logging.py
    └── utils.py
```

## Queue Configuration

### job.queue
- Queue for scraping tasks
- Exchange: `scrap.exchange`
- Routing key: `scrap.task`

### persist.queue
- Queue for persistence tasks
- Exchange: `persist.exchange`
- Routing key: `persist.task`

## Event Flow

1. User → POST /api/v1/scrap/jobs → job-api
2. job-api → Publish to job.queue → RabbitMQ
3. job-worker → Consume from job.queue
4. job-worker → Scrap data from Bzzoiro API
5. job-worker → Publish result to persist.queue
6. persist-worker → Consume from persist.queue
7. persist-worker → Persist to MongoDB
8. User → GET /api/v1/events → persist-api → MongoDB

## Dependencies

```
# requirements.txt
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
celery>=5.3.0
redis>=5.0.0
aio-pika>=9.3.0
motor>=3.3.0
httpx>=0.26.0
python-dotenv>=1.0.0
```

## Run Commands

```bash
# Start job-api
uvicorn apps.job-api.main:app --host 0.0.0.0 --port 8001 --reload

# Start persist-api
uvicorn apps.persist-api.main:app --host 0.0.0.0 --port 8002 --reload

# Start job-worker
celery -A workers.job_worker.main worker --loglevel=info -Q job.queue

# Start persist-worker
celery -A workers.persist_worker.main worker --loglevel=info -Q persist.queue
```

## TODO

- [x] Create project structure
- [x] Implement common utilities
- [x] Implement job-api (FastAPI + DDD)
- [x] Implement job-worker (Celery + Vertical Slice)
- [x] Implement persist-worker (Celery + Vertical Slice)
- [x] Implement persist-api (FastAPI + DDD)
- [x] Add docker-compose for infrastructure
- [ ] Add tests
