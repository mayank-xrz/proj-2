"""Pydantic schemas for OmniDimension webhook payloads.

Based on the OmniDimension official API documentation (omnidim.io / docs.omnidim.io).
OmniDimension delivers POST-call webhook events as HTTP POST requests to your
registered callback URL (configured in the agent's Post-Call tab in the dashboard).

Authentication: Bearer token via `Authorization: Bearer YOUR_API_KEY`
Base API URL: https://backend.omnidim.io/api/v1

Webhook payload shape documented at:
  https://docs.omnidim.io/docs/dashboard-guides/post-call
  https://docs.omnidim.io/docs/api-reference/calls/dispatchCall

Doc version: June 2025 (OmniDimension docs are continuously updated;
Python SDK latest release: September 2024 — pip install omnidimension)
"""

from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# OmniDimension call report sub-models
# ---------------------------------------------------------------------------


class CallReport(BaseModel):
    """AI-generated post-call analysis included in the webhook payload."""

    summary: str | None = None
    sentiment: str | None = None
    # extracted_variables is a free-form dict of key/value pairs configured
    # in the OmniDimension agent instructions (e.g. patient_name, service, etc.)
    extracted_variables: dict[str, Any] = Field(default_factory=dict)


class ConversationMessage(BaseModel):
    """A single turn in the conversation."""

    speaker: str  # "agent" | "user"
    message: str


class ConversationData(BaseModel):
    """Full conversation transcript included in the webhook payload."""

    full_transcript: str | None = None
    interaction_sequence: list[ConversationMessage] = Field(default_factory=list)
    # Raw messages array as [speaker, message] pairs
    messages_array: list[list[str]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Top-level OmniDimension webhook payload
# ---------------------------------------------------------------------------


class OmniDimWebhookEvent(BaseModel):
    """Root envelope for OmniDimension post-call webhook deliveries.

    OmniDimension sends this as an HTTP POST after every completed call.
    The receiving endpoint must respond with HTTP 200 OK.
    """

    # Call identification
    call_id: str | None = None
    phone_number: str | None = None      # caller / recipient number
    to_number: str | None = None         # called party
    from_number_id: str | None = None    # OmniDimension phone number resource ID

    # Agent metadata
    bot_name: str | None = None
    agent_id: str | None = None

    # Outcome
    call_status: str = "unknown"  # "success" | "not_picked_up" | "dispatched" | etc.
    call_date: str | None = None
    timestamp: datetime | None = None

    # Post-call AI analysis
    call_report: CallReport = Field(default_factory=CallReport)
    conversation: ConversationData = Field(default_factory=ConversationData)

    # Raw pass-through for any extra fields OmniDimension adds in future versions
    extra: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "allow"}


class DispatchCallRequest(BaseModel):
    """Payload for POST /calls/dispatch — trigger an outbound call from OmniDimension."""

    phone_number: str
    agent_id: str
    custom_variables: dict[str, str] = Field(default_factory=dict)


class DispatchCallResponse(BaseModel):
    """Response from OmniDimension /calls/dispatch endpoint."""

    success: bool
    status: str
    request_id: str | None = None
    custom_variables_count: int | None = None


class WebhookResponse(BaseModel):
    """Standard HTTP 200 response returned to OmniDimension after webhook delivery."""

    received: bool = True
    message: str = "ok"
