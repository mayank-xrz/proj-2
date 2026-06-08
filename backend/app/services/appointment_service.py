"""Service layer for appointment booking and management."""

import uuid
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.config import load_business_config


async def book_appointment(db: AsyncSession, payload: AppointmentCreate) -> Appointment:
    """Create a new confirmed appointment record."""
    config = load_business_config()
    price = _resolve_price(payload.service, payload.price_usd, config)
    duration = _resolve_duration(payload.service, payload.duration_minutes, config)

    appt = Appointment(
        id=str(uuid.uuid4()),
        call_log_id=payload.call_log_id,
        patient_name=payload.patient_name,
        patient_phone=payload.patient_phone,
        patient_email=payload.patient_email,
        service=payload.service,
        appointment_dt=payload.appointment_dt,
        duration_minutes=duration,
        status=AppointmentStatus.CONFIRMED,
        notes=payload.notes,
        price_usd=price,
    )
    db.add(appt)
    await db.flush()
    return appt


async def update_appointment(
    db: AsyncSession,
    appointment_id: str,
    payload: AppointmentUpdate,
) -> Appointment | None:
    """Partially update an existing appointment."""
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appt = result.scalar_one_or_none()
    if not appt:
        return None
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(appt, field, value)
    appt.updated_at = datetime.utcnow()
    await db.flush()
    return appt


async def cancel_appointment(db: AsyncSession, appointment_id: str) -> Appointment | None:
    """Cancel an appointment by ID."""
    return await update_appointment(
        db, appointment_id, AppointmentUpdate(status=AppointmentStatus.CANCELLED)
    )


async def list_appointments(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    status: AppointmentStatus | None = None,
) -> tuple[int, list[Appointment]]:
    """Return paginated appointments, upcoming first, optionally filtered by status."""
    query = select(Appointment)
    count_query = select(func.count(Appointment.id))
    if status:
        query = query.where(Appointment.status == status)
        count_query = count_query.where(Appointment.status == status)
    total = (await db.execute(count_query)).scalar_one()
    items = list(
        (
            await db.execute(
                query.order_by(Appointment.appointment_dt.asc()).offset(skip).limit(limit)
            )
        )
        .scalars()
        .all()
    )
    return total, items


async def get_appointment(db: AsyncSession, appointment_id: str) -> Appointment | None:
    """Fetch a single appointment by its ID."""
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    return result.scalar_one_or_none()


def _resolve_price(service: str, override: float | None, config: dict) -> float | None:
    if override is not None:
        return override
    for svc in config.get("services", []):
        if svc["name"].lower() == service.lower():
            return svc.get("price_usd")
    return None


def _resolve_duration(service: str, override: int, config: dict) -> int:
    for svc in config.get("services", []):
        if svc["name"].lower() == service.lower():
            return svc.get("duration_minutes", override)
    return override
