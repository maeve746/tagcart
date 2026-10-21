"""Amazon SP-API Login with Amazon seller authorization adapter."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlencode, urlparse

import httpx

from app.core.config import Settings
from app.integrations.base import ConnectionResult, MarketplaceAdapter, MarketplaceError


LWA_TOKEN_URL = "https://api.amazon.com/auth/o2/token"


class AmazonSPAPIAdapter(MarketplaceAdapter):
    marketplace = "amazon"

    def __init__(self, settings: Settings, transport: Optional[httpx.AsyncBaseTransport] = None):
        self.settings = settings
        self._transport = transport

    def _secret(self) -> str:
        return (
            self.settings.amazon_lwa_client_secret.get_secret_value().strip()
            if self.settings.amazon_lwa_client_secret
            else ""
        )

    def configuration_status(self) -> Dict[str, Any]:
        missing = []
        values = {
            "AMAZON_SPAPI_APP_ID": self.settings.amazon_spapi_app_id,
            "AMAZON_LWA_CLIENT_ID": self.settings.amazon_lwa_client_id,
            "AMAZON_LWA_CLIENT_SECRET": self._secret(),
            "AMAZON_OAUTH_REDIRECT_URI": self.settings.amazon_oauth_redirect_uri,
            "AMAZON_SELLER_CENTRAL_URL": self.settings.amazon_seller_central_url,
        }
        missing.extend(name for name, value in values.items() if not value)
        return {"configured": not missing, "missing": missing, "draft": self.settings.amazon_app_is_draft}

    def authorization_url(self, state: str) -> str:
        status = self.configuration_status()
        if not status["configured"]:
            raise MarketplaceError("amazon_not_configured", "Amazon SP-API configuration is incomplete.", status_code=503)
        base = self.settings.amazon_seller_central_url.rstrip("/")
        parsed = urlparse(base)
        if parsed.scheme != "https" or not parsed.netloc:
            raise MarketplaceError("amazon_invalid_seller_central_url", "Amazon Seller Central URL must be an HTTPS origin.", status_code=503)
        params = {"application_id": self.settings.amazon_spapi_app_id, "state": state}
        if self.settings.amazon_app_is_draft:
            params["version"] = "beta"
        return f"{base}/apps/authorize/consent?{urlencode(params)}"

    async def connect(self, **kwargs: Any) -> ConnectionResult:
        code = str(kwargs.get("authorization_code", ""))
        seller_id = str(kwargs.get("selling_partner_id", ""))
        if not code or not seller_id:
            raise MarketplaceError("amazon_callback_invalid", "Amazon callback parameters are incomplete.", status_code=400)
        if not self.configuration_status()["configured"]:
            raise MarketplaceError("amazon_not_configured", "Amazon SP-API configuration is incomplete.", status_code=503)
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.settings.amazon_oauth_redirect_uri,
            "client_id": self.settings.amazon_lwa_client_id,
            "client_secret": self._secret(),
        }
        try:
            async with httpx.AsyncClient(
                timeout=self.settings.marketplace_http_timeout_seconds,
                transport=self._transport,
            ) as client:
                response = await client.post(LWA_TOKEN_URL, data=data)
                response.raise_for_status()
                payload = response.json()
        except httpx.TimeoutException as exc:
            raise MarketplaceError("amazon_timeout", "Amazon token exchange timed out.", retryable=True) from exc
        except (httpx.HTTPError, ValueError) as exc:
            raise MarketplaceError("amazon_token_exchange_failed", "Amazon rejected the authorization code exchange.") from exc
        refresh_token = str(payload.get("refresh_token", ""))
        if not refresh_token:
            raise MarketplaceError("amazon_refresh_token_missing", "Amazon did not return a refresh token.")
        expires_in = int(payload.get("expires_in", 3600))
        return ConnectionResult(
            external_account_id=seller_id,
            encrypted_values={"refresh_token": refresh_token},
            token_expires_at=None,
            metadata={"access_token_expires_at": (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat(), "token_type": payload.get("token_type", "bearer")},
        )
