import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings

if not settings.jwt_secret:
    raise RuntimeError("JWT_SECRET tidak dikonfigurasi. Set di .env atau Railway variables.")


def create_login_token(telegram_id: int) -> str:
    payload = {
        "telegram_id": telegram_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "iat": datetime.now(timezone.utc),
        "type": "login",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_session_token(telegram_id: int, user_id: uuid.UUID) -> str:
    payload = {
        "telegram_id": telegram_id,
        "user_id": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
        "iat": datetime.now(timezone.utc),
        "type": "session",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.PyJWTError:
        return None
