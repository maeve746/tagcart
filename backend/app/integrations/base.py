"""Shared marketplace adapter contracts and errors."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class MarketplaceError(RuntimeError):
    """Safe error type returned by marketplace API routes."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 502,
        retryable: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.retryable = retryable
        self.details = details


@dataclass(frozen=True)
class ConnectionResult:
    external_account_id: str
    encrypted_values: Dict[str, str]
    token_expires_at: Optional[str]
    metadata: Dict[str, Any]


class MarketplaceAdapter(ABC):
    """Common interface for marketplace connection adapters."""

    marketplace: str

    @abstractmethod
    def configuration_status(self) -> Dict[str, Any]:
        """Return non-secret configuration readiness information."""

    @abstractmethod
    async def connect(self, **kwargs: Any) -> ConnectionResult:
        """Perform the marketplace-specific connection handshake."""


@dataclass(frozen=True)
class FieldValidationError:
    field: str
    code: str
    message: str


@dataclass(frozen=True)
class ListingValidationResult:
    valid: bool
    errors: List[FieldValidationError]
    illustrative_payload: Dict[str, Any]


class MarketplaceSubmissionAdapter(ABC):
    """Interface for listing validation and submission adapters.

    Mock adapters implement this interface today. Production submission is
    deliberately not wired until the required marketplace approvals exist.
    """

    marketplace: str
    mode: str

    @abstractmethod
    def validate(self, listing: Dict[str, Any]) -> ListingValidationResult:
        """Validate and map one owned TagCart listing."""

    @abstractmethod
    def final_outcome(self, listing_id: str) -> str:
        """Return the deterministic terminal mock state."""
