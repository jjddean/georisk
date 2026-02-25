# GeoRisk V1

Premium risk advisory layer for freight forwarders.

## Project Structure

- `apps/api`: FastAPI backend providing the REST API.
- `apps/web`: Next.js frontend for the dashboard.
- `apps/worker`: Celery worker for background ingestion and scoring.
- `infra`: Infrastructure configurations (Docker Compose).

## Getting Started

### 1. Infrastructure
Spin up Postgres and Redis:
```bash
docker-compose -f infra/docker-compose.yml up -d
```

### 2. Backend (API)
```bash
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Frontend (Web)
```bash
cd apps/web
npm install
npm run dev
```

### 4. Worker
```bash
cd apps/worker
pip install -r requirements.txt
celery -A main worker --loglevel=info
```

## V1 Scope
- Portfolio-first lane monitoring.
- Rule-based risk scoring (0-100).
- Decision-ready alternatives.
- Client-ready PDF reports.
