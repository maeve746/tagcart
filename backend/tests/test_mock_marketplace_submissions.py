"""Pytest coverage for the offline marketplace submission workflow."""

from copy import deepcopy
from typing import Any, Dict, List, Optional
import unittest
from unittest.mock import patch
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.api.marketplaces import get_submission_service
from app.core.auth import CurrentUser, get_current_user
from app.core.config import Settings
from app.integrations.base import MarketplaceError
from app.integrations.mock import AmazonMockAdapter, MyntraMockAdapter
from app.main import app
from app.services.marketplace_submissions import MarketplaceSubmissionService


USER_ID = "11111111-1111-4111-8111-111111111111"
OTHER_USER_ID = "22222222-2222-4222-8222-222222222222"
LISTING_ID = "33333333-3333-4333-8333-333333333333"


def valid_listing(**overrides: Any) -> Dict[str, Any]:
    listing = {
        "id": LISTING_ID,
        "user_id": USER_ID,
        "status": "Approved",
        "sku": "TC-SHIRT-001",
        "title": "Illustrative cotton shirt",
        "brand": "TagCart Demo",
        "category": "Shirts",
        "article_type": "Shirts",
        "description": "An illustrative listing used only in offline tests.",
        "bullets": ["Mock data", "Not a live offer"],
        "price": 999,
        "currency": "INR",
        "quantity": 5,
        "color": "Blue",
        "sizes": ["M", "L"],
    }
    listing.update(overrides)
    return listing


class MemoryListings:
    def __init__(self, records: List[Dict[str, Any]]) -> None:
        self.records = records

    def get_owned(self, user_id: str, listing_id: str) -> Optional[Dict[str, Any]]:
        return next(
            (deepcopy(item) for item in self.records if item["id"] == listing_id and item["user_id"] == user_id),
            None,
        )


class MemorySubmissions:
    def __init__(self) -> None:
        self.records: Dict[str, Dict[str, Any]] = {}
        self.histories: Dict[str, List[Dict[str, Any]]] = {}

    def create_mock(self, **values: Any) -> Dict[str, Any]:
        submission_id = str(uuid4())
        record = {
            "id": submission_id,
            "user_id": values["user_id"],
            "listing_id": values["listing_id"],
            "marketplace": values["marketplace"],
            "mode": "mock",
            "status": "accepted",
            "final_mock_outcome": values["final_outcome"],
            "mock_reference": values["reference"],
            "request_payload": values["payload"],
            "validation_snapshot": values["validation"],
            "poll_count": 0,
            "created_at": "2026-10-21T00:00:00Z",
            "updated_at": "2026-10-21T00:00:00Z",
            "completed_at": None,
        }
        self.records[submission_id] = record
        self.histories[submission_id] = [{"from_status": None, "to_status": "accepted", "reason": "mock"}]
        return deepcopy(record)

    def get_owned(self, user_id: str, submission_id: str) -> Optional[Dict[str, Any]]:
        record = self.records.get(submission_id)
        return deepcopy(record) if record and record["user_id"] == user_id else None

    def list_owned(self, user_id: str) -> List[Dict[str, Any]]:
        return [deepcopy(item) for item in self.records.values() if item["user_id"] == user_id]

    def advance_mock(self, user_id: str, submission_id: str) -> Optional[Dict[str, Any]]:
        record = self.records.get(submission_id)
        if not record or record["user_id"] != user_id:
            return None
        previous = record["status"]
        next_status = "processing" if previous == "accepted" else record["final_mock_outcome"] if previous == "processing" else previous
        if next_status != previous:
            record["status"] = next_status
            record["poll_count"] += 1
            self.histories[submission_id].append({"from_status": previous, "to_status": next_status, "reason": "mock"})
        return deepcopy(record)

    def history_owned(self, user_id: str, submission_id: str) -> List[Dict[str, Any]]:
        record = self.records.get(submission_id)
        return deepcopy(self.histories.get(submission_id, [])) if record and record["user_id"] == user_id else []


def make_service(listings: List[Dict[str, Any]]) -> MarketplaceSubmissionService:
    return MarketplaceSubmissionService(
        Settings(_env_file=None, MARKETPLACE_MODE="mock"),
        MemoryListings(listings),  # type: ignore[arg-type]
        MemorySubmissions(),  # type: ignore[arg-type]
    )


def test_marketplace_routes_require_authentication() -> None:
    app.dependency_overrides[get_submission_service] = lambda: make_service([valid_listing()])
    try:
        response = TestClient(app).post(f"/api/marketplaces/amazon/listings/{LISTING_ID}/validate")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 401


def test_validation_returns_field_specific_errors() -> None:
    service = make_service([valid_listing(brand="", currency=None)])
    result = service.validate(USER_ID, "amazon", LISTING_ID)
    assert result["mode"] == "mock"
    assert result["is_live"] is False
    assert result["valid"] is False
    assert {item["field"] for item in result["errors"]} == {"brand", "currency"}
    assert result["illustrative_payload"]["compliance_claim"] is False


