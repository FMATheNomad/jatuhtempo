import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment


async def create_payment(
    session: AsyncSession, debt_id: uuid.UUID, user_id: uuid.UUID,
    amount_paid: int, notes: str | None = None,
) -> Payment:
    payment = Payment(
        debt_id=debt_id,
        user_id=user_id,
        amount_paid=amount_paid,
        notes=notes,
    )
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    return payment


async def get_payments_for_debt(session: AsyncSession, debt_id: uuid.UUID, user_id: uuid.UUID) -> list[Payment]:
    result = await session.execute(
        select(Payment)
        .where(Payment.debt_id == debt_id, Payment.user_id == user_id)
        .order_by(Payment.paid_at.desc())
    )
    return list(result.scalars().all())
