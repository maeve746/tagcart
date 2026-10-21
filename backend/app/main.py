"""FastAPI entry point for the TagCart backend."""

from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError

from app.core.config import get_settings
from app.core.supabase_client import (
    SupabaseNotConfiguredError,
    get_supabase_client,
)
from app.api.marketplaces import router as marketplaces_router
from app.core.security import TokenEncryptionNotConfiguredError
from app.integrations.base import MarketplaceError


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="TagCart backend API with Supabase persistence and isolated mock marketplace workflows.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(marketplaces_router)


@app.exception_handler(MarketplaceError)
async def marketplace_error_handler(
    request: Request, exc: MarketplaceError
) -> JSONResponse:
    del request
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "retryable": exc.retryable,
                **({"details": exc.details} if exc.details is not None else {}),
            },
            **(
                {"mode": "mock", "is_live": False}
                if settings.marketplace_mode == "mock"
                else {}
            ),
        },
    )


@app.exception_handler(TokenEncryptionNotConfiguredError)
async def token_encryption_error_handler(
    request: Request, exc: TokenEncryptionNotConfiguredError
) -> JSONResponse:
    del request, exc
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "token_encryption_not_configured",
                "message": "Marketplace credential encryption is not configured.",
                "retryable": False,
            }
        },
    )


@app.exception_handler(SupabaseNotConfiguredError)
async def supabase_configuration_error_handler(
    request: Request, exc: SupabaseNotConfiguredError
) -> JSONResponse:
    del request, exc
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "supabase_not_configured",
                "message": "Supabase server configuration is incomplete.",
                "retryable": False,
            }
        },
    )


@app.exception_handler(APIError)
async def supabase_api_error_handler(
    request: Request, exc: APIError
) -> JSONResponse:
    del request, exc
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "marketplace_storage_unavailable",
                "message": "Marketplace connection storage is unavailable or migrations are pending.",
                "retryable": True,
            }
        },
    )


@app.get("/health", tags=["Health"])
def health() -> Dict[str, str]:
    """Verify that the FastAPI process is running."""

    return {"status": "ok", "service": "tagcart-api"}


@app.get("/health/db", tags=["Health"])
def database_health() -> Any:
    """Verify Supabase connectivity with a minimal public.profiles query.

    The profiles table is intentionally not created here. A missing table is
    reported as a pending migration rather than a successful database check.
    """

    try:
        client = get_supabase_client()
        client.schema("public").table("profiles").select("id").limit(1).execute()
        return {
            "status": "ok",
            "database": "reachable",
            "table": "public.profiles",
        }
    except SupabaseNotConfiguredError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_configured",
                "database": "unchecked",
                "message": "Supabase server environment variables are not configured.",
            },
        )
    except APIError as exc:
        code = str(getattr(exc, "code", ""))
        message = str(getattr(exc, "message", "")).lower()
        if code in {"42P01", "PGRST205"} or "profiles" in message and (
            "not find" in message or "does not exist" in message
        ):
            return JSONResponse(
                status_code=503,
                content={
                    "status": "migrations_pending",
                    "database": "reachable",
                    "table": "public.profiles",
                    "message": "Supabase is reachable, but the profiles table is not available yet.",
                },
            )
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "database": "unreachable_or_rejected",
                "message": "Supabase rejected the database health query.",
            },
        )
    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "database": "unreachable",
                "message": "The database health check could not be completed.",
            },
        )
