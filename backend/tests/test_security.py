import unittest

from cryptography.fernet import Fernet

from app.core.security import TokenCipher


class TokenCipherTests(unittest.TestCase):
    def test_marketplace_tokens_are_encrypted_at_rest(self) -> None:
        cipher = TokenCipher(Fernet.generate_key().decode())
        encrypted = cipher.encrypt({"refresh_token": "secret-token"})

        self.assertNotIn("secret-token", encrypted)
        self.assertEqual(cipher.decrypt(encrypted), {"refresh_token": "secret-token"})
