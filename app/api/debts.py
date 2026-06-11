import uuid
from typing import Optional

from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile, File, Request
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
from app.services.audit_service import log_audit
from app.services.platform_matcher import match_platform, learn_from_correction
from app.services.platform_rate_service import (
    get_all_platform_rates,
    get_platform_rate,
    update_platform_rate,
    reset_platform_rate,
)
from app.schemas.debt import PlatformRateResponse
from app.models.platform_rate import PlatformRate

router = APIRouter(prefix="/api")

logger = __import__("logging").getLogger(__name__)


def _check_admin(user: User) -> bool:
    """Simple admin check: subscription 'pro' or email in ADMIN_EMAILS env var."""
    if user.subscription_status == "pro":
        return True
    admin_emails = __import__("os").environ.get("ADMIN_EMAILS", "")
    if admin_emails and user.email and user.email in [e.strip() for e in admin_emails.split(",")]:
        return True
    return False


def get_client_ip(request: Request = None) -> str | None:
    if request and request.client:
        return request.client.host
    return None


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
    interest_rate: Optional[float] = None
    interest_type: Optional[str] = None
    installment_current: Optional[int] = None
    installment_total: Optional[int] = None
    category: Optional[str] = None
    notes: Optional[str] = None


@router.get("/debts")
async def list_debts(
    status: str | None = None,
    platform: str | None = None,
    user: User = Depends(get_current_user),
    request: Request = None,
):
    try:
        async with async_session_factory() as session:
            status_enum = DebtStatus(status) if status else None
            debts = await get_user_debts(session, user.id, status=status_enum, platform=platform)
            return [DebtResponse.model_validate(d) for d in debts]
    except Exception:
        logger.exception("Failed to list debts")
        raise HTTPException(500, "Internal server error")


@router.get("/debts/summary")
async def get_summary(user: User = Depends(get_current_user)):
    try:
        async with async_session_factory() as session:
            summary = await get_monthly_summary(session, user.id)
            return summary
    except Exception:
        logger.exception("Failed to get summary")
        raise HTTPException(500, "Internal server error")


@router.get("/debts/upcoming")
async def get_upcoming_endpoint(days: int = 30, user: User = Depends(get_current_user)):
    try:
        async with async_session_factory() as session:
            debts = await get_upcoming_debts(session, user.id, days)
            return [DebtResponse.model_validate(d) for d in debts]
    except Exception:
        logger.exception("Failed to get upcoming debts")
        raise HTTPException(500, "Internal server error")


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
async def patch_debt_status(debt_id_str: str, body: StatusUpdate, user: User = Depends(get_current_user), request: Request = None):
    try:
        did = uuid.UUID(debt_id_str)
    except ValueError:
        raise HTTPException(404, "Invalid debt id")

    try:
        new_status = DebtStatus(body.status)
    except ValueError:
        raise HTTPException(400, "Invalid status")

    async with async_session_factory() as session:
        try:
            debt = await get_user_debt_by_id(session, did, user.id)
            if not debt:
                raise HTTPException(404, "Debt not found")
            debt = await update_debt_status(session, did, new_status, user.id)
            await log_audit(session, user.id, "update_status", "debt", str(did), f"→ {body.status}", ip_address=get_client_ip(request))
            return DebtResponse.model_validate(debt)
        except HTTPException:
            raise
        except Exception:
            logger.exception("Failed to update debt status")
            raise HTTPException(500, "Internal server error")


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

    async with async_session_factory() as session:
        matched = await match_platform(raw_text, session)
        if matched and (not parsed.get("platform") or parsed["platform"] in ("Tidak Diketahui", None)):
            parsed["platform"] = matched

    image_path.unlink(missing_ok=True)

    return {
        "raw_text": raw_text,
        "parsed": parsed,
    }


@router.post("/debts/parse-natural")
async def parse_natural_debt(body: dict, user: User = Depends(get_current_user)):
    """
    Parse debt information from natural language text using AI.

    Body: {"text": "gua utang 2000 ke bahlul bayar tanggal 2"}
    Returns: {"parsed": {...}} or {"parsed": null, "error": "..."}
    """
    text = body.get("text", "").strip() if body else ""
    if not text:
        raise HTTPException(400, "text is required")

    try:
        parsed = await parse_debt_from_text(text)
        return {"parsed": parsed}
    except ValueError as e:
        return {"parsed": None, "error": str(e)}
    except Exception as e:
        logger = __import__("logging").getLogger(__name__)
        logger.exception("Failed to parse natural language debt")
        return {"parsed": None, "error": f"Parsing failed: {str(e)}"}


class TrainPlatformRequest(BaseModel):
    raw_text: str
    platform: str
    old_platform: str | None = None


@router.post("/platform/learn")
async def learn_platform(body: TrainPlatformRequest, user: User = Depends(get_current_user)):
    async with async_session_factory() as session:
        await learn_from_correction(session, body.raw_text, body.platform, body.old_platform)
    return {"ok": True}


@router.get("/platforms/rates")
async def list_platform_rates():
    """Public reference data: aggregated interest rates per platform."""
    async with async_session_factory() as session:
        rates = await get_all_platform_rates(session)
        return [PlatformRateResponse.model_validate(r) for r in rates]


