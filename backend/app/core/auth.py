"""Supabase bearer-token authentication for protected API routes."""

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase_client import SupabaseNotConfiguredError, get_supabase_client


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    """Validate a Supabase access token without exposing it downstream."""

    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "authentication_required", "message": "Bearer token required."},
        )
    try:
        response = get_supabase_client().auth.get_user(credentials.credentials)
        user = getattr(response, "user", None)
        user_id = str(getattr(user, "id", ""))
        if not user_id:
            raise ValueError("Supabase returned no authenticated user.")
        return CurrentUser(id=user_id)
    except HTTPException:
        raise
    except SupabaseNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "supabase_not_configured", "message": "Supabase authentication is not configured."},
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_access_token", "message": "Access token is invalid or expired."},
        ) from exc
