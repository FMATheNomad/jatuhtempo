import uuid
import time
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from sqlalchemy import select
from passlib.hash import bcrypt

from app.core.auth import verify_token, create_session_token, create_login_token
from app.core.db import async_session_factory
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

# FIX E: IP-based rate limiting for auth endpoints
_auth_rates: dict[str, list[float]] = defaultdict(list)
AUTH_RATE_LIMIT = 10  # requests
AUTH_RATE_WINDOW = 60  # seconds


def _check_auth_rate_limit(ip: str) -> bool:
    now = time.time()
    _auth_rates[ip] = [t for t in _auth_rates[ip] if now - t < AUTH_RATE_WINDOW]
    if len(_auth_rates[ip]) >= AUTH_RATE_LIMIT:
        return False
    _auth_rates[ip].append(now)
    return True


class LoginRequest(BaseModel):
    token: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    nama: str = ""


class LoginWebRequest(BaseModel):
    email: str
    password: str


class LinkTelegramRequest(BaseModel):
    token: str


class LoginResponse(BaseModel):
    session_token: str
    user_id: str
    telegram_id: int | None = None
    email: str | None = None
    nama: str | None = None


@router.post("/register")
async def register(req: RegisterRequest, request: Request = None) -> LoginResponse:
    if not _check_auth_rate_limit(request.client.host if request else "unknown"):
        raise HTTPException(429, "Too many requests. Please wait.")
    if not req.email or "@" not in req.email:
        raise HTTPException(400, "Email tidak valid")
    if len(req.password) < 6:
        raise HTTPException(400, "Password minimal 6 karakter")

    async with async_session_factory() as session:
        existing = await session.execute(select(User).where(User.email == req.email))
        if existing.scalar_one_or_none():
            raise HTTPException(409, "Email sudah terdaftar")

        user = User(email=req.email, password_hash=bcrypt.hash(req.password), nama=req.nama or "User")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        session_token = create_session_token(None, user.id)
        return LoginResponse(
            session_token=session_token, user_id=str(user.id),
            email=user.email, nama=user.nama,
        )


@router.post("/login-web")
async def login_web(req: LoginWebRequest, request: Request = None) -> LoginResponse:
    if not _check_auth_rate_limit(request.client.host if request else "unknown"):
        raise HTTPException(429, "Too many requests. Please wait.")
    if not req.email or not req.password:
        raise HTTPException(400, "Email dan password wajib diisi")

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == req.email))
        user = result.scalar_one_or_none()
        if not user or not user.password_hash:
            raise HTTPException(401, "Email atau password salah")
        if not bcrypt.verify(req.password, user.password_hash):
            raise HTTPException(401, "Email atau password salah")

        session_token = create_session_token(user.telegram_id, user.id)
        return LoginResponse(
            session_token=session_token, user_id=str(user.id),
            telegram_id=user.telegram_id, email=user.email, nama=user.nama,
        )


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
        nama=user.nama,
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
        nama=user.nama,
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
