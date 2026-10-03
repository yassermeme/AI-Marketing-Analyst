# AI Marketing Analyst

Marketing and revenue intelligence that helps teams identify what changed, where it changed, and what to investigate.

## Phase 1: run locally

1. Copy configuration: `cp .env.example .env`.
2. Start the complete stack: `docker compose up --build`.
3. Open `http://localhost:5173`. The API health endpoint is `http://localhost:8000/api/v1/health`.

The health endpoint verifies PostgreSQL and Redis independently and returns HTTP 503 until every required dependency is reachable.

## Architecture

- `frontend/`: React, TypeScript, Vite, Tailwind, and Recharts UI.
- `backend/`: FastAPI service with dependency-aware health checks and Celery configuration.
- `database/migrations/`: versioned schema migration home (Phase 2).
- `database/seed/`: seed data home (Phase 3).
- `docker/`: container definitions.

All secrets and connection configuration are supplied through environment variables. See `.env.example`.

## Phase 2 database

Apply the schema from an empty database with `cd backend && alembic upgrade head`. For a deterministic local data set after migration, run `python -m app.seed`. The seed creates two organizations, six campaigns per organization, 90 days of daily spend, and 360 linked lead records with qualified-lead, appointment, opportunity, sale, and revenue events.
