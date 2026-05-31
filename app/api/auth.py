import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.auth import verify_token, create_session_token
from app.core.db import async_session_factory
from app.models.user import User
from sqlalchemy import select

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    token: str


class LoginResponse(BaseModel):
    session_token: str
    user_id: str
    telegram_id: int
    name: str | None


@router.post("/login")
async def login(req: LoginRequest) -> LoginResponse:
    payload = verify_token(req.token)
    if not payload or payload.get("type") != "login":
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    telegram_id = payload["telegram_id"]

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        session_token = create_session_token(telegram_id, user.id)

    return LoginResponse(
        session_token=session_token,
        user_id=str(user.id),
        telegram_id=telegram_id,
        name=user.nama,
    )


class VerifyResponse(BaseModel):
    valid: bool
    telegram_id: int | None = None
    user_id: str | None = None


@router.get("/verify")
async def verify(token: str) -> VerifyResponse:
    payload = verify_token(token)
    if not payload or payload.get("type") != "session":
        return VerifyResponse(valid=False)
    return VerifyResponse(
        valid=True,
        telegram_id=payload.get("telegram_id"),
        user_id=payload.get("user_id"),
    )
