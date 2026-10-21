"""Myntra PPMP/Omni partner token adapter."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx

from app.core.config import Settings
from app.integrations.base import ConnectionResult, MarketplaceAdapter, MarketplaceError


class MyntraPartnerAdapter(MarketplaceAdapter):
    marketplace = "myntra"

    def __init__(self, settings: Settings, transport: Optional[httpx.AsyncBaseTransport] = None):
        self.settings = settings
        self._transport = transport

    def _secret(self) -> str:
        return self.settings.myntra_secret_key.get_secret_value().strip() if self.settings.myntra_secret_key else ""

    def configuration_status(self) -> Dict[str, Any]:
        missing = []
        values = {"MYNTRA_API_BASE_URL": self.settings.myntra_api_base_url, "MYNTRA_MERCHANT_ID": self.settings.myntra_merchant_id, "MYNTRA_SECRET_KEY": self._secret()}
        missing.extend(name for name, value in values.items() if not value)
        return {"configured": not missing, "missing": missing}

    async def connect(self, **kwargs: Any) -> ConnectionResult:
        if not self.configuration_status()["configured"]:
            raise MarketplaceError("myntra_not_configured", "Myntra partner configuration is incomplete.", status_code=503)
        base = self.settings.myntra_api_base_url.rstrip("/")
        parsed = urlparse(base)
        if parsed.scheme != "https" or not parsed.netloc:
            raise MarketplaceError("myntra_invalid_base_url", "Myntra API base URL must be HTTPS.", status_code=503)
        try:
            async with httpx.AsyncClient(timeout=self.settings.marketplace_http_timeout_seconds, transport=self._transport) as client:
                response = await client.post(
                    f"{base}/authorization/generate_token",
                    headers={"secret_key": self._secret(), "Content-Type": "application/json"},
                    json={"merchant_id": self.settings.myntra_merchant_id},
                )
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise MarketplaceError("myntra_timeout", "Myntra token request timed out.", retryable=True) from exc
        except httpx.HTTPError as exc:
            raise MarketplaceError("myntra_token_request_failed", "Myntra rejected the partner token request.") from exc
        access_token = response.headers.get("access_token", "")
        refresh_token = response.headers.get("refresh_token", "")
        if not access_token or not refresh_token:
            raise MarketplaceError("myntra_tokens_missing", "Myntra did not return the documented token headers.")
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        return ConnectionResult(
            external_account_id=self.settings.myntra_merchant_id,
            encrypted_values={"access_token": access_token, "refresh_token": refresh_token},
            token_expires_at=expires_at.isoformat(),
            metadata={"authentication": "partner_token", "access_token_validity_days": 30},
        )