def test_submission_requires_original_tagcart_approval() -> None:
    service = make_service([valid_listing(status="Review")])
    try:
        service.submit(USER_ID, "amazon", LISTING_ID)
        raise AssertionError("Expected an approval error")
    except MarketplaceError as exc:
        assert exc.code == "listing_not_approved"
        assert exc.status_code == 409


def test_listing_and_submission_ownership_is_enforced() -> None:
    service = make_service([valid_listing()])
    try:
        service.validate(OTHER_USER_ID, "amazon", LISTING_ID)
        raise AssertionError("Expected ownership to hide the listing")
    except MarketplaceError as exc:
        assert exc.code == "listing_not_found"

    created = service.submit(USER_ID, "amazon", LISTING_ID)
    submission_id = created["submission"]["id"]
    try:
        service.get(OTHER_USER_ID, submission_id)
        raise AssertionError("Expected ownership to hide the submission")
    except MarketplaceError as exc:
        assert exc.code == "submission_not_found"


def test_deterministic_submission_state_changes_are_persisted() -> None:
    service = make_service([valid_listing()])
    created = service.submit(USER_ID, "amazon", LISTING_ID)
    submission_id = created["submission"]["id"]
    assert created["submission"]["status"] == "accepted"

    processing = service.advance(USER_ID, submission_id)
    terminal = service.advance(USER_ID, submission_id)
    repeated = service.advance(USER_ID, submission_id)

    assert processing["submission"]["status"] == "processing"
    assert terminal["submission"]["status"] in {"completed", "rejected"}
    assert repeated["submission"]["status"] == terminal["submission"]["status"]
    assert len(terminal["submission"]["history"]) == 3
    assert terminal["is_live"] is False


def test_terminal_outcomes_are_deterministic_and_cover_both_results() -> None:
    for adapter in (AmazonMockAdapter(), MyntraMockAdapter()):
        first = adapter.final_outcome(LISTING_ID)
        assert adapter.final_outcome(LISTING_ID) == first
        outcomes = {adapter.final_outcome(str(UUID(int=index))) for index in range(100)}
        assert outcomes == {"completed", "rejected"}


def test_list_returns_only_current_users_submissions() -> None:
    service = make_service([valid_listing()])
    service.submit(USER_ID, "amazon", LISTING_ID)
    assert len(service.list(USER_ID)["submissions"]) == 1
    assert service.list(OTHER_USER_ID)["submissions"] == []


def test_mock_mode_never_calls_production_connection_adapter() -> None:
    called = False

    async def forbidden_connect(*args: Any, **kwargs: Any) -> None:
        nonlocal called
        called = True
        raise AssertionError("Production adapter was called in mock mode")

    with patch("app.integrations.amazon.AmazonSPAPIAdapter.connect", forbidden_connect), patch(
        "app.integrations.myntra.MyntraPartnerAdapter.connect", forbidden_connect
    ):
        app.dependency_overrides[get_current_user] = lambda: CurrentUser(id=USER_ID)
        try:
            client = TestClient(app)
            amazon = client.post("/api/marketplaces/amazon/connect")
            myntra = client.post("/api/marketplaces/myntra/connect")
        finally:
            app.dependency_overrides.clear()
    assert amazon.status_code == 409
    assert myntra.status_code == 409
    assert amazon.json()["mode"] == "mock"
    assert myntra.json()["mode"] == "mock"
    assert called is False


def test_download_routes_return_labeled_json_and_valid_xlsx_container() -> None:
    service = make_service([valid_listing()])
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id=USER_ID)
    app.dependency_overrides[get_submission_service] = lambda: service
    client = TestClient(app)
    try:
        amazon = client.get(f"/api/marketplaces/amazon/listings/{LISTING_ID}/sample.json")
        myntra = client.get(f"/api/marketplaces/myntra/listings/{LISTING_ID}/sample.xlsx")
    finally:
        app.dependency_overrides.clear()

    assert amazon.status_code == 200
    assert amazon.json()["mode"] == "mock"
    assert amazon.json()["is_live"] is False
    assert "attachment" in amazon.headers["content-disposition"]
    assert myntra.status_code == 200
    assert myntra.content.startswith(b"PK")
    assert "attachment" in myntra.headers["content-disposition"]


class MockMarketplaceSubmissionTests(unittest.TestCase):
    """Also runs under unittest when pytest cannot be installed offline."""

    def test_authentication(self) -> None:
        test_marketplace_routes_require_authentication()

    def test_field_validation(self) -> None:
        test_validation_returns_field_specific_errors()

    def test_approval(self) -> None:
        test_submission_requires_original_tagcart_approval()

    def test_ownership(self) -> None:
        test_listing_and_submission_ownership_is_enforced()

    def test_state_changes(self) -> None:
        test_deterministic_submission_state_changes_are_persisted()

    def test_deterministic_outcomes(self) -> None:
        test_terminal_outcomes_are_deterministic_and_cover_both_results()

    def test_user_list(self) -> None:
        test_list_returns_only_current_users_submissions()

    def test_external_api_isolation(self) -> None:
        test_mock_mode_never_calls_production_connection_adapter()

    def test_downloads(self) -> None:
        test_download_routes_return_labeled_json_and_valid_xlsx_container()
