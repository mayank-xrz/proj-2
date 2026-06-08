"""FastAPI application entrypoint for the Voice Receptionist backend."""

import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings, load_business_config
from app.database import init_db
from app.routers import health, webhook, calls, appointments, faq

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lifespan (replaces deprecated @app.on_event)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting Voice Receptionist API — env=%s", settings.app_env)
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Voice Receptionist API shutting down")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

business_config = load_business_config()
business_name = business_config.get("business", {}).get("name", "Voice Receptionist")

app = FastAPI(
    title=f"{business_name} — Voice Receptionist API",
    description=(
        "Backend API for the AI Voice Receptionist powered by OmniDimension. "
        "Handles call logs, appointment bookings, FAQ resolution, and webhook events."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(health.router)
app.include_router(webhook.router, prefix="/api/v1")
app.include_router(calls.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(faq.router, prefix="/api/v1")
