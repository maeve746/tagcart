"""Secure, lazy Supabase client initialization."""

from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings


class SupabaseNotConfiguredError(RuntimeError):
    """Raised when required server-only Supabase settings are absent."""


@lru_cache
def get_supabase_client() -> Client:
    """Create one server-side Supabase client per process.

    The secret key is unwrapped only at client construction and is never logged,
    returned by an endpoint, or sent to the browser.
    """

    settings = get_settings()
    secret_key = (
        settings.supabase_secret_key.get_secret_value().strip()
        if settings.supabase_secret_key
        else ""
    )
    if not settings.supabase_url or not secret_key:
        raise SupabaseNotConfiguredError(
            "SUPABASE_URL and SUPABASE_SECRET_KEY must be configured on the server."
        )

    return create_client(
        settings.supabase_url,
        secret_key,
    )
