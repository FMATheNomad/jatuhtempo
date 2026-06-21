import logging
import random
import uuid
from datetime import date
from pathlib import Path

from aiogram import Router
from aiogram.types import CallbackQuery

from app.core.crypto import encrypt
from app.core.db import async_session_factory
from app.core.temp_store import pop_ocr
from app.models.debt import DebtSource, DebtStatus
from app.models.ocr_log import OcrLog
from app.schemas.debt import DebtCreate
from sqlalchemy import select
from app.services.debt_service import update_debt_status, get_or_create_user, create_debt, update_user_wa, delete_debt
from app.services.platform_matcher import reinforce_match
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
        user = await get_or_create_user(session, callback.from_user.id)
        debt = await update_debt_status(session, debt_id, DebtStatus.paid, user.id)

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
        user = await get_or_create_user(session, callback.from_user.id)
        debt = await update_debt_status(session, debt_id, DebtStatus.late, user.id)

    if debt:
        await callback.message.edit_text(
            f"🔴 {debt.platform} — Rp{debt.amount:,}\nStatus: 🔴 Terlambat"
        )
        await callback.answer("Utang ditandai terlambat!")
    else:
        await callback.answer("Utang tidak ditemukan.", show_alert=True)


@router.callback_query(lambda c: c.data and c.data.startswith("delete:"))
async def callback_delete(callback: CallbackQuery):
    debt_id_str = callback.data.split(":", 1)[1]
    try:
        debt_id = uuid.UUID(debt_id_str)
    except ValueError:
        await callback.answer("ID utang tidak valid.")
        return

    async with async_session_factory() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        deleted = await delete_debt(session, debt_id, user.id)

    if deleted:
        await callback.message.edit_text("🗑 Utang berhasil dihapus.")
        await callback.answer("✅ Dihapus!")
    else:
        await callback.answer("Utang tidak ditemukan atau bukan milik Anda.", show_alert=True)


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
                raw_text=encrypt(raw_text),
                parsed_json=parsed,
            )
            session.add(ocr_log)

        raw_due = parsed.get("due_date")
        try:
            due_date_val = date.fromisoformat(raw_due) if raw_due else date.today()
        except (ValueError, TypeError):
            due_date_val = date.today()

        try:
            debt_data = DebtCreate(
                platform=parsed.get("platform") or "Unknown",
                amount=parsed.get("amount") or 1,
                due_date=due_date_val,
                installment_current=parsed.get("installment_current"),
                installment_total=parsed.get("installment_total"),
                category=parsed.get("category"),
                notes=parsed.get("notes"),
            )
        except Exception as e:
            await callback.message.edit_text(f"❌ Gagal menyimpan: data tidak valid ({str(e)})")
            await callback.answer("Gagal menyimpan.", show_alert=True)
            return

        debt = await create_debt(session, user.id, debt_data, source=DebtSource.screenshot)

        await _learn_from_confirm(session, raw_text, debt.platform)

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


@router.callback_query(lambda c: c.data and c.data.startswith("confirm_debt:save:"))
async def callback_confirm_debt_save(callback: CallbackQuery):
    temp_key = callback.data.split(":", 2)[2]
    from app.core.temp_store import pop_temp

    data = pop_temp(temp_key)
    if not data:
        await callback.answer("Data sudah kadaluarsa. Kirim ulang teks.", show_alert=True)
        return

    parsed = data.get("parsed", {})
    raw_due = parsed.get("due_date")
    try:
        due_date_val = date.fromisoformat(raw_due) if raw_due else date.today()
    except (ValueError, TypeError):
        due_date_val = date.today()

    try:
        debt_data = DebtCreate(
            platform=parsed.get("platform") or "Unknown",
            amount=parsed.get("amount") or 1,
            due_date=due_date_val,
            installment_current=parsed.get("installment_current"),
            installment_total=parsed.get("installment_total"),
            interest_rate=parsed.get("interest_rate"),
            interest_type=parsed.get("interest_type"),
            category=parsed.get("category"),
            notes=parsed.get("notes"),
        )
    except Exception as e:
        await callback.message.edit_text(f"❌ Gagal menyimpan: data tidak valid ({str(e)})")
        await callback.answer("Gagal menyimpan.", show_alert=True)
        return

    async with async_session_factory() as session:
        user = await get_or_create_user(session, callback.from_user.id)
        debt = await create_debt(session, user.id, debt_data, source=DebtSource.manual)

        raw = data.get("raw_text") or data.get("user_input") or ""
        await _learn_from_confirm(session, raw, debt.platform)

    msg = (
        f"✅ Disimpan!\n"
        f"Platform: {debt.platform}\n"
        f"Jumlah: Rp{debt.amount:,}\n"
        f"Jatuh tempo: {debt.due_date}"
    )
    if debt.installment_current and debt.installment_total:
        msg += f"\nCicilan: {debt.installment_current}/{debt.installment_total}"
    if debt.interest_rate:
        bunga_type = {"daily": "/hari", "monthly": "/bln", "yearly": "/thn", "flat": "/flat"}.get(debt.interest_type, "")
        msg += f"\nBunga: {debt.interest_rate}%{bunga_type}"
    if debt.category:
        msg += f"\nKategori: {debt.category}"
    if debt.notes:
        msg += f"\nCatatan: {debt.notes}"

    await callback.message.edit_text(msg, reply_markup=debt_keyboard(debt.id))
    await callback.answer("Utang berhasil disimpan!")


@router.callback_query(lambda c: c.data and c.data.startswith("confirm_debt:cancel:"))
async def callback_confirm_debt_cancel(callback: CallbackQuery):
    temp_key = callback.data.split(":", 2)[2]
    from app.core.temp_store import pop_temp
    pop_temp(temp_key)
    await callback.message.edit_text("❌ Dibatalkan. Tidak ada data yang disimpan.")
    await callback.answer("Dibatalkan.")


async def _learn_from_confirm(session, raw_text: str, confirmed_platform: str) -> None:
    """Trigger positive reinforcement after user confirms a debt."""
    if not raw_text or not confirmed_platform:
        return
    from app.services.platform_matcher import match_platform
    suggested = await match_platform(raw_text, session)
    if suggested and suggested == confirmed_platform:
        await reinforce_match(session, raw_text, confirmed_platform)
