"""Service layer for call log persistence and retrieval."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call import CallLog, CallStatus, CallOutcome


async def create_call_log(
    db: AsyncSession,
    *,
    omnidim_call_id: str | None,
    caller_number: str,
    caller_name: str | None = None,
    status: CallStatus = CallStatus.COMPLETED,
    outcome: CallOutcome = CallOutcome.UNKNOWN,
    duration_seconds: float | None = None,
    transcript: str | None = None,
    summary: str | None = None,
    started_at: datetime | None = None,
    ended_at: datetime | None = None,
) -> CallLog:
    """Persist a new call log record."""
    now = datetime.now(timezone.utc)
    call = CallLog(
        id=str(uuid.uuid4()),
        omnidim_call_id=omnidim_call_id,
        caller_number=caller_number,
        caller_name=caller_name,
        status=status,
        outcome=outcome,
        duration_seconds=duration_seconds,
        transcript=transcript,
        summary=summary,
        started_at=started_at or now,
        ended_at=ended_at,
        created_at=now,
    )
    db.add(call)
    await db.flush()
    return call


async def get_call_by_omnidim_id(db: AsyncSession, omnidim_call_id: str) -> CallLog | None:
    """Look up a call by its OmniDimension call ID."""
    result = await db.execute(
        select(CallLog).where(CallLog.omnidim_call_id == omnidim_call_id)
    )
    return result.scalar_one_or_none()


async def list_calls(db: AsyncSession, skip: int = 0, limit: int = 50) -> tuple[int, list[CallLog]]:
    """Return paginated call logs newest-first."""
    count_result = await db.execute(select(func.count(CallLog.id)))
    total = count_result.scalar_one()
    result = await db.execute(
        select(CallLog).order_by(CallLog.created_at.desc()).offset(skip).limit(limit)
    )
    return total, list(result.scalars().all())
