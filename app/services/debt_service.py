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
        source=source,
    )
    session.add(debt)
    await session.commit()
    await session.refresh(debt)

    await _create_reminders(session, debt)
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
) -> list[Debt]:
    stmt = select(Debt).where(Debt.user_id == user_id)
    if status:
        stmt = stmt.where(Debt.status == status)
    if platform:
        stmt = stmt.where(Debt.platform.ilike(f"%{platform}%"))
    stmt = stmt.order_by(Debt.due_date.asc())
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


async def update_debt_status(session: AsyncSession, debt_id: uuid.UUID, status: DebtStatus):
    debt = await session.get(Debt, debt_id)
    if debt:
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


async def update_debt(session: AsyncSession, debt_id: uuid.UUID, user_id: uuid.UUID, **kwargs) -> Debt | None:
    debt = await session.get(Debt, debt_id)
    if not debt or debt.user_id != user_id:
        return None
    for key, value in kwargs.items():
        if value is not None:
            setattr(debt, key, value)
    if kwargs.get("status") == DebtStatus.paid:
        debt.paid_at = datetime.now(timezone.utc)
        payment = Payment(debt_id=debt.id, user_id=debt.user_id, amount_paid=debt.amount)
        session.add(payment)
    await session.commit()
    await session.refresh(debt)
    return debt
