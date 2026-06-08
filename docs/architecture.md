# Architecture Notes

## Overview

Voice Receptionist is a three-layer system:

```
OmniDimension Platform (cloud)
        │
        │ HTTP POST (post-call webhook)
        ▼
FastAPI Backend (Python)
        │
        │ SQL (async SQLAlchemy)
        ▼
SQLite / PostgreSQL
        │
        │ REST API (JSON)
        ▼
Next.js Dashboard (browser)
```

## Backend structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app factory, CORS, startup
│   ├── config.py            # pydantic-settings + YAML loader
│   ├── database.py          # async engine, session, Base, init_db
│   ├── models/
│   │   ├── call.py          # CallLog ORM model
│   │   └── appointment.py   # Appointment ORM model
│   ├── schemas/
│   │   ├── webhook.py       # OmniDimension payload schemas
│   │   ├── call.py          # API response schemas for calls
│   │   └── appointment.py   # API schemas for appointments
│   ├── services/
│   │   ├── call_service.py          # Call log persistence
│   │   ├── appointment_service.py   # Booking logic
│   │   ├── faq_service.py           # FAQ fuzzy matching
│   │   └── omnidim_client.py        # OmniDimension HTTP client
│   └── routers/
│       ├── health.py        # GET /health
│       ├── webhook.py       # POST /api/v1/webhooks/omnidim
│       ├── calls.py         # GET /api/v1/calls
│       ├── appointments.py  # CRUD /api/v1/appointments
│       └── faq.py           # GET+POST /api/v1/faq
└── business_config.yaml     # Per-business configuration
```

## Design decisions

### Single webhook endpoint
OmniDimension delivers one post-call webhook per call. We don't need separate events for call.started / call.ended — the full context arrives after the call completes. This simplifies the backend considerably.

### SQLite for development
SQLite requires zero infrastructure and supports async via `aiosqlite`. Switch to PostgreSQL for production by changing `DATABASE_URL` — SQLAlchemy handles the rest.

### FAQ matching
Uses Python's `difflib.SequenceMatcher` + keyword overlap for simplicity. Sufficient for a business with 5–50 FAQs. For larger knowledge bases, replace with a vector embedding approach (e.g. sentence-transformers + pgvector).

### No background task queue
Webhook processing is synchronous within the request. This is fine for the expected call volume of a local business (< 100 calls/day). For high-volume deployments, move processing to Celery or ARQ.

### Pydantic v2
All request/response validation uses Pydantic v2 models with `model_validate` / `model_dump`. The `ConfigDict(from_attributes=True)` pattern is used on all ORM-mapped response schemas.
