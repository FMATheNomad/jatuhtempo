import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings

_key: bytes | None = None


def _get_key() -> bytes:
    global _key
    if _key is not None:
        return _key
    secret = os.environ.get("ENCRYPTION_KEY", "")
    if not secret:
        raise RuntimeError("ENCRYPTION_KEY not configured")
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=settings.crypto_salt.encode(), iterations=100000)
    _key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
    return _key


def encrypt(plain_text: str) -> str:
    if not plain_text:
        return ""
    f = Fernet(_get_key())
    return f.encrypt(plain_text.encode()).decode()


def decrypt(cipher_text: str) -> str:
    if not cipher_text:
        return ""
    f = Fernet(_get_key())
    return f.decrypt(cipher_text.encode()).decode()
