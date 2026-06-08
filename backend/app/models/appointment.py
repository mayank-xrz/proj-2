"""ORM model for appointment bookings."""

from datetime import datetime
from sqlalchemy import String, DateTime, Text, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.database import Base


class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class Appointment(Base):
    """A booked appointment captured by the voice agent."""

    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    call_log_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    patient_name: Mapped[str] = mapped_column(String(128))
    patient_phone: Mapped[str] = mapped_column(String(32))
    patient_email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    service: Mapped[str] = mapped_column(String(128))
    appointment_dt: Mapped[datetime] = mapped_column(DateTime, index=True)
    duration_minutes: Mapped[int] = mapped_column(default=30)
    status: Mapped[AppointmentStatus] = mapped_column(
        SAEnum(AppointmentStatus), default=AppointmentStatus.PENDING
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
