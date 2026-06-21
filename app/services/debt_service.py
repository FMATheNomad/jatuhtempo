import logging
import uuid
from datetime import date, datetime, timezone, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.debt import Debt, DebtStatus, DebtSource
from app.models.payment import Payment
from app.models.reminder import Reminder
from app.models.user import User
from app.schemas.debt import DebtCreate, MonthlySummary
from app.core.platforms import PLATFORMS
from app.services.platform_rate_service import update_platform_rate

logger = logging.getLogger(__name__)


async def get_or_create_user(session: AsyncSession, telegram_id: int, nama: str | None = None) -> User:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id, nama=nama)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def create_debt(session: AsyncSession, user_id: uuid.UUID, data: DebtCreate, source: DebtSource = DebtSource.manual) -> Debt:
    debt = Debt(
        user_id=user_id,
        platform=data.platform,
        amount=data.amount,
        due_date=data.due_date,
        installment_current=data.installment_current,
        installment_total=data.installment_total,
        category=data.category,
        notes=data.notes,
        interest_rate=data.interest_rate,
        interest_type=data.interest_type,
        source=source,
    )
    session.add(debt)
    await session.commit()
    await session.refresh(debt)

    await _create_reminders(session, debt)

    # Learn from this debt if it has interest rate info and is a known platform
    await _learn_from_debt(session, debt, data.interest_rate, data.interest_type)

    return debt


async def _create_reminders(session: AsyncSession, debt: Debt):
    due = debt.due_date
    reminder_types = [
        ("H-7", due - timedelta(days=7)),
        ("H-3", due - timedelta(days=3)),
        ("H-1", due - timedelta(days=1)),
        ("due", due),
        ("overdue", due + timedelta(days=1)),
    ]
    for rtype, rdate in reminder_types:
        remind_at = datetime.combine(rdate, datetime.min.time(), tzinfo=timezone.utc)
        reminder = Reminder(
            debt_id=debt.id,
            user_id=debt.user_id,
            remind_at=remind_at,
            type=rtype,
        )
        session.add(reminder)
    await session.commit()


async def get_user_debts(
    session: AsyncSession, user_id: uuid.UUID,
    status: DebtStatus | None = None, platform: str | None = None,
    skip: int = 0, limit: int = 50,
) -> list[Debt]:
    stmt = select(Debt).where(Debt.user_id == user_id)
    if status:
        stmt = stmt.where(Debt.status == status)
    if platform:
        stmt = stmt.where(Debt.platform.ilike(f"%{platform}%"))
    stmt = stmt.order_by(Debt.due_date.asc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_monthly_summary(session: AsyncSession, user_id: uuid.UUID) -> MonthlySummary:
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    active_result = await session.execute(
        select(func.count(), func.coalesce(func.sum(Debt.amount), 0)).where(
            Debt.user_id == user_id, Debt.status == DebtStatus.active
        )
    )
    total_active, total_amount = active_result.one()

    paid_result = await session.execute(
        select(func.count(), func.coalesce(func.sum(Debt.amount), 0)).where(
            Debt.user_id == user_id,
            Debt.status == DebtStatus.paid,
            func.coalesce(Debt.paid_at, Debt.updated_at) >= start_of_month,
        )
    )
    paid_count, paid_amount = paid_result.one()

    upcoming_result = await session.execute(
        select(Debt).where(
            Debt.user_id == user_id,
            Debt.status == DebtStatus.active,
            Debt.due_date >= now.date(),
        ).order_by(Debt.due_date.asc())
    )
    upcoming = list(upcoming_result.scalars().all())

    return MonthlySummary(
        total_active=total_active,
        total_amount=total_amount,
        paid_this_month=paid_count,
        paid_amount=paid_amount,
        upcoming=upcoming,
    )


async def get_upcoming_debts(session: AsyncSession, user_id: uuid.UUID, days: int = 30) -> list[Debt]:
    from datetime import timedelta
    now = datetime.now(timezone.utc).date()
    deadline = now + timedelta(days=days)
    result = await session.execute(
        select(Debt).where(
            Debt.user_id == user_id,
            Debt.status == DebtStatus.active,
            Debt.due_date >= now,
            Debt.due_date <= deadline,
        ).order_by(Debt.due_date.asc())
    )
    return list(result.scalars().all())


async def update_debt_status(session: AsyncSession, debt_id: uuid.UUID, status: DebtStatus, user_id: uuid.UUID | None = None):
    debt = await session.get(Debt, debt_id)
    if not debt:
        return None
    if user_id and debt.user_id != user_id:
        return None
    debt.status = status
    if status == DebtStatus.paid:
        debt.paid_at = datetime.now(timezone.utc)
        payment = Payment(debt_id=debt.id, user_id=debt.user_id, amount_paid=debt.amount)
        session.add(payment)
    await session.commit()
    await session.refresh(debt)
    return debt


async def update_user_wa(
    session: AsyncSession, telegram_id: int,
    phone_number: str | None = None, optout: bool | None = None,
) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if phone_number is not None:
        if phone_number == "":
            user.phone_number = None
            user.wa_linked_at = None
        else:
            user.phone_number = phone_number
            user.wa_linked_at = datetime.now(timezone.utc)
    if optout is not None:
        user.wa_reminder_optout = optout
    await session.commit()
    await session.refresh(user)
    return user


async def delete_debt(session: AsyncSession, debt_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    debt = await session.get(Debt, debt_id)
    if debt and debt.user_id == user_id:
        await session.delete(debt)
        await session.commit()
        return True
    return False


async def get_user_debt_by_id(session: AsyncSession, debt_id: uuid.UUID, user_id: uuid.UUID) -> Debt | None:
    debt = await session.get(Debt, debt_id)
    if debt and debt.user_id == user_id:
        return debt
    return None


async def update_debt(session: AsyncSession, debt_id: uuid.UUID, user_id: uuid.UUID, null_fields: list[str] | None = None, **kwargs) -> Debt | None:
    debt = await session.get(Debt, debt_id)
    if not debt or debt.user_id != user_id:
        return None
    for key, value in kwargs.items():
        if value is not None:
            setattr(debt, key, value)
    if null_fields:
        for field in null_fields:
            if hasattr(debt, field):
                setattr(debt, field, None)
    if kwargs.get("status") == DebtStatus.paid:
        debt.paid_at = datetime.now(timezone.utc)
        payment = Payment(debt_id=debt.id, user_id=debt.user_id, amount_paid=debt.amount)
        session.add(payment)
    await session.commit()
    await session.refresh(debt)

    rate = kwargs.get("interest_rate")
    rate_type = kwargs.get("interest_type")
    await _learn_from_debt(session, debt, rate, rate_type)

    return debt


async def _learn_from_debt(session: AsyncSession, debt: Debt, rate: float | None, rate_type: str | None) -> bool | None:
    """Update platform rate from a debt if it has interest info and a known platform.

    Returns:
        True if rate was accepted and learned,
        False if it was rejected as outlier,
        None if no learning was attempted (no rate or unknown platform).
    """
    if rate is not None and debt.platform in PLATFORMS and debt.platform != "Lainnya":
        result = await update_platform_rate(session, debt.platform, rate, rate_type)
        if result is None:
            logger.info("Rate rejected as outlier for platform=%s rate=%.4f", debt.platform, rate)
            return False
        return True
    return None
