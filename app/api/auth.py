import uuid

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy import select

from app.core.auth import verify_token, create_session_token, create_login_token
from app.core.db import async_session_factory
from app.models.user import User
from app.services.debt_service import get_or_create_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    token: str


class LoginResponse(BaseModel):
    session_token: str
    user_id: str
    telegram_id: int | None = None
    name: str | None = None


class LinkTelegramRequest(BaseModel):
    token: str


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


@router.post("/guest")
async def guest_login() -> LoginResponse:
    async with async_session_factory() as session:
        user = User(nama="Guest")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        session_token = create_session_token(None, user.id)

    return LoginResponse(
        session_token=session_token,
        user_id=str(user.id),
        name=user.nama,
    )


@router.post("/link-telegram")
async def link_telegram(req: LinkTelegramRequest, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing token")

    payload = verify_token(authorization.split(" ", 1)[1])
    if not payload or payload.get("type") != "session":
        raise HTTPException(401, "Invalid session")

    login_payload = verify_token(req.token)
    if not login_payload or login_payload.get("type") != "login":
        raise HTTPException(401, "Invalid or expired Telegram link token")

    telegram_id = login_payload["telegram_id"]
    user_id = uuid.UUID(payload["user_id"])

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(404, "User not found")

        existing = await session.execute(select(User).where(User.telegram_id == telegram_id))
        if existing.scalar_one_or_none():
            raise HTTPException(409, "Telegram sudah terhubung ke akun lain")

        user.telegram_id = telegram_id
        await session.commit()

        new_token = create_session_token(telegram_id, user.id)

    return LoginResponse(
        session_token=new_token,
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
