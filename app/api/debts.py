import uuid
from typing import Optional

from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile, File
from pydantic import BaseModel

from sqlalchemy import select as sa_select

from app.core.auth import verify_token
from app.core.db import async_session_factory
from app.models.debt import Debt, DebtStatus
from app.models.user import User
from app.schemas.debt import DebtResponse
from app.services.debt_service import (
    get_or_create_user, get_user_debts, create_debt, update_debt,
    get_monthly_summary, get_upcoming_debts, delete_debt, get_user_debt_by_id, update_debt_status, update_user_wa,
)
from app.services.payment_service import get_payments_for_debt
from app.services.ocr_service import ocr_image
from app.services.ai_parser import parse_debt_from_text

router = APIRouter(prefix="/api")


async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid token")
    payload = verify_token(authorization.split(" ", 1)[1])
    if not payload or payload.get("type") != "session":
        raise HTTPException(401, "Invalid or expired token")

    telegram_id = payload.get("telegram_id")
    user_id = payload.get("user_id")

    async with async_session_factory() as session:
        if telegram_id is not None:
            result = await session.execute(
                sa_select(User).where(User.telegram_id == telegram_id)
            )
        elif user_id:
            result = await session.execute(
                sa_select(User).where(User.id == uuid.UUID(user_id))
            )
        else:
            raise HTTPException(401, "Invalid session")
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


@router.post("/ocr")
async def ocr_upload(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    import uuid as uuid_gen
    media_dir = Path("media")
    media_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename or "image.jpg").suffix or ".jpg"
    image_path = media_dir / f"{uuid_gen.uuid4()}{ext}"

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(400, "Image too large (max 10MB)")

    image_path.write_bytes(content)
    raw_text = await ocr_image(str(image_path))

    if not raw_text or len(raw_text) < 20:
        image_path.unlink(missing_ok=True)
        raise HTTPException(400, "Could not read text from image")

    parsed = await parse_debt_from_text(raw_text)

    image_path.unlink(missing_ok=True)

    return {
        "raw_text": raw_text,
        "parsed": parsed,
    }


@router.post("/debts")
async def create_debt_endpoint(body: DebtCreateBody, user: User = Depends(get_current_user)):
    from datetime import date
    try:
        due = date.fromisoformat(body.due_date) if isinstance(body.due_date, str) else body.due_date
    except (ValueError, TypeError):
        raise HTTPException(400, "Invalid due_date format (use YYYY-MM-DD)")
    from app.schemas.debt import DebtCreate as DebtCreateSchema
    data = DebtCreateSchema(
        platform=body.platform,
        amount=body.amount,
        due_date=due,
        installment_current=body.installment_current,
        installment_total=body.installment_total,
        category=body.category,
        notes=body.notes,
    )
    async with async_session_factory() as session:
        debt = await create_debt(session, user.id, data, source=DebtSource.manual)
        return DebtResponse.model_validate(debt)


@router.patch("/debts/{debt_id_str}")
async def patch_debt(debt_id_str: str, body: DebtCreateBody, user: User = Depends(get_current_user)):
    try:
        did = uuid.UUID(debt_id_str)
    except ValueError:
        raise HTTPException(404, "Invalid debt id")
    from datetime import date
    kwargs = {
        "platform": body.platform,
        "amount": body.amount,
        "category": body.category,
        "notes": body.notes,
        "installment_current": body.installment_current,
        "installment_total": body.installment_total,
    }
    try:
        kwargs["due_date"] = date.fromisoformat(body.due_date) if isinstance(body.due_date, str) else body.due_date
    except (ValueError, TypeError):
        raise HTTPException(400, "Invalid due_date")
    async with async_session_factory() as session:
        debt = await update_debt(session, did, user.id, **kwargs)
        if not debt:
            raise HTTPException(404, "Debt not found")
        return DebtResponse.model_validate(debt)


@router.delete("/debts/{debt_id_str}")
async def delete_debt_endpoint(debt_id_str: str, user: User = Depends(get_current_user)):
    try:
        did = uuid.UUID(debt_id_str)
    except ValueError:
        raise HTTPException(404, "Invalid debt id")
    async with async_session_factory() as session:
        ok = await delete_debt(session, did, user.id)
        if not ok:
            raise HTTPException(404, "Debt not found")
        return {"ok": True}


@router.get("/user/me")
async def get_current_user_endpoint(user: User = Depends(get_current_user)):
    return {
        "id": str(user.id),
        "telegram_id": user.telegram_id,
        "email": user.email,
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
