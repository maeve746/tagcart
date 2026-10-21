import unittest
from urllib.parse import parse_qs, urlparse

import httpx
from pydantic import SecretStr

from app.core.config import Settings
from app.integrations.amazon import AmazonSPAPIAdapter, LWA_TOKEN_URL
from app.integrations.base import MarketplaceError


def amazon_settings() -> Settings:
    return Settings(
        _env_file=None,
        SUPABASE_URL=None,
        SUPABASE_SECRET_KEY=None,
        AMAZON_SPAPI_APP_ID="amzn1.sellerapps.app.test",
        AMAZON_LWA_CLIENT_ID="lwa-client-id",
        AMAZON_LWA_CLIENT_SECRET=SecretStr("lwa-secret"),
        AMAZON_OAUTH_REDIRECT_URI="https://tagcart.example/api/marketplaces/amazon/callback",
        AMAZON_SELLER_CENTRAL_URL="https://sellercentral.amazon.com",
        AMAZON_APP_IS_DRAFT=True,
    )


class AmazonAdapterTests(unittest.IsolatedAsyncioTestCase):
    def test_authorization_url_uses_official_consent_path_and_state(self) -> None:
        adapter = AmazonSPAPIAdapter(amazon_settings())
        url = urlparse(adapter.authorization_url("secure-state"))
        query = parse_qs(url.query)

        self.assertEqual(url.path, "/apps/authorize/consent")
        self.assertEqual(query, {
            "application_id": ["amzn1.sellerapps.app.test"],
            "state": ["secure-state"],
            "version": ["beta"],
        })

    async def test_code_exchange_uses_lwa_and_omits_access_token_from_storage(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(str(request.url), LWA_TOKEN_URL)
            self.assertTrue(request.headers["content-type"].startswith("application/x-www-form-urlencoded"))
            body = request.content.decode()
            self.assertIn("grant_type=authorization_code", body)
            self.assertIn("client_secret=lwa-secret", body)
            return httpx.Response(200, json={"access_token": "short-lived", "refresh_token": "long-lived", "token_type": "bearer", "expires_in": 3600})

        adapter = AmazonSPAPIAdapter(amazon_settings(), transport=httpx.MockTransport(handler))
        result = await adapter.connect(authorization_code="oauth-code", selling_partner_id="SELLER123")

        self.assertEqual(result.external_account_id, "SELLER123")
        self.assertEqual(result.encrypted_values, {"refresh_token": "long-lived"})
        self.assertNotIn("access_token", result.encrypted_values)

    async def test_code_exchange_returns_structured_error_on_rejection(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            del request
            return httpx.Response(400, json={"error": "invalid_grant"})

        adapter = AmazonSPAPIAdapter(amazon_settings(), transport=httpx.MockTransport(handler))
        with self.assertRaises(MarketplaceError) as raised:
            await adapter.connect(authorization_code="expired", selling_partner_id="SELLER123")
        self.assertEqual(raised.exception.code, "amazon_token_exchange_failed")
