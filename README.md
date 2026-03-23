# Soccer Scrapper

Event-driven job processing system for scraping football data with React frontend.

## Project Structure

```
├── src/
│   ├── backend/           # Python backend (FastAPI + Celery)
│   │   ├── apps/         # FastAPI applications (DDD)
│   │   │   ├── job_api/     # Job creation API (port 8001)
│   │   │   └── persist_api/ # Data query API (port 8002)
│   │   ├── workers/      # Celery workers (Vertical Slice)
│   │   │   ├── job_worker/  # Scraping worker
│   │   │   └── persist_worker/ # Persistence worker
│   │   ├── requirements.txt
│   │   ├── Dockerfile.*   # Service Dockerfiles
│   │   └── docker-compose.yml
│   └── frontend/         # React frontend (port 5173 dev, 3000 prod)
├── docker-compose.yml    # Root compose for orchestration
└── .env                 # Environment variables
```

## Quick Start

### Start Backend (all services)
```bash
cd src/backend
docker compose up -d
```

### Start Frontend (dev)
```bash
cd src/frontend
npm install
npm run dev
```

### Start Frontend (production)
```bash
docker compose up -d frontend
```

## Frontend

The frontend displays:
- **Live Matches**: Real-time scores for ongoing matches
- **Top Predictions**: AI predictions sorted by confidence
- **Upcoming Events**: Scheduled matches with odds

### Development
```bash
cd src/frontend
npm run dev  # Runs on http://localhost:5173
```

### Production Build
```bash
cd src/frontend
npm run build
```

## Backend Services

| Service | Port | Description |
|---------|------|-------------|
| job-api | 8001 | Job creation API |
| persist-api | 8002 | Data query API |
| rabbitmq | 5672/15672 | Message queue |
| mongodb | 27017 | Database |
| redis | 6379 | Cache |

## API Endpoints

### Job API (`:8001`)
- `POST /api/job/scrap/jobs` - Create scraping job
- `GET /api/job/scrap/jobs` - List jobs
- `GET /api/job/scrap/jobs/{id}` - Get job by ID

### Data API (`:8002`)
- `GET /api/data/leagues` - List leagues
- `GET /api/data/teams` - List teams
- `GET /api/data/events` - List events
- `GET /api/data/live` - List live matches
- `GET /api/data/predictions` - List predictions

## Scheduled Tasks (Celery Beat)

| Task | Frequency |
|------|-----------|
| Live scraping (Football/Tennis) | Every 1 min |
| Live scraping (Hockey) | Every 2 min |
| Events scraping | Every 1 hour |
| Predictions scraping | Every 15 min |
| Leagues scraping | Daily 06:20 |
| Teams scraping | Daily 06:30 |
