"""Marketplace listing validation and deterministic mock submission workflow."""

import hashlib
from dataclasses import asdict
from typing import Any, Dict, List

from app.core.config import Settings
from app.integrations.base import MarketplaceError, MarketplaceSubmissionAdapter
from app.integrations.mock import MOCK_NOTICE, get_mock_adapter
from app.repositories.listings import ListingRepository
from app.repositories.marketplace_submissions import MarketplaceSubmissionRepository


class MarketplaceSubmissionService:
    def __init__(
        self,
        settings: Settings,
        listings: ListingRepository,
        submissions: MarketplaceSubmissionRepository,
    ) -> None:
        self.settings = settings
        self.listings = listings
        self.submissions = submissions

    def _adapter(self, marketplace: str) -> MarketplaceSubmissionAdapter:
        if self.settings.marketplace_mode != "mock":
            raise MarketplaceError(
                "live_submission_not_implemented",
                "Production marketplace listing submission is not implemented or enabled.",
                status_code=501,
            )
        return get_mock_adapter(marketplace)

    def _listing(self, user_id: str, listing_id: str) -> Dict[str, Any]:
        listing = self.listings.get_owned(user_id, listing_id)
        if not listing:
            raise MarketplaceError(
                "listing_not_found",
                "Listing was not found for the authenticated user.",
                status_code=404,
            )
        return listing

    @staticmethod
    def _envelope(data: Dict[str, Any]) -> Dict[str, Any]:
        return {"mode": "mock", "is_live": False, "simulation_notice": MOCK_NOTICE, **data}

    def validate(self, user_id: str, marketplace: str, listing_id: str) -> Dict[str, Any]:
        listing = self._listing(user_id, listing_id)
        result = self._adapter(marketplace).validate(listing)
        return self._envelope({
            "marketplace": marketplace,
            "listing_id": listing_id,
            "valid": result.valid,
            "errors": [asdict(item) for item in result.errors],
            "illustrative_payload": result.illustrative_payload,
        })

    def submit(self, user_id: str, marketplace: str, listing_id: str) -> Dict[str, Any]:
        listing = self._listing(user_id, listing_id)
        if str(listing.get("status", "")).strip().lower() != "approved":
            raise MarketplaceError(
                "listing_not_approved",
                "The original TagCart listing must be approved before mock submission.",
                status_code=409,
                details={"field": "status", "required_value": "approved"},
            )
        adapter = self._adapter(marketplace)
        result = adapter.validate(listing)
        if not result.valid:
            raise MarketplaceError(
                "listing_validation_failed",
                "The listing has marketplace validation errors.",
                status_code=422,
                details={"fields": [asdict(item) for item in result.errors]},
            )
        outcome = adapter.final_outcome(listing_id)
        reference = "MOCK-" + hashlib.sha256(
            f"{user_id}:{marketplace}:{listing_id}".encode("utf-8")
        ).hexdigest()[:16].upper()
        saved = self.submissions.create_mock(
            user_id=user_id,
            listing_id=listing_id,
            marketplace=marketplace,
            payload=result.illustrative_payload,
            validation={"valid": True, "errors": []},
            final_outcome=outcome,
            reference=reference,
        )
        return self._submission(saved, include_history=True, user_id=user_id)

    def get(self, user_id: str, submission_id: str) -> Dict[str, Any]:
        submission = self.submissions.get_owned(user_id, submission_id)
        if not submission:
            raise MarketplaceError("submission_not_found", "Submission was not found.", status_code=404)
        return self._submission(submission, include_history=True, user_id=user_id)

    def list(self, user_id: str) -> Dict[str, Any]:
        records = [self._submission(item) for item in self.submissions.list_owned(user_id)]
        return self._envelope({"submissions": records})

    def advance(self, user_id: str, submission_id: str) -> Dict[str, Any]:
        submission = self.submissions.advance_mock(user_id, submission_id)
        if not submission:
            raise MarketplaceError("submission_not_found", "Submission was not found.", status_code=404)
        return self._submission(submission, include_history=True, user_id=user_id)

    def _submission(
        self,
        record: Dict[str, Any],
        *,
        include_history: bool = False,
        user_id: str = "",
    ) -> Dict[str, Any]:
        public = {key: value for key, value in record.items() if key not in {"user_id", "final_mock_outcome"}}
        if include_history:
            public["history"] = self.submissions.history_owned(user_id, str(record["id"]))
        return self._envelope({"submission": public})

    def sample(self, user_id: str, marketplace: str, listing_id: str) -> Dict[str, Any]:
        result = self.validate(user_id, marketplace, listing_id)
        if not result["valid"]:
            raise MarketplaceError(
                "listing_validation_failed",
                "A sample cannot be generated until required fields are present.",
                status_code=422,
                details={"fields": result["errors"]},
            )
        return result["illustrative_payload"]
