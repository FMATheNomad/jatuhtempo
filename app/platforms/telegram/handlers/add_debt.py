from datetime import date, datetime, timezone

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.core.config import settings
from app.core.db import async_session_factory
from app.core.platforms import PLATFORMS, CATEGORIES
from app.core.ratelimit import check_rate_limit
from app.schemas.debt import DebtCreate
from app.services.debt_service import get_or_create_user, create_debt
from app.models.debt import DebtSource
from app.platforms.telegram.keyboards.inline import debt_keyboard

router = Router()


class AddDebt(StatesGroup):
    platform = State()
    amount = State()
    due_date = State()
    installment = State()
    category = State()
    confirm = State()


def platform_keyboard() -> InlineKeyboardMarkup:
    rows = []
    row = []
    for p in PLATFORMS:
        row.append(InlineKeyboardButton(text=p, callback_data=f"adb_plat:{p}"))
        if len(row) >= 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="❌ Batal", callback_data="adb_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def category_keyboard() -> InlineKeyboardMarkup:
    rows = []
    row = []
    for c in CATEGORIES:
        row.append(InlineKeyboardButton(text=c, callback_data=f"adb_cat:{c}"))
        if len(row) >= 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="⏭ Lewati", callback_data="adb_skip_cat")])
    rows.append([InlineKeyboardButton(text="❌ Batal", callback_data="adb_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def installment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1× (Bayar penuh)", callback_data="adb_inst:1/1")],
        [InlineKeyboardButton(text="3×", callback_data="adb_inst:1/3")],
        [InlineKeyboardButton(text="6×", callback_data="adb_inst:1/6")],
        [InlineKeyboardButton(text="12×", callback_data="adb_inst:1/12")],
        [InlineKeyboardButton(text="⏭ Tidak ada cicilan", callback_data="adb_skip_inst")],
        [InlineKeyboardButton(text="❌ Batal", callback_data="adb_cancel")],
    ])


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Simpan", callback_data="adb_save")],
        [InlineKeyboardButton(text="❌ Batal", callback_data="adb_cancel")],
    ])


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Batal", callback_data="adb_cancel")],
    ])


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    if not check_rate_limit(message.from_user.id):
        await message.reply("⏳ Mohon tunggu...")
        return

    # Check if user provided inline args
    text = message.text.removeprefix("/add").strip()
    if text:
        try:
            import shlex
            parts = shlex.split(text)
            if len(parts) >= 3:
                platform = parts[0]
                amount = int(parts[1])
                due = date.fromisoformat(parts[2])
                data = DebtCreate(platform=platform, amount=amount, due_date=due)
                async with async_session_factory() as session:
                    user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
                    debt = await create_debt(session, user.id, data, source=DebtSource.manual)
                msg = f"Utang tercatat!\n{debt.platform} — Rp{debt.amount:,}\nJatuh tempo: {debt.due_date}"
                await message.reply(msg, reply_markup=debt_keyboard(debt.id))
                return
        except (ValueError, IndexError):
            pass

    await state.set_state(AddDebt.platform)
    await message.reply(
        "➕ Tambah utang baru — pilih platform:",
        reply_markup=platform_keyboard(),
    )


@router.callback_query(lambda c: c.data == "adb_cancel")
async def cancel_add(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Dibatalkan.")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("adb_plat:"))
async def select_platform(callback: CallbackQuery, state: FSMContext):
    platform = callback.data.split(":", 1)[1]
    await state.update_data(platform=platform)
    await state.set_state(AddDebt.amount)
    await callback.message.edit_text(f"Platform: {platform}\n\nBerapa jumlah utang? (angka saja, Rp)")
    await callback.answer()


@router.message(AddDebt.amount)
async def input_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text.replace(".", "").replace(",", "").strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.reply("Masukkan jumlah yang valid, contoh: 500000")
        return
    await state.update_data(amount=amount)
    await state.set_state(AddDebt.due_date)
    await message.reply(f"Jumlah: Rp{amount:,}\n\nTanggal jatuh tempo? (YYYY-MM-DD)")


@router.message(AddDebt.due_date)
async def input_due_date(message: Message, state: FSMContext):
    try:
        due = date.fromisoformat(message.text.strip())
    except ValueError:
        await message.reply("Format tanggal: YYYY-MM-DD. Contoh: 2026-07-15")
        return
    await state.update_data(due_date=str(due))
    await state.set_state(AddDebt.installment)
    await message.reply(f"Jatuh tempo: {due}\n\nAda cicilan?", reply_markup=installment_keyboard())


@router.callback_query(lambda c: c.data.startswith("adb_inst:") or c.data == "adb_skip_inst")
async def select_installment(callback: CallbackQuery, state: FSMContext):
    if callback.data == "adb_skip_inst":
        await state.update_data(installment_current=None, installment_total=None)
    else:
        parts = callback.data.split(":", 1)[1].split("/")
        await state.update_data(installment_current=int(parts[0]), installment_total=int(parts[1]))
    await state.set_state(AddDebt.category)
    await callback.message.edit_text("Kategori?", reply_markup=category_keyboard())
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("adb_cat:") or c.data == "adb_skip_cat")
async def select_category(callback: CallbackQuery, state: FSMContext):
    if callback.data == "adb_skip_cat":
        category = None
    else:
        category = callback.data.split(":", 1)[1]
    await state.update_data(category=category)
    data = await state.get_data()
    summary = (
        f"📋 <b>Ringkasan:</b>\n"
        f"🏷 Platform: {data['platform']}\n"
        f"💰 Jumlah: Rp{data['amount']:,}\n"
        f"📅 Jatuh tempo: {data['due_date']}"
    )
    if data.get('installment_total'):
        summary += f"\n📊 Cicilan: {data['installment_current']}/{data['installment_total']}"
    if category:
        summary += f"\n📂 Kategori: {category}"
    summary += "\n\nSimpan?"
    await state.set_state(AddDebt.confirm)
    await callback.message.edit_text(summary, reply_markup=confirm_keyboard())
    await callback.answer()


@router.callback_query(lambda c: c.data == "adb_save")
async def save_debt(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        debt_data = DebtCreate(
            platform=data["platform"],
            amount=data["amount"],
            due_date=date.fromisoformat(data["due_date"]),
            installment_current=data.get("installment_current"),
            installment_total=data.get("installment_total"),
            category=data.get("category"),
        )
        async with async_session_factory() as session:
            user = await get_or_create_user(session, callback.from_user.id)
            debt = await create_debt(session, user.id, debt_data, source=DebtSource.manual)
        msg = f"✅ Utang tercatat!\n{debt.platform} — Rp{debt.amount:,}\nJatuh tempo: {debt.due_date}"
        await callback.message.edit_text(msg, reply_markup=debt_keyboard(debt.id))
        await callback.answer("Utang berhasil disimpan!")
    except Exception as e:
        await callback.message.edit_text(f"Gagal menyimpan: {e}")
        await callback.answer("Terjadi kesalahan.", show_alert=True)
    await state.clear()
