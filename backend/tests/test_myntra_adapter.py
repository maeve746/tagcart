import json
import unittest

import httpx
from pydantic import SecretStr

from app.core.config import Settings
from app.integrations.base import MarketplaceError
from app.integrations.myntra import MyntraPartnerAdapter


def myntra_settings() -> Settings:
    return Settings(
        _env_file=None,
        SUPABASE_URL=None,
        SUPABASE_SECRET_KEY=None,
        MYNTRA_API_BASE_URL="https://partner-api.example",
        MYNTRA_MERCHANT_ID="merchant-123",
        MYNTRA_SECRET_KEY=SecretStr("partner-secret"),
    )


class MyntraAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_generate_token_uses_documented_headers_and_body(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(str(request.url), "https://partner-api.example/authorization/generate_token")
            self.assertEqual(request.headers["secret_key"], "partner-secret")
            self.assertEqual(json.loads(request.content), {"merchant_id": "merchant-123"})
            return httpx.Response(200, headers={"access_token": "access-value", "refresh_token": "refresh-value"})

        adapter = MyntraPartnerAdapter(myntra_settings(), transport=httpx.MockTransport(handler))
        result = await adapter.connect()

        self.assertEqual(result.external_account_id, "merchant-123")
        self.assertEqual(result.encrypted_values, {"access_token": "access-value", "refresh_token": "refresh-value"})
        self.assertIsNotNone(result.token_expires_at)

    async def test_missing_token_headers_is_not_reported_as_connected(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            del request
            return httpx.Response(200)

        adapter = MyntraPartnerAdapter(myntra_settings(), transport=httpx.MockTransport(handler))
        with self.assertRaises(MarketplaceError) as raised:
            await adapter.connect()
        self.assertEqual(raised.exception.code, "myntra_tokens_missing")
