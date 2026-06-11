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
    interest_rate = State()
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


def interest_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Per bulan (monthly)", callback_data="adb_int_type:monthly")],
        [InlineKeyboardButton(text="📊 Per hari (daily)", callback_data="adb_int_type:daily")],
        [InlineKeyboardButton(text="📊 Per tahun (yearly)", callback_data="adb_int_type:yearly")],
        [InlineKeyboardButton(text="📊 Flat", callback_data="adb_int_type:flat")],
        [InlineKeyboardButton(text="⏭ Tidak ada bunga", callback_data="adb_int_type:none")],
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
            # Structured parse failed — try NL AI parsing
            try:
                import uuid as _uuid
                from app.services.ai_parser import parse_debt_from_text
                from app.core.temp_store import store_temp
                from app.platforms.telegram.keyboards.inline import confirm_nl_keyboard

                parsed = await parse_debt_from_text(text)
                temp_key = str(_uuid.uuid4())
                store_temp(temp_key, {"parsed": parsed, "user_id": message.from_user.id})

                lines = ["📋 <b>Hasil parsing AI:</b>\n"]
                if parsed.get("platform"):
                    lines.append(f"🏦 Platform: {parsed['platform']}")
                if parsed.get("amount"):
                    lines.append(f"💰 Jumlah: Rp{parsed['amount']:,}")
                if parsed.get("due_date"):
                    lines.append(f"📅 Jatuh tempo: {parsed['due_date']}")
                if parsed.get("installment_current") and parsed.get("installment_total"):
                    lines.append(f"🔄 Cicilan: {parsed['installment_current']}/{parsed['installment_total']}")
                if parsed.get("interest_rate"):
                    bunga_type = {"daily": "/hari", "monthly": "/bln", "yearly": "/thn", "flat": "/flat"}
                    suffix = bunga_type.get(parsed.get("interest_type"), "")
                    lines.append(f"📊 Bunga: {parsed['interest_rate']}%{suffix}")
                if parsed.get("category"):
                    lines.append(f"🏷️ Kategori: {parsed['category']}")
                lines.append("\nSimpan data ini?")

                await message.reply("\n".join(lines), reply_markup=confirm_nl_keyboard(temp_key))
                return
            except Exception:
                pass  # Fall through to FSM wizard

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
    await state.set_state(AddDebt.interest_rate)
    await callback.message.edit_text(
        f"Kategori: {category or '−'}\n\n"
        "Berapa bunganya? Ketik angka persen, atau ketik 'tidak ada'.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏭ Tidak ada bunga", callback_data="adb_int_rate:none")],
            [InlineKeyboardButton(text="❌ Batal", callback_data="adb_cancel")],
        ])
    )
    await callback.answer()


def _build_summary(data: dict) -> str:
    lines = ["📋 <b>Ringkasan:</b>"]
    lines.append(f"🏷 Platform: {data.get('platform', '−')}")
    if data.get("amount"):
        lines.append(f"💰 Jumlah: Rp{data['amount']:,}")
    lines.append(f"📅 Jatuh tempo: {data.get('due_date', '−')}")
    if data.get("installment_total"):
        lines.append(f"📊 Cicilan: {data['installment_current']}/{data['installment_total']}")
    if data.get("category"):
        lines.append(f"📂 Kategori: {data['category']}")
    if data.get("interest_rate") is not None:
        bunga_type = {"daily": "/hari", "monthly": "/bln", "yearly": "/thn", "flat": "/flat"}
        suffix = bunga_type.get(data.get("interest_type"), "")
        lines.append(f"📊 Bunga: {data['interest_rate']}%{suffix}")
    elif data.get("interest_skipped"):
        lines.append(f"📊 Bunga: Tidak ada")
    lines.append("\nSimpan?")
    return "\n".join(lines)


@router.message(AddDebt.interest_rate)
async def input_interest_rate(message: Message, state: FSMContext):
    text = message.text.strip().lower()
    if text in ("tidak ada", "0", "0.0", "none", "no", "n"):
        await state.update_data(interest_rate=None, interest_type=None, interest_skipped=True)
        data = await state.get_data()
        await state.set_state(AddDebt.confirm)
        await message.reply(_build_summary(data), reply_markup=confirm_keyboard())
        return
    try:
        rate = float(text.replace(",", "."))
        if rate < 0:
            raise ValueError
    except ValueError:
        await message.reply("Masukkan angka persen yang valid, atau ketik 'tidak ada'.")
        return
    await state.update_data(interest_rate=rate)
    await state.set_state(AddDebt.interest_rate)
    await message.reply(
        f"Bunga: {rate}%\n\n"
        "Jenis bunga?",
        reply_markup=interest_type_keyboard(),
    )


@router.callback_query(lambda c: c.data == "adb_int_rate:none")
async def skip_interest_rate(callback: CallbackQuery, state: FSMContext):
    await state.update_data(interest_rate=None, interest_type=None, interest_skipped=True)
    data = await state.get_data()
    await state.set_state(AddDebt.confirm)
    await callback.message.edit_text(_build_summary(data), reply_markup=confirm_keyboard())
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("adb_int_type:"))
async def select_interest_type(callback: CallbackQuery, state: FSMContext):
    int_type = callback.data.split(":", 1)[1]
    if int_type == "none":
        await state.update_data(interest_rate=None, interest_type=None, interest_skipped=True)
    else:
        await state.update_data(interest_type=int_type, interest_skipped=False)
    data = await state.get_data()
    await state.set_state(AddDebt.confirm)
    await callback.message.edit_text(_build_summary(data), reply_markup=confirm_keyboard())
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
            interest_rate=data.get("interest_rate"),
            interest_type=data.get("interest_type"),
        )
        async with async_session_factory() as session:
            user = await get_or_create_user(session, callback.from_user.id)
            debt = await create_debt(session, user.id, debt_data, source=DebtSource.manual)
        msg = f"✅ Utang tercatat!\n{debt.platform} — Rp{debt.amount:,}\nJatuh tempo: {debt.due_date}"
        if debt.installment_current and debt.installment_total:
            msg += f"\nCicilan: {debt.installment_current}/{debt.installment_total}"
        if debt.interest_rate:
            bunga_type = {"daily": "/hari", "monthly": "/bln", "yearly": "/thn", "flat": "/flat"}.get(debt.interest_type, "")
            msg += f"\nBunga: {debt.interest_rate}%{bunga_type}"
        if debt.category:
            msg += f"\nKategori: {debt.category}"
        await callback.message.edit_text(msg, reply_markup=debt_keyboard(debt.id))
        await callback.answer("Utang berhasil disimpan!")
    except Exception as e:
        await callback.message.edit_text(f"Gagal menyimpan: {e}")
        await callback.answer("Terjadi kesalahan.", show_alert=True)
    await state.clear()
