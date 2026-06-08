"""Pydantic schemas for call log API responses."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.call import CallStatus, CallOutcome


class CallLogRead(BaseModel):
    """Public representation of a call log record."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    omnidim_call_id: str | None
    caller_number: str
    caller_name: str | None
    status: CallStatus
    outcome: CallOutcome
    duration_seconds: float | None
    summary: str | None
    started_at: datetime
    ended_at: datetime | None
    created_at: datetime


class CallLogList(BaseModel):
    """Paginated list of call logs."""

    total: int
    items: list[CallLogRead]
