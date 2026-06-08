"""Router for appointment management endpoints."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.appointment import AppointmentStatus
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentRead,
    AppointmentList,
    AppointmentUpdate,
)
from app.services.appointment_service import (
    book_appointment,
    cancel_appointment,
    get_appointment,
    list_appointments,
    update_appointment,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("", response_model=AppointmentList)
async def get_appointments(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    status: AppointmentStatus | None = Query(default=None),
) -> AppointmentList:
    """Return paginated appointments, upcoming first. Optionally filter by status."""
    total, items = await list_appointments(db, skip=skip, limit=limit, status=status)
    return AppointmentList(total=total, items=[AppointmentRead.model_validate(a) for a in items])


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    payload: AppointmentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AppointmentRead:
    """Manually book an appointment (useful for testing and admin use)."""
    appt = await book_appointment(db, payload)
    return AppointmentRead.model_validate(appt)


@router.get("/{appointment_id}", response_model=AppointmentRead)
async def get_appointment_by_id(
    appointment_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AppointmentRead:
    """Fetch a single appointment by ID."""
    appt = await get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return AppointmentRead.model_validate(appt)


@router.patch("/{appointment_id}", response_model=AppointmentRead)
async def update_appointment_by_id(
    appointment_id: str,
    payload: AppointmentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AppointmentRead:
    """Partially update an appointment (reschedule, change status, etc.)."""
    appt = await update_appointment(db, appointment_id, payload)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return AppointmentRead.model_validate(appt)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment_by_id(
    appointment_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Cancel an appointment by ID."""
    appt = await cancel_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
