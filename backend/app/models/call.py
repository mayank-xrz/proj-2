"""ORM model for call log records."""

from datetime import datetime
from sqlalchemy import String, DateTime, Text, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.database import Base


class CallStatus(str, enum.Enum):
    INCOMING = "incoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MISSED = "missed"
    FAILED = "failed"


class CallOutcome(str, enum.Enum):
    APPOINTMENT_BOOKED = "appointment_booked"
    FAQ_ANSWERED = "faq_answered"
    TRANSFERRED = "transferred"
    VOICEMAIL = "voicemail"
    HUNG_UP = "hung_up"
    UNKNOWN = "unknown"


class CallLog(Base):
    """Persisted record of every inbound call handled by the voice agent."""

    __tablename__ = "call_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    omnidim_call_id: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True, index=True)
    caller_number: Mapped[str] = mapped_column(String(32))
    caller_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[CallStatus] = mapped_column(SAEnum(CallStatus), default=CallStatus.INCOMING)
    outcome: Mapped[CallOutcome] = mapped_column(SAEnum(CallOutcome), default=CallOutcome.UNKNOWN)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
