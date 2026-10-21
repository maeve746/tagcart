"""Authenticated marketplace connection and mock submission routes."""

import json
import secrets
from typing import Any, Dict, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response

from app.core.auth import CurrentUser, get_current_user
from app.core.config import get_settings
from app.core.security import get_token_cipher
from app.integrations.amazon import AmazonSPAPIAdapter
from app.integrations.base import MarketplaceError
from app.integrations.mock import MOCK_NOTICE
from app.integrations.myntra import MyntraPartnerAdapter
from app.repositories.marketplace_connections import MarketplaceConnectionRepository
from app.repositories.listings import ListingRepository
from app.repositories.marketplace_submissions import MarketplaceSubmissionRepository
from app.services.marketplace_submissions import MarketplaceSubmissionService
from app.utils.xlsx import illustrative_xlsx


router = APIRouter(prefix="/api/marketplaces", tags=["Marketplaces"])
MarketplaceName = Literal["amazon", "myntra"]


def get_repository() -> MarketplaceConnectionRepository:
    return MarketplaceConnectionRepository()


def adapters() -> Dict[str, Any]:
    settings = get_settings()
    return {"amazon": AmazonSPAPIAdapter(settings), "myntra": MyntraPartnerAdapter(settings)}


def get_submission_service() -> MarketplaceSubmissionService:
    return MarketplaceSubmissionService(
        get_settings(), ListingRepository(), MarketplaceSubmissionRepository()
    )


def _require_production_connections() -> None:
    if get_settings().marketplace_mode == "mock":
        raise MarketplaceError(
            "production_connections_disabled_in_mock_mode",
            "Real marketplace connection flows are disabled while MARKETPLACE_MODE=mock.",
            status_code=409,
        )


@router.get("/status")
def marketplace_status(
    user: CurrentUser = Depends(get_current_user),
) -> Dict[str, Any]:
    settings = get_settings()
    if settings.marketplace_mode == "mock":
        del user
        return {
            "mode": "mock",
            "is_live": False,
            "simulation_notice": MOCK_NOTICE,
            "connections": [
                {"marketplace": name, "status": "mock_ready", "configured": True, "missing_configuration": []}
                for name in ("amazon", "myntra")
            ],
        }
    repository = get_repository()
    existing = {item["marketplace"]: item for item in repository.list_statuses(user.id)}
    encryption_configured = bool(
        settings.marketplace_token_encryption_key
        and settings.marketplace_token_encryption_key.get_secret_value().strip()
    )
    result = []
    for name, adapter in adapters().items():
        record = existing.get(name)
        result.append({
            "marketplace": name,
            "status": record.get("status", "not_connected") if record else "not_connected",
            "configured": adapter.configuration_status()["configured"] and encryption_configured,
            "missing_configuration": adapter.configuration_status()["missing"] + ([] if encryption_configured else ["MARKETPLACE_TOKEN_ENCRYPTION_KEY"]),
            "external_account_id": record.get("external_account_id") if record else None,
            "connected_at": record.get("connected_at") if record else None,
            "token_expires_at": record.get("token_expires_at") if record else None,
            "last_error_code": record.get("last_error_code") if record else None,
        })
    return {"mode": "production", "connections": result}


@router.post("/amazon/connect")
def connect_amazon(
    user: CurrentUser = Depends(get_current_user),
) -> Dict[str, str]:
    _require_production_connections()
    repository = get_repository()
    get_token_cipher()  # Fail before seller authorization if secure storage is unavailable.
    state = secrets.token_urlsafe(32)
    adapter = AmazonSPAPIAdapter(get_settings())
    authorization_url = adapter.authorization_url(state)
    repository.create_oauth_state(user.id, "amazon", state)
    return {"authorization_url": authorization_url}


