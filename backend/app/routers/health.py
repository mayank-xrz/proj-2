"""Health-check endpoint."""

from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str


@router.get("/health", response_model=HealthResponse, summary="Application health check")
async def health() -> HealthResponse:
    """Returns service health status. Used by load balancers and monitoring."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(tz=timezone.utc),
        version="1.0.0",
    )
