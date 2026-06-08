"""Router handling incoming OmniDimension webhook events.

OmniDimension fires a single HTTP POST after each completed call (configured
in the agent's Post-Call tab → Webhook delivery). The payload contains call
metadata, AI-generated summary, sentiment, extracted variables, and transcript.

Authentication: We verify the HMAC-SHA256 signature from the
X-Omnidim-Signature header. In demo mode (placeholder secret) verification
is skipped so the project boots without a real OmniDimension account.

Reference: https://docs.omnidim.io/docs/dashboard-guides/post-call
"""

import hashlib
import hmac
import logging
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.call import CallLog, CallStatus, CallOutcome
from app.schemas.webhook import OmniDimWebhookEvent, WebhookResponse
from app.schemas.appointment import AppointmentCreate
from app.services import appointment_service
from app.services.call_service import create_call_log, get_call_by_omnidim_id
from app.services.faq_service import resolve_faq

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()


def _verify_signature(body: bytes, signature: str | None) -> None:
    """Verify HMAC-SHA256 signature. Skip in demo mode (placeholder secret)."""
    if settings.omnidim_webhook_secret == "whsec_placeholder":
        return
    if not signature:
        raise HTTPException(status_code=400, detail="Missing X-Omnidim-Signature header")
    expected = hmac.new(
        settings.omnidim_webhook_secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


@router.post("/omnidim", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
async def omnidim_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_omnidim_signature: Annotated[str | None, Header(alias="X-Omnidim-Signature")] = None,
) -> WebhookResponse:
    """Receive a post-call webhook from OmniDimension.

    Must return HTTP 200 quickly. Heavy work (email confirmation, CRM sync)
    should be moved to a background task queue in production.
    """
    body = await request.body()
    _verify_signature(body, x_omnidim_signature)

    try:
        event = OmniDimWebhookEvent.model_validate_json(body)
    except Exception as exc:
        logger.warning("Failed to parse OmniDimension webhook: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc))

    logger.info(
        "OmniDimension webhook | call_id=%s status=%s bot=%s",
        event.call_id,
        event.call_status,
        event.bot_name,
    )

    await _process_event(event, db)
    return WebhookResponse(received=True, message="ok")


async def _process_event(event: OmniDimWebhookEvent, db: AsyncSession) -> None:
    """Upsert call log and optionally create an appointment from extracted vars."""
    outcome = _infer_outcome(event)
    ev = event.call_report.extracted_variables
    now = datetime.now(timezone.utc)

    # ------------------------------------------------------------------ #
    # 1. Upsert call log
    # ------------------------------------------------------------------ #
    call_log = None
    if event.call_id:
        call_log = await get_call_by_omnidim_id(db, event.call_id)

    if call_log is None:
        call_log = await create_call_log(
            db,
            omnidim_call_id=event.call_id,
            caller_number=event.phone_number or "unknown",
            status=CallStatus.COMPLETED,
            outcome=outcome,
            transcript=event.conversation.full_transcript,
            summary=event.call_report.summary,
            started_at=event.timestamp or now,
            ended_at=event.timestamp or now,
        )
    else:
        call_log.status = CallStatus.COMPLETED
        call_log.outcome = outcome
        call_log.transcript = event.conversation.full_transcript
        call_log.summary = event.call_report.summary
        call_log.ended_at = event.timestamp or now
        await db.flush()

    # ------------------------------------------------------------------ #
    # 2. Book appointment if agent extracted booking variables
    # ------------------------------------------------------------------ #
    if ev.get("patient_name") and ev.get("appointment_datetime"):
        try:
            appt_dt = datetime.fromisoformat(ev["appointment_datetime"])
            payload = AppointmentCreate(
                patient_name=ev["patient_name"],
                patient_phone=event.phone_number or ev.get("patient_phone", "unknown"),
                patient_email=ev.get("patient_email"),
                service=ev.get("service", "General Appointment"),
                appointment_dt=appt_dt,
                notes=ev.get("notes"),
                call_log_id=call_log.id,
            )
            await appointment_service.book_appointment(db, payload)
            call_log.outcome = CallOutcome.APPOINTMENT_BOOKED
            logger.info("Appointment booked from webhook call_id=%s", event.call_id)
        except Exception as exc:
            logger.error("Failed to book appointment from webhook: %s", exc)

    # ------------------------------------------------------------------ #
    # 3. Log FAQ resolution (informational only — agent already answered)
    # ------------------------------------------------------------------ #
    if event.call_report.summary and outcome == CallOutcome.FAQ_ANSWERED:
        matched = resolve_faq(event.call_report.summary)
        if matched:
            logger.info(
                "FAQ matched call_id=%s confidence=%.2f", event.call_id, matched["confidence"]
            )


def _infer_outcome(event: OmniDimWebhookEvent) -> CallOutcome:
    """Map OmniDimension call_status / extracted variables to an internal outcome."""
    ev = event.call_report.extracted_variables
    if ev.get("appointment_datetime") or ev.get("patient_name"):
        return CallOutcome.APPOINTMENT_BOOKED
    if event.call_report.summary and len(event.call_report.summary) > 20:
        return CallOutcome.FAQ_ANSWERED
    return {
        "not_picked_up": CallOutcome.HUNG_UP,
        "voicemail": CallOutcome.VOICEMAIL,
        "transferred": CallOutcome.TRANSFERRED,
    }.get(event.call_status, CallOutcome.UNKNOWN)
