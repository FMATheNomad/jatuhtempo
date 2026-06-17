import uuid
import hashlib
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings

_blacklisted_tokens: set[str] = set()


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def blacklist_token(token: str) -> None:
    _blacklisted_tokens.add(_token_hash(token))


def is_blacklisted(token: str) -> bool:
    return _token_hash(token) in _blacklisted_tokens


def _require_jwt_secret():
    if not settings.jwt_secret:
        raise RuntimeError(
            "JWT_SECRET tidak dikonfigurasi. "
            "Set di .env atau Railway variables."
        )


def create_login_token(telegram_id: int) -> str:
    _require_jwt_secret()
    payload = {
        "telegram_id": telegram_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "iat": datetime.now(timezone.utc),
        "type": "login",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_session_token(telegram_id: int | None, user_id: uuid.UUID) -> str:
    _require_jwt_secret()
    payload = {
        "telegram_id": telegram_id,
        "user_id": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "iat": datetime.now(timezone.utc),
        "type": "session",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> dict | None:
    _require_jwt_secret()
    if is_blacklisted(token):
        return None
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.PyJWTError:
        return None
