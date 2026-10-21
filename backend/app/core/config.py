"""Application configuration loaded only from environment variables or backend/.env."""

from functools import lru_cache
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Server settings.

    Supabase values are optional at import time so the API can expose its basic
    health endpoint before local configuration is complete. Database operations
    reject missing configuration in the client factory.
    """

    app_name: str = "TagCart API"
    environment: str = "development"
    supabase_url: Optional[str] = Field(default=None, validation_alias="SUPABASE_URL")
    supabase_secret_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias="SUPABASE_SECRET_KEY",
    )
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        validation_alias="CORS_ORIGINS",
    )
    marketplace_http_timeout_seconds: float = Field(
        default=10.0,
        validation_alias="MARKETPLACE_HTTP_TIMEOUT_SECONDS",
        ge=1.0,
        le=30.0,
    )
    marketplace_mode: Literal["mock", "production"] = Field(
        default="mock",
        validation_alias="MARKETPLACE_MODE",
    )
    marketplace_token_encryption_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias="MARKETPLACE_TOKEN_ENCRYPTION_KEY",
    )

    # Amazon SP-API / Login with Amazon settings. The Seller Central URL is
    # deliberately required because Amazon documents region-specific URLs.
    amazon_spapi_app_id: Optional[str] = Field(
        default=None,
        validation_alias="AMAZON_SPAPI_APP_ID",
    )
    amazon_lwa_client_id: Optional[str] = Field(
        default=None,
        validation_alias="AMAZON_LWA_CLIENT_ID",
    )
    amazon_lwa_client_secret: Optional[SecretStr] = Field(
        default=None,
        validation_alias="AMAZON_LWA_CLIENT_SECRET",
    )
    amazon_oauth_redirect_uri: Optional[str] = Field(
        default=None,
        validation_alias="AMAZON_OAUTH_REDIRECT_URI",
    )
    amazon_seller_central_url: Optional[str] = Field(
        default=None,
        validation_alias="AMAZON_SELLER_CENTRAL_URL",
    )
    amazon_app_is_draft: bool = Field(
        default=True,
        validation_alias="AMAZON_APP_IS_DRAFT",
    )

    # Myntra supplies these values during partner onboarding. No public base
    # URL or seller credential is assumed by the application.
    myntra_api_base_url: Optional[str] = Field(
        default=None,
        validation_alias="MYNTRA_API_BASE_URL",
    )
    myntra_merchant_id: Optional[str] = Field(
        default=None,
        validation_alias="MYNTRA_MERCHANT_ID",
    )
    myntra_secret_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias="MYNTRA_SECRET_KEY",
    )

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached, process-local settings object."""

    return Settings()
