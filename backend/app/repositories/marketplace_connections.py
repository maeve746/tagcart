"""Persistence for marketplace connections and short-lived OAuth state."""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.core.security import get_token_cipher
from app.core.supabase_client import get_supabase_client
from app.integrations.base import ConnectionResult, MarketplaceError


PUBLIC_CONNECTION_FIELDS = (
    "marketplace,status,external_account_id,token_expires_at,connected_at,"
    "last_error_code,metadata,updated_at"
)


class MarketplaceConnectionRepository:
    def __init__(self):
        self.client = get_supabase_client()

    def list_statuses(self, user_id: str) -> List[Dict[str, Any]]:
        response = (
            self.client.schema("public")
            .table("marketplace_connections")
            .select(PUBLIC_CONNECTION_FIELDS)
            .eq("user_id", user_id)
            .execute()
        )
        return list(response.data or [])

    def get_connection(self, user_id: str, marketplace: str) -> Optional[Dict[str, Any]]:
        response = (
            self.client.schema("public")
            .table("marketplace_connections")
            .select(PUBLIC_CONNECTION_FIELDS)
            .eq("user_id", user_id)
            .eq("marketplace", marketplace)
            .limit(1)
            .execute()
        )
        data = list(response.data or [])
        return data[0] if data else None

    def save_connection(self, user_id: str, marketplace: str, result: ConnectionResult) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "user_id": user_id,
            "marketplace": marketplace,
            "external_account_id": result.external_account_id,
            "status": "connected",
            "encrypted_credentials": get_token_cipher().encrypt(result.encrypted_values),
            "token_expires_at": result.token_expires_at,
            "metadata": result.metadata,
            "last_error_code": None,
            "connected_at": now,
            "updated_at": now,
        }
        response = (
            self.client.schema("public")
            .table("marketplace_connections")
            .upsert(record, on_conflict="user_id,marketplace")
            .execute()
        )
        saved = list(response.data or [])
        if not saved:
            raise MarketplaceError("connection_persistence_failed", "Marketplace connection could not be persisted.")
        return {key: value for key, value in saved[0].items() if key != "encrypted_credentials"}

    def create_oauth_state(self, user_id: str, marketplace: str, state: str) -> None:
        state_hash = hashlib.sha256(state.encode("utf-8")).hexdigest()
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
        self.client.schema("public").table("marketplace_oauth_states").insert(
            {"user_id": user_id, "marketplace": marketplace, "state_hash": state_hash, "expires_at": expires_at}
        ).execute()

    def consume_oauth_state(self, marketplace: str, state: str) -> str:
        state_hash = hashlib.sha256(state.encode("utf-8")).hexdigest()
        response = self.client.schema("public").rpc(
            "consume_marketplace_oauth_state",
            {"p_state_hash": state_hash, "p_marketplace": marketplace},
        ).execute()
        rows = list(response.data or [])
        if not rows or not rows[0].get("user_id"):
            raise MarketplaceError("oauth_state_invalid", "OAuth state is invalid, expired, or already used.", status_code=400)
        return str(rows[0]["user_id"])
