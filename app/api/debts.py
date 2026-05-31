import uuid

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional

from app.core.auth import verify_token
from app.core.db import async_session_factory
from app.models.debt import Debt, DebtStatus
from app.models.user import User
from app.schemas.debt import DebtCreate, DebtResponse, MonthlySummary
from app.services.debt_service import (
    get_or_create_user, get_user_debts, create_debt, update_debt,
    get_monthly_summary, get_upcoming_debts, delete_debt, get_user_debt_by_id, update_debt_status, update_user_wa,
)
from app.services.payment_service import get_payments_for_debt

router = APIRouter(prefix="/api")


async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid token")
    payload = verify_token(authorization.split(" ", 1)[1])
    if not payload or payload.get("type") != "session":
        raise HTTPException(401, "Invalid or expired token")
    async with async_session_factory() as session:
        result = await session.execute(
            __import__("sqlalchemy").select(User).where(User.telegram_id == payload["telegram_id"])
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(404, "User not found")
        return user


class StatusUpdate(BaseModel):
    status: str


class PhoneUpdate(BaseModel):
    phone_number: str


class DebtCreateBody(BaseModel):
    platform: str
    amount: int
    due_date: str
    installment_current: Optional[int] = None
    installment_total: Optional[int] = None
    category: Optional[str] = None
    notes: Optional[str] = None


@router.get("/debts")
async def list_debts(
    status: str | None = None,
    platform: str | None = None,
    user: User = Depends(get_current_user),
):
    async with async_session_factory() as session:
        status_enum = DebtStatus(status) if status else None
        debts = await get_user_debts(session, user.id, status=status_enum, platform=platform)
        return [DebtResponse.model_validate(d) for d in debts]


@router.get("/debts/summary")
async def get_summary(user: User = Depends(get_current_user)):
    async with async_session_factory() as session:
        summary = await get_monthly_summary(session, user.id)
        return summary


@router.get("/debts/upcoming")
async def get_upcoming_endpoint(days: int = 30, user: User = Depends(get_current_user)):
    async with async_session_factory() as session:
        debts = await get_upcoming_debts(session, user.id, days)
        return [DebtResponse.model_validate(d) for d in debts]


@router.get("/debts/{debt_id_str}/payments")
async def get_debt_payments(debt_id_str: str, user: User = Depends(get_current_user)):
    try:
        did = uuid.UUID(debt_id_str)
    except ValueError:
        raise HTTPException(404, "Invalid debt id")

    async with async_session_factory() as session:
        debt = await get_user_debt_by_id(session, did, user.id)
        if not debt:
            raise HTTPException(404, "Debt not found")
        payments = await get_payments_for_debt(session, did, user.id)
        return [
            {
                "id": str(p.id),
                "debt_id": str(p.debt_id),
                "amount_paid": p.amount_paid,
                "paid_at": p.paid_at.isoformat(),
                "notes": p.notes,
            }
            for p in payments
        ]


@router.patch("/debts/{debt_id_str}/status")
async def patch_debt_status(debt_id_str: str, body: StatusUpdate, user: User = Depends(get_current_user)):
    try:
        did = uuid.UUID(debt_id_str)
    except ValueError:
        raise HTTPException(404, "Invalid debt id")

    try:
        new_status = DebtStatus(body.status)
    except ValueError:
        raise HTTPException(400, "Invalid status")

    async with async_session_factory() as session:
        debt = await get_user_debt_by_id(session, did, user.id)
        if not debt:
            raise HTTPException(404, "Debt not found")
        debt = await update_debt_status(session, did, new_status)
        return DebtResponse.model_validate(debt)


@router.get("/user/me")
async def get_current_user_endpoint(user: User = Depends(get_current_user)):
    return {
        "id": str(user.id),
        "telegram_id": user.telegram_id,
        "nama": user.nama,
        "phone_number": user.phone_number,
    }


@router.put("/user/phone")
async def update_phone(body: PhoneUpdate, user: User = Depends(get_current_user)):
    async with async_session_factory() as session:
        updated = await update_user_wa(session, user.telegram_id, phone_number=body.phone_number)
        if not updated:
            raise HTTPException(404, "User not found")
        return {"phone_number": updated.phone_number}