@router.get("/amazon/callback")
async def amazon_callback(
    response: Response,
    state: str = Query(..., min_length=32, max_length=256),
    selling_partner_id: str = Query(..., min_length=1, max_length=128),
    spapi_oauth_code: str = Query(..., min_length=1, max_length=4096),
) -> Dict[str, Any]:
    _require_production_connections()
    repository = get_repository()
    # Amazon redirects browsers without the application's bearer header. The
    # single-use, user-bound state is the callback's authentication mechanism.
    user_id = repository.consume_oauth_state("amazon", state)
    result = await AmazonSPAPIAdapter(get_settings()).connect(
        authorization_code=spapi_oauth_code,
        selling_partner_id=selling_partner_id,
    )
    saved = repository.save_connection(user_id, "amazon", result)
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return {"marketplace": "amazon", "status": saved["status"], "external_account_id": saved["external_account_id"], "connected_at": saved["connected_at"]}


@router.get("/myntra/configuration")
def myntra_configuration(user: CurrentUser = Depends(get_current_user)) -> Dict[str, Any]:
    del user
    if get_settings().marketplace_mode == "mock":
        return {"mode": "mock", "is_live": False, "marketplace": "myntra", "configured": True, "missing": [], "simulation_notice": MOCK_NOTICE}
    status = MyntraPartnerAdapter(get_settings()).configuration_status()
    return {"mode": "production", "marketplace": "myntra", **status}


@router.post("/myntra/connect")
async def connect_myntra(
    user: CurrentUser = Depends(get_current_user),
) -> Dict[str, Any]:
    _require_production_connections()
    repository = get_repository()
    get_token_cipher()  # Never request partner tokens unless they can be encrypted.
    current = repository.get_connection(user.id, "myntra")
    if current and current.get("status") == "connected":
        raise MarketplaceError("myntra_already_connected", "Myntra is already connected. Token generation is a one-time partner operation.", status_code=409)
    result = await MyntraPartnerAdapter(get_settings()).connect()
    saved = repository.save_connection(user.id, "myntra", result)
    return {"marketplace": "myntra", "status": saved["status"], "external_account_id": saved["external_account_id"], "connected_at": saved["connected_at"], "token_expires_at": saved["token_expires_at"]}


@router.post("/{marketplace}/listings/{listing_id}/validate")
def validate_listing(
    marketplace: MarketplaceName,
    listing_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    service: MarketplaceSubmissionService = Depends(get_submission_service),
) -> Dict[str, Any]:
    return service.validate(user.id, marketplace, str(listing_id))


@router.post("/{marketplace}/listings/{listing_id}/submit", status_code=201)
def submit_listing(
    marketplace: MarketplaceName,
    listing_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    service: MarketplaceSubmissionService = Depends(get_submission_service),
) -> Dict[str, Any]:
    return service.submit(user.id, marketplace, str(listing_id))


@router.get("/submissions")
def list_submissions(
    user: CurrentUser = Depends(get_current_user),
    service: MarketplaceSubmissionService = Depends(get_submission_service),
) -> Dict[str, Any]:
    return service.list(user.id)


@router.get("/submissions/{submission_id}")
def get_submission(
    submission_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    service: MarketplaceSubmissionService = Depends(get_submission_service),
) -> Dict[str, Any]:
    return service.get(user.id, str(submission_id))


@router.post("/submissions/{submission_id}/advance")
def advance_submission(
    submission_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    service: MarketplaceSubmissionService = Depends(get_submission_service),
) -> Dict[str, Any]:
    return service.advance(user.id, str(submission_id))


@router.get("/amazon/listings/{listing_id}/sample.json")
def download_amazon_sample(
    listing_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    service: MarketplaceSubmissionService = Depends(get_submission_service),
) -> Response:
    payload = {
        "mode": "mock",
        "is_live": False,
        "simulation_notice": MOCK_NOTICE,
        "sample": service.sample(user.id, "amazon", str(listing_id)),
    }
    return Response(
        json.dumps(payload, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="tagcart-amazon-{listing_id}-sample.json"'},
    )


@router.get("/myntra/listings/{listing_id}/sample.xlsx")
def download_myntra_sample(
    listing_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    service: MarketplaceSubmissionService = Depends(get_submission_service),
) -> Response:
    payload = service.sample(user.id, "myntra", str(listing_id))
    payload = {"mode": "mock", "is_live": False, "simulation_notice": MOCK_NOTICE, **payload}
    return Response(
        illustrative_xlsx(payload),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="tagcart-myntra-{listing_id}-sample.xlsx"'},
    )
