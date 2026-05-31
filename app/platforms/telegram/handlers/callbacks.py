import logging

from aiogram import Router
from aiogram.types import CallbackQuery

from app.core.db import async_session_factory
from app.models.debt import DebtStatus
from app.services.debt_service import update_debt_status

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("paid:"))
async def callback_paid(callback: CallbackQuery):
    debt_id_str = callback.data.split(":", 1)[1]
    import uuid
    try:
        debt_id = uuid.UUID(debt_id_str)
    except ValueError:
        await callback.answer("ID utang tidak valid.")
        return

    async with async_session_factory() as session:
        debt = await update_debt_status(session, debt_id, DebtStatus.paid)

    if debt:
        await callback.message.edit_text(
            f"✅ {debt.platform} — Rp{debt.amount:,}\nStatus: ✅ Lunas"
        )
        await callback.answer("Utang ditandai lunas!")
    else:
        await callback.answer("Utang tidak ditemukan.", show_alert=True)


@router.callback_query(lambda c: c.data and c.data.startswith("late:"))
async def callback_late(callback: CallbackQuery):
    debt_id_str = callback.data.split(":", 1)[1]
    import uuid
    try:
        debt_id = uuid.UUID(debt_id_str)
    except ValueError:
        await callback.answer("ID utang tidak valid.")
        return

    async with async_session_factory() as session:
        debt = await update_debt_status(session, debt_id, DebtStatus.late)

    if debt:
        await callback.message.edit_text(
            f"🔴 {debt.platform} — Rp{debt.amount:,}\nStatus: 🔴 Terlambat"
        )
        await callback.answer("Utang ditandai terlambat!")
    else:
        await callback.answer("Utang tidak ditemukan.", show_alert=True)
