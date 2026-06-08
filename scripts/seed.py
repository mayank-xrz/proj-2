#!/usr/bin/env python3
"""Seed script — populates the database with demo call logs and appointments.

Run from the backend/ directory:
    python ../scripts/seed.py

The dashboard will display this data immediately without needing a real
OmniDimension account or live phone calls.
"""

import asyncio
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure the backend package is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.models.call import CallLog, CallStatus, CallOutcome
from app.models.appointment import Appointment, AppointmentStatus
from app.database import Base

fake = Faker()

DATABASE_URL = "sqlite+aiosqlite:///./backend/voice_receptionist.db"

SERVICES = [
    ("Routine Cleaning", 45, 120.0),
    ("Dental Exam", 30, 80.0),
    ("Teeth Whitening", 60, 299.0),
    ("Emergency Visit", 30, 150.0),
    ("X-Ray", 20, 75.0),
]

CALL_OUTCOMES = [
    CallOutcome.APPOINTMENT_BOOKED,
    CallOutcome.APPOINTMENT_BOOKED,
    CallOutcome.APPOINTMENT_BOOKED,
    CallOutcome.FAQ_ANSWERED,
    CallOutcome.FAQ_ANSWERED,
    CallOutcome.HUNG_UP,
    CallOutcome.VOICEMAIL,
    CallOutcome.UNKNOWN,
]

SUMMARIES = [
    "Caller booked a routine cleaning for next Tuesday at 10am.",
    "Patient asked about insurance — confirmed Delta Dental coverage.",
    "Scheduled a teeth whitening appointment. Patient mentioned referral from Dr. Smith.",
    "Caller inquired about parking. Agent confirmed free parking is available.",
    "Emergency visit booked for this afternoon at 2pm. Patient has a toothache.",
    "Patient asked about pricing for X-Ray. Agent provided pricing information.",
    "Caller wanted to reschedule; transferred to front desk.",
    "New patient booked a dental exam for next week.",
    "Caller asked about children's dentistry. Agent confirmed all ages are treated.",
    "Payment plan inquiry — agent directed caller to CareCredit information.",
]


async def seed() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as db:
        now = datetime.now(timezone.utc)

        # ------------------------------------------------------------------
        # Seed call logs (last 14 days)
        # ------------------------------------------------------------------
        call_ids: list[str] = []
        print("Seeding call logs...")
        for i in range(25):
            started = now - timedelta(days=i % 14, hours=fake.random_int(0, 8))
            duration = fake.random_int(45, 480)
            outcome = CALL_OUTCOMES[i % len(CALL_OUTCOMES)]
            status = CallStatus.COMPLETED if outcome != CallOutcome.UNKNOWN else CallStatus.MISSED

            call = CallLog(
                id=str(uuid.uuid4()),
                omnidim_call_id=f"omni_{uuid.uuid4().hex[:16]}",
                caller_number=fake.phone_number(),
                caller_name=fake.name() if fake.boolean(chance_of_getting_true=70) else None,
                status=status,
                outcome=outcome,
                duration_seconds=float(duration),
                summary=SUMMARIES[i % len(SUMMARIES)],
                transcript=f"Agent: Hello, thank you for calling {fake.company()} Dental. How can I help you today?\n"
                           f"Caller: {fake.sentence()}\n"
                           f"Agent: {fake.sentence()}\n"
                           f"Caller: {fake.sentence()}\n"
                           f"Agent: Is there anything else I can help you with?\n"
                           f"Caller: No, that's all. Thank you!\n"
                           f"Agent: Have a great day!",
                started_at=started,
                ended_at=started + timedelta(seconds=duration),
                created_at=started,
            )
            db.add(call)
            call_ids.append(call.id)

        await db.flush()
        print(f"  ✓ {len(call_ids)} call logs created")

        # ------------------------------------------------------------------
        # Seed appointments (mix of upcoming + past)
        # ------------------------------------------------------------------
        print("Seeding appointments...")
        appt_count = 0
        for i in range(20):
            # Mix upcoming and past appointments
            if i < 12:
                appt_dt = now + timedelta(days=i + 1, hours=9 + (i % 4))
                appt_status = AppointmentStatus.CONFIRMED
            else:
                appt_dt = now - timedelta(days=i - 11, hours=9 + (i % 4))
                appt_status = AppointmentStatus.COMPLETED if i % 4 != 0 else AppointmentStatus.NO_SHOW

            service_name, duration, price = SERVICES[i % len(SERVICES)]
            patient_name = fake.name()

            appt = Appointment(
                id=str(uuid.uuid4()),
                call_log_id=call_ids[i % len(call_ids)] if i < len(call_ids) else None,
                patient_name=patient_name,
                patient_phone=fake.phone_number(),
                patient_email=fake.email() if fake.boolean(chance_of_getting_true=60) else None,
                service=service_name,
                appointment_dt=appt_dt,
                duration_minutes=duration,
                status=appt_status,
                notes=fake.sentence() if fake.boolean(chance_of_getting_true=40) else None,
                price_usd=price,
                created_at=appt_dt - timedelta(days=fake.random_int(1, 7)),
                updated_at=appt_dt - timedelta(days=fake.random_int(0, 2)),
            )
            db.add(appt)
            appt_count += 1

        await db.commit()
        print(f"  ✓ {appt_count} appointments created")

    await engine.dispose()
    print("\n✅ Seed complete! Start the backend and frontend to see demo data in the dashboard.")


if __name__ == "__main__":
    asyncio.run(seed())
