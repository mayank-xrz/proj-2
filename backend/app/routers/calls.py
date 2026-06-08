"""Router for call log read endpoints."""

from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.call import CallLogRead, CallLogList
from app.services.call_service import list_calls

router = APIRouter(prefix="/calls", tags=["calls"])


@router.get("", response_model=CallLogList)
async def get_calls(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> CallLogList:
    """Return paginated call logs, newest first."""
    total, items = await list_calls(db, skip=skip, limit=limit)
    return CallLogList(total=total, items=[CallLogRead.model_validate(c) for c in items])


@router.get("/{call_id}", response_model=CallLogRead)
async def get_call(
    call_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CallLogRead:
    """Fetch a single call log by ID."""
    from sqlalchemy import select
    from app.models.call import CallLog
    from fastapi import HTTPException

    result = await db.execute(select(CallLog).where(CallLog.id == call_id))
    call = result.scalar_one_or_none()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return CallLogRead.model_validate(call)
