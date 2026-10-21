"""Supabase persistence for marketplace mock submissions and state history."""

from typing import Any, Dict, List, Optional

from postgrest.exceptions import APIError

from app.core.supabase_client import get_supabase_client
from app.integrations.base import MarketplaceError


PUBLIC_FIELDS = (
    "id,user_id,listing_id,marketplace,mode,status,final_mock_outcome,"
    "mock_reference,request_payload,validation_snapshot,poll_count,"
    "created_at,updated_at,completed_at"
)


def _storage_error(exc: APIError) -> MarketplaceError:
    code = str(getattr(exc, "code", ""))
    message = str(getattr(exc, "message", "")).lower()
    missing = code in {"42P01", "PGRST202", "PGRST205"} or (
        "marketplace_submission" in message
        and any(term in message for term in ("not find", "does not exist", "schema cache"))
    )
    if missing:
        return MarketplaceError(
            "marketplace_submissions_migration_pending",
            "Marketplace submission storage is unavailable. Apply the marketplace submissions migration.",
            status_code=503,
            retryable=False,
        )
    return MarketplaceError(
        "marketplace_submission_storage_error",
        "Supabase rejected the marketplace submission operation.",
        status_code=503,
        retryable=True,
    )


class MarketplaceSubmissionRepository:
    def __init__(self) -> None:
        self.client = get_supabase_client()

    def create_mock(
        self,
        *,
        user_id: str,
        listing_id: str,
        marketplace: str,
        payload: Dict[str, Any],
        validation: Dict[str, Any],
        final_outcome: str,
        reference: str,
    ) -> Dict[str, Any]:
        try:
            response = self.client.schema("public").rpc(
                "create_mock_marketplace_submission",
                {
                    "p_user_id": user_id,
                    "p_listing_id": listing_id,
                    "p_marketplace": marketplace,
                    "p_payload": payload,
                    "p_validation": validation,
                    "p_final_outcome": final_outcome,
                    "p_reference": reference,
                },
            ).execute()
        except APIError as exc:
            raise _storage_error(exc) from exc
        rows = list(response.data or [])
        if not rows:
            raise MarketplaceError(
                "submission_persistence_failed",
                "The mock submission could not be persisted.",
                status_code=503,
            )
        return rows[0]

    def get_owned(self, user_id: str, submission_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = (
                self.client.schema("public")
                .table("marketplace_submissions")
                .select(PUBLIC_FIELDS)
                .eq("id", submission_id)
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )
        except APIError as exc:
            raise _storage_error(exc) from exc
        rows = list(response.data or [])
        return rows[0] if rows else None

    def list_owned(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            response = (
                self.client.schema("public")
                .table("marketplace_submissions")
                .select(PUBLIC_FIELDS)
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
        except APIError as exc:
            raise _storage_error(exc) from exc
        return list(response.data or [])

    def advance_mock(self, user_id: str, submission_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.schema("public").rpc(
                "advance_mock_marketplace_submission",
                {"p_submission_id": submission_id, "p_user_id": user_id},
            ).execute()
        except APIError as exc:
            raise _storage_error(exc) from exc
        rows = list(response.data or [])
        return rows[0] if rows else None

    def history_owned(self, user_id: str, submission_id: str) -> List[Dict[str, Any]]:
        try:
            response = (
                self.client.schema("public")
                .table("marketplace_submission_history")
                .select("id,submission_id,from_status,to_status,reason,created_at")
                .eq("submission_id", submission_id)
                .eq("user_id", user_id)
                .order("created_at")
                .execute()
            )
        except APIError as exc:
            raise _storage_error(exc) from exc
        return list(response.data or [])
