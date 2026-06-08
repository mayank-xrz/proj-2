"""Pydantic schemas for appointment API endpoints."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from app.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    """Payload for booking a new appointment."""

    patient_name: str
    patient_phone: str
    patient_email: str | None = None
    service: str
    appointment_dt: datetime
    duration_minutes: int = 30
    notes: str | None = None
    price_usd: float | None = None
    call_log_id: str | None = None

    @field_validator("patient_name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("patient_name must not be empty")
        return v.strip()


class AppointmentUpdate(BaseModel):
    """Partial update payload for an existing appointment."""

    status: AppointmentStatus | None = None
    appointment_dt: datetime | None = None
    notes: str | None = None
    service: str | None = None


class AppointmentRead(BaseModel):
    """Public representation of an appointment."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    call_log_id: str | None
    patient_name: str
    patient_phone: str
    patient_email: str | None
    service: str
    appointment_dt: datetime
    duration_minutes: int
    status: AppointmentStatus
    notes: str | None
    price_usd: float | None
    created_at: datetime
    updated_at: datetime


class AppointmentList(BaseModel):
    """Paginated list of appointments."""

    total: int
    items: list[AppointmentRead]
