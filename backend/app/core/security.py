"""Security helpers for marketplace credentials."""

import json
from typing import Dict

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class TokenEncryptionNotConfiguredError(RuntimeError):
    """Raised when token encryption has not been configured."""


class TokenDecryptionError(RuntimeError):
    """Raised when encrypted marketplace credentials cannot be decoded."""


class TokenCipher:
    """Encrypt marketplace credentials before they reach Supabase."""

    def __init__(self, key: str):
        try:
            self._fernet = Fernet(key.encode("utf-8"))
        except (TypeError, ValueError) as exc:
            raise TokenEncryptionNotConfiguredError(
                "MARKETPLACE_TOKEN_ENCRYPTION_KEY is not a valid Fernet key."
            ) from exc

    def encrypt(self, values: Dict[str, str]) -> str:
        payload = json.dumps(values, separators=(",", ":")).encode("utf-8")
        return self._fernet.encrypt(payload).decode("utf-8")

    def decrypt(self, encrypted: str) -> Dict[str, str]:
        try:
            payload = self._fernet.decrypt(encrypted.encode("utf-8"))
            return json.loads(payload.decode("utf-8"))
        except (InvalidToken, ValueError, json.JSONDecodeError) as exc:
            raise TokenDecryptionError(
                "Stored marketplace credentials could not be decrypted."
            ) from exc


def get_token_cipher() -> TokenCipher:
    settings = get_settings()
    key = (
        settings.marketplace_token_encryption_key.get_secret_value().strip()
        if settings.marketplace_token_encryption_key
        else ""
    )
    if not key:
        raise TokenEncryptionNotConfiguredError(
            "MARKETPLACE_TOKEN_ENCRYPTION_KEY is required."
        )
    return TokenCipher(key)