# --- Admin endpoints for platform rates ---


class AdminRateUpdate(BaseModel):
    avg_rate: float | None = None
    common_type: str | None = None


@router.get("/admin/platforms/rates")
async def admin_list_platform_rates(user: User = Depends(get_current_user)):
    """Return all platform rates sorted by sample_count descending (admin)."""
    if not _check_admin(user):
        logger.warning("Non-admin user %s accessed admin platform rates list", user.id)
    async with async_session_factory() as session:
        rates = await get_all_platform_rates(session)
        rates.sort(key=lambda r: r.sample_count, reverse=True)
        return [PlatformRateResponse.model_validate(r) for r in rates]


@router.put("/admin/platforms/rates/{platform}")
async def admin_update_platform_rate(
    platform: str, body: AdminRateUpdate, user: User = Depends(get_current_user)
):
    """Manually set/override a platform's rate data. Sets confidence to 1.0 (admin-verified)."""
    if not _check_admin(user):
        logger.warning("Non-admin user %s attempted admin rate update for %s", user.id, platform)
        raise HTTPException(403, "Admin access required")
    async with async_session_factory() as session:
        result = await session.execute(
            sa_select(PlatformRate).where(PlatformRate.platform == platform)
        )
        existing = result.scalar_one_or_none()
        if existing:
            if body.avg_rate is not None:
                existing.avg_rate = body.avg_rate
            if body.common_type is not None:
                existing.common_type = body.common_type
            existing.confidence = 1.0
        else:
            existing = PlatformRate(
                platform=platform,
                avg_rate=body.avg_rate or 0.0,
                common_type=body.common_type,
                sample_count=1,
                confidence=1.0,
                type_counts={},
            )
            session.add(existing)
        await session.commit()
        await session.refresh(existing)
        return PlatformRateResponse.model_validate(existing)


@router.delete("/admin/platforms/rates/{platform}")
async def admin_delete_platform_rate(
    platform: str, user: User = Depends(get_current_user)
):
    """Delete a platform rate entry (admin)."""
    if not _check_admin(user):
        logger.warning("Non-admin user %s attempted admin rate delete for %s", user.id, platform)
        raise HTTPException(403, "Admin access required")
    async with async_session_factory() as session:
        ok = await reset_platform_rate(session, platform)
        if not ok:
            raise HTTPException(404, f"Platform rate '{platform}' not found")
        return {"ok": True}


# --- Suggest endpoint ---


@router.get("/platforms/rates/suggest")
async def suggest_platform_rate(platform: str):
    """Return suggested rate for a platform if confidence > 0.3."""
    async with async_session_factory() as session:
        rate = await get_platform_rate(session, platform)
        if not rate or rate.confidence <= 0.3:
            raise HTTPException(404, f"No reliable rate data for '{platform}'")
        return PlatformRateResponse.model_validate(rate)


@router.post("/debts")
async def create_debt_endpoint(body: DebtCreateBody, user: User = Depends(get_current_user), request: Request = None):
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
        interest_rate=body.interest_rate,
        interest_type=body.interest_type,
        installment_current=body.installment_current,
        installment_total=body.installment_total,
        category=body.category,
        notes=body.notes,
    )
    async with async_session_factory() as session:
        try:
            debt = await create_debt(session, user.id, data, source=DebtSource.manual)
            await log_audit(session, user.id, "create", "debt", str(debt.id), ip_address=get_client_ip(request))
            return DebtResponse.model_validate(debt)
        except Exception:
            logger.exception("Failed to create debt")
            raise HTTPException(500, "Internal server error")


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
        "interest_rate": body.interest_rate,
        "interest_type": body.interest_type,
        "installment_current": body.installment_current,
        "installment_total": body.installment_total,
    }
    try:
        kwargs["due_date"] = date.fromisoformat(body.due_date) if isinstance(body.due_date, str) else body.due_date
    except (ValueError, TypeError):
        raise HTTPException(400, "Invalid due_date")
    async with async_session_factory() as session:
        try:
            debt = await update_debt(session, did, user.id, **kwargs)
            if not debt:
                raise HTTPException(404, "Debt not found")
            return DebtResponse.model_validate(debt)
        except HTTPException:
            raise
        except Exception:
            logger.exception("Failed to update debt")
            raise HTTPException(500, "Internal server error")


@router.delete("/debts/{debt_id_str}")
async def delete_debt_endpoint(debt_id_str: str, user: User = Depends(get_current_user), request: Request = None):
    try:
        did = uuid.UUID(debt_id_str)
    except ValueError:
        raise HTTPException(404, "Invalid debt id")
    async with async_session_factory() as session:
        try:
            ok = await delete_debt(session, did, user.id)
            if not ok:
                raise HTTPException(404, "Debt not found")
            await log_audit(session, user.id, "delete", "debt", str(did), ip_address=get_client_ip(request))
            return {"ok": True}
        except HTTPException:
            raise
        except Exception:
            logger.exception("Failed to delete debt")
            raise HTTPException(500, "Internal server error")


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
