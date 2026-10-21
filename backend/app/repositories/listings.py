"""Read-only access to persisted TagCart listings used by marketplace flows."""

from typing import Any, Dict, Optional

from postgrest.exceptions import APIError

from app.core.supabase_client import get_supabase_client
from app.integrations.base import MarketplaceError


class ListingRepository:
    """Read existing listings; this module never creates or approves them."""

    def __init__(self) -> None:
        self.client = get_supabase_client()

    def get_owned(self, user_id: str, listing_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = (
                self.client.schema("public")
                .table("listings")
                .select("*")
                .eq("id", listing_id)
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )
        except APIError as exc:
            code = str(getattr(exc, "code", ""))
            message = str(getattr(exc, "message", "")).lower()
            if code in {"42P01", "PGRST205"} or "listings" in message and "not find" in message:
                raise MarketplaceError(
                    "tagcart_listings_table_missing",
                    "The required public.listings table is unavailable. Apply the TagCart listings migration before using marketplace submissions.",
                    status_code=503,
                ) from exc
            raise
        rows = list(response.data or [])
        return rows[0] if rows else None
