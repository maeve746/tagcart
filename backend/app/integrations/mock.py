"""Deterministic, offline marketplace simulators for development and demos."""

import hashlib
from typing import Any, Dict, Iterable, List, Tuple

from app.integrations.base import (
    FieldValidationError,
    ListingValidationResult,
    MarketplaceSubmissionAdapter,
)


MOCK_NOTICE = (
    "Illustrative mock workflow only. No product was submitted, published, "
    "or made live on any marketplace."
)


def _first(listing: Dict[str, Any], *paths: str) -> Any:
    for path in paths:
        value: Any = listing
        for part in path.split("."):
            if not isinstance(value, dict):
                value = None
                break
            value = value.get(part)
        if value not in (None, "", [], {}):
            return value
    return None


def _errors(values: Iterable[Tuple[str, Any, str]]) -> List[FieldValidationError]:
    return [
        FieldValidationError(field=field, code="required", message=message)
        for field, value, message in values
        if value in (None, "", [], {})
    ]


class BaseMockAdapter(MarketplaceSubmissionAdapter):
    mode = "mock"

    def final_outcome(self, listing_id: str) -> str:
        digest = hashlib.sha256(
            f"tagcart-mock:{self.marketplace}:{listing_id}".encode("utf-8")
        ).digest()
        return "rejected" if digest[0] % 5 == 0 else "completed"


class AmazonMockAdapter(BaseMockAdapter):
    marketplace = "amazon"
    schema_label = "Illustrative TagCart Amazon sample; not an official SP-API schema."

    def validate(self, listing: Dict[str, Any]) -> ListingValidationResult:
        payload = {
            "schema_label": self.schema_label,
            "compliance_claim": False,
            "seller_sku": _first(listing, "sku"),
            "title": _first(listing, "title", "name", "content.title"),
            "brand": _first(listing, "brand", "analysis.attributes.brand"),
            "category": _first(listing, "category"),
            "description": _first(listing, "description", "content.description"),
            "bullet_points": _first(listing, "bullets", "content.bullets"),
            "price": _first(listing, "price"),
            "currency": _first(listing, "currency"),
            "quantity": _first(listing, "quantity"),
            "keywords": _first(listing, "keywords", "content.keywords") or [],
        }
        errors = _errors([
            ("sku", payload["seller_sku"], "Seller SKU is required."),
            ("title", payload["title"], "Product title is required."),
            ("brand", payload["brand"], "Brand is required."),
            ("category", payload["category"], "Category is required."),
            ("description", payload["description"], "Description is required."),
            ("bullets", payload["bullet_points"], "At least one bullet point is required."),
            ("price", payload["price"], "Price is required."),
            ("currency", payload["currency"], "Currency is required."),
            ("quantity", payload["quantity"], "Quantity is required."),
        ])
        return ListingValidationResult(not errors, errors, payload)


class MyntraMockAdapter(BaseMockAdapter):
    marketplace = "myntra"
    schema_label = "Illustrative TagCart Myntra sample; not an official partner schema."

    def validate(self, listing: Dict[str, Any]) -> ListingValidationResult:
        payload = {
            "schema_label": self.schema_label,
            "compliance_claim": False,
            "style_id": _first(listing, "sku"),
            "product_name": _first(listing, "title", "name", "content.title"),
            "brand": _first(listing, "brand", "analysis.attributes.brand"),
            "article_type": _first(listing, "article_type", "category"),
            "description": _first(listing, "description", "content.description"),
            "base_colour": _first(listing, "color", "analysis.attributes.color"),
            "mrp": _first(listing, "mrp", "price"),
            "selling_price": _first(listing, "selling_price", "price"),
            "sizes": _first(listing, "sizes", "analysis.attributes.sizes"),
            "quantity": _first(listing, "quantity"),
        }
        errors = _errors([
            ("sku", payload["style_id"], "Style/SKU identifier is required."),
            ("title", payload["product_name"], "Product name is required."),
            ("brand", payload["brand"], "Brand is required."),
            ("category", payload["article_type"], "Article type/category is required."),
            ("description", payload["description"], "Description is required."),
            ("color", payload["base_colour"], "Base colour is required."),
            ("price", payload["selling_price"], "Selling price is required."),
            ("sizes", payload["sizes"], "At least one size is required."),
            ("quantity", payload["quantity"], "Quantity is required."),
        ])
        return ListingValidationResult(not errors, errors, payload)


MOCK_ADAPTERS = {
    "amazon": AmazonMockAdapter,
    "myntra": MyntraMockAdapter,
}


def get_mock_adapter(marketplace: str) -> MarketplaceSubmissionAdapter:
    adapter_class = MOCK_ADAPTERS.get(marketplace.lower())
    if not adapter_class:
        from app.integrations.base import MarketplaceError

        raise MarketplaceError(
            "marketplace_not_supported",
            "Supported mock marketplaces are amazon and myntra.",
            status_code=404,
        )
    return adapter_class()
