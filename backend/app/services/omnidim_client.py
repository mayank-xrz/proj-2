"""Thin async HTTP client for the OmniDimension REST API.

Docs: https://docs.omnidim.io/docs/api-reference/calls/dispatchCall
Auth: Bearer token via Authorization header.
"""

import httpx
from app.config import get_settings
from app.schemas.webhook import DispatchCallRequest, DispatchCallResponse


class OmniDimClient:
    """Async client for the OmniDimension v1 API."""

    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.omnidim_base_url
        self._api_key = settings.omnidim_api_key
        self._agent_id = settings.omnidim_agent_id

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    async def dispatch_call(
        self,
        phone_number: str,
        custom_variables: dict[str, str] | None = None,
    ) -> DispatchCallResponse:
        """Trigger an outbound call via OmniDimension POST /calls/dispatch."""
        payload = DispatchCallRequest(
            phone_number=phone_number,
            agent_id=self._agent_id,
            custom_variables=custom_variables or {},
        )
        async with httpx.AsyncClient(base_url=self._base_url, timeout=15) as client:
            resp = client.post(
                "/calls/dispatch",
                headers=self._headers(),
                json=payload.model_dump(),
            )
            resp.raise_for_status()
            return DispatchCallResponse(**resp.json())

    async def get_call_logs(self, call_id: str) -> dict:
        """Fetch call details from OmniDimension GET /calls/logs/{call_id}."""
        async with httpx.AsyncClient(base_url=self._base_url, timeout=15) as client:
            resp = client.get(f"/calls/logs/{call_id}", headers=self._headers())
            resp.raise_for_status()
            return resp.json()
