# Deployment Guide

## Prerequisites

- Public HTTPS URL (OmniDimension webhooks require HTTPS)
- PostgreSQL database (recommended for production)

## Option 1: Railway (easiest)

1. Push the repo to GitHub
2. Create a new Railway project → "Deploy from GitHub repo"
3. Add a PostgreSQL service in Railway
4. Set environment variables in Railway dashboard (see README env table)
5. Change `DATABASE_URL` to Railway's PostgreSQL connection string (use asyncpg driver):
   ```
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
   ```
6. Set the start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Deploy the frontend as a second Railway service or on Vercel

## Option 2: Render

1. Create a Web Service from GitHub
2. **Build command:** `pip install -r backend/requirements.txt`
3. **Start command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add a PostgreSQL addon and copy the connection string to `DATABASE_URL`

## Option 3: Fly.io

```bash
fly launch --name voice-receptionist
fly postgres create --name voice-receptionist-db
fly secrets set OMNIDIM_API_KEY=sk-omni-your-key ...
fly deploy
```

## Option 4: Docker

A `Dockerfile` and `docker-compose.yml` are on the roadmap. For now, run backend and frontend separately.

## Switching from SQLite to PostgreSQL

Install the asyncpg driver:
```bash
pip install asyncpg
```

Set `DATABASE_URL`:
```
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/voice_receptionist
```

The SQLAlchemy models are database-agnostic — no other changes needed.

## Setting the OmniDimension webhook URL

Once deployed, configure your OmniDimension agent's Post-Call webhook to:
```
https://your-domain.com/api/v1/webhooks/omnidim
```

Copy the signing secret from OmniDimension and set `OMNIDIM_WEBHOOK_SECRET`.

## Frontend deployment (Vercel)

```bash
cd frontend
vercel deploy --prod
```

Set `NEXT_PUBLIC_API_URL` to your backend's public URL in Vercel's environment settings.
