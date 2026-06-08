import logging
import random
import uuid
from datetime import date
from pathlib import Path

from aiogram import Router
from aiogram.types import CallbackQuery

from app.core.db import async_session_factory
from app.core.temp_store import pop_ocr
from app.models.debt import DebtSource, DebtStatus
from app.models.ocr_log import OcrLog
from app.schemas.debt import DebtCreate
from sqlalchemy import select
from app.services.debt_service import update_debt_status, get_or_create_user, create_debt, update_user_wa
from app.models.user import User
from app.platforms.telegram.keyboards.inline import debt_keyboard

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("paid:"))
async def callback_paid(callback: CallbackQuery):
    debt_id_str = callback.data.split(":", 1)[1]
    try:
        debt_id = uuid.UUID(debt_id_str)
    except ValueError:
        await callback.answer("ID utang tidak valid.")
        return

    async with async_session_factory() as session:
        debt = await update_debt_status(session, debt_id, DebtStatus.paid)

    if debt:
        party = random.choice(["🎉", "🥳", "🏆", "⭐", "🚀", "💪", "✨"])
        msgs = [
            f"SELAMAT! {debt.platform} sudah lunas!",
            f"LUNAS! {debt.platform} beres! Kebebasan finansial selangkah lagi!",
            f"Mantap! {debt.platform} lunas! Kamu hebat!",
            f"Yes! {debt.platform} selesai! Rasakan lega nya!",
            f"Keren! {debt.platform} lunas! Semakin dekat menuju bebas utang!",
        ]
        await callback.message.edit_text(
            f"{party} {random.choice(msgs)}\nRp{debt.amount:,} — Jatuh tempo {debt.due_date}"
        )
        await callback.answer("✅ Lunas! 🎉")
    else:
        await callback.answer("Utang tidak ditemukan.", show_alert=True)


@router.callback_query(lambda c: c.data and c.data.startswith("late:"))
async def callback_late(callback: CallbackQuery):
    debt_id_str = callback.data.split(":", 1)[1]
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


@router.callback_query(lambda c: c.data == "ocr_confirm")
async def callback_ocr_confirm(callback: CallbackQuery):
    data = pop_ocr(callback.from_user.id)
    if not data:
        await callback.answer("Data sudah kadaluarsa. Kirim ulang screenshot.", show_alert=True)
        return

    parsed = data["parsed"]
    raw_text = data.get("raw_text", "")
    image_path = data.get("image_path")

    async with async_session_factory() as session:
        user = await get_or_create_user(session, callback.from_user.id)

        if image_path:
            ocr_log = OcrLog(
                user_id=user.id,
                image_path=image_path,
                raw_text=raw_text,
                parsed_json=parsed,
            )
            session.add(ocr_log)

        raw_due = parsed.get("due_date")
        try:
            due_date_val = date.fromisoformat(raw_due) if raw_due else date.today()
        except (ValueError, TypeError):
            due_date_val = date.today()

        debt_data = DebtCreate(
            platform=parsed.get("platform") or "Unknown",
            amount=parsed.get("amount") or 0,
            due_date=due_date_val,
            installment_current=parsed.get("installment_current"),
            installment_total=parsed.get("installment_total"),
            category=parsed.get("category"),
            notes=parsed.get("notes"),
        )
        debt = await create_debt(session, user.id, debt_data, source=DebtSource.screenshot)

    msg = (
        f"✅ Disimpan!\n"
        f"Platform: {debt.platform}\n"
        f"Jumlah: Rp{debt.amount:,}\n"
        f"Jatuh tempo: {debt.due_date}"
    )
    await callback.message.edit_text(msg, reply_markup=debt_keyboard(debt.id))
    await callback.answer("Utang berhasil disimpan!")

    if image_path:
        try:
            Path(image_path).unlink()
        except OSError:
            pass


@router.callback_query(lambda c: c.data == "ocr_cancel")
async def callback_ocr_cancel(callback: CallbackQuery):
    data = pop_ocr(callback.from_user.id)
    await callback.message.edit_text("❌ Dibatalkan. Tidak ada data yang disimpan.")
    await callback.answer("Dibatalkan.")

    if data and data.get("image_path"):
        try:
            Path(data["image_path"]).unlink()
        except OSError:
            pass


@router.callback_query(lambda c: c.data == "wa_optout")
async def callback_wa_optout(callback: CallbackQuery):
    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = result.scalar_one_or_none()
        if user:
            await update_user_wa(session, user.telegram_id, optout=True)
    await callback.message.edit_text("⏸ Notifikasi tautkan WA tidak akan muncul lagi.")
    await callback.answer("Dimatikan.")
