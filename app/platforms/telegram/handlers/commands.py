from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.db import async_session_factory
from app.schemas.debt import DebtCreate
from app.services.debt_service import get_or_create_user, create_debt, get_user_debts, get_monthly_summary, get_upcoming_debts
from app.models.debt import DebtSource
from app.platforms.telegram.keyboards.inline import debt_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    async with async_session_factory() as session:
        await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
    await message.reply(
        "Halo! Saya JatuhTempo, asisten manajemen utang Anda.\n\n"
        "Kirim screenshot tagihan atau gunakan perintah:\n"
        "/add - Tambah utang manual\n"
        "/debts - Lihat semua utang\n"
        "/monthly - Rekap bulan ini\n"
        "/upcoming - Utang mendatang\n"
        "/summary - Ringkasan singkat"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Perintah yang tersedia:\n"
        "/start - Mulai bot\n"
        "/help - Bantuan ini\n"
        "/add - Tambah utang baru\n"
        "/debts - Lihat daftar utang\n"
        "/monthly - Rekap bulan ini\n"
        "/upcoming - Utang 30 hari ke depan\n"
        "/summary - Ringkasan singkat\n\n"
        "Atau kirim screenshot tagihan untuk parsing otomatis."
    )


@router.message(Command("add"))
async def cmd_add(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "Gunakan format:\n/add [platform] [amount] [due_date YYYY-MM-DD]\n\n"
            "Contoh: /add Akulaku 500000 2026-06-15"
        )
        return

    parts = args[1].split()
    if len(parts) < 3:
        await message.reply("Format tidak lengkap. Gunakan: /add [platform] [amount] [YYYY-MM-DD]")
        return

    platform = parts[0]
    try:
        amount = int(parts[1])
    except ValueError:
        await message.reply("Jumlah harus angka.")
        return

    from datetime import date
    try:
        due_date = date.fromisoformat(parts[2])
    except ValueError:
        await message.reply("Tanggal harus format YYYY-MM-DD.")
        return

    data = DebtCreate(platform=platform, amount=amount, due_date=due_date)

    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
        debt = await create_debt(session, user.id, data, source=DebtSource.manual)

    await message.reply(
        f"Utang tercatat!\n"
        f"Platform: {debt.platform}\n"
        f"Jumlah: Rp{debt.amount:,}\n"
        f"Jatuh tempo: {debt.due_date}",
        reply_markup=debt_keyboard(debt.id),
    )


@router.message(Command("debts"))
async def cmd_debts(message: Message):
    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
        debts = await get_user_debts(session, user.id)

    if not debts:
        await message.reply("Belum ada utang tercatat.")
        return

    lines = ["<b>Daftar Utang:</b>\n"]
    for d in debts:
        status_emoji = {"active": "🟡", "paid": "✅", "late": "🔴"}
        lines.append(
            f"{status_emoji.get(d.status.value, '⚪')} <b>{d.platform}</b>\n"
            f"   Rp{d.amount:,} | Jatuh tempo: {d.due_date}\n"
            f"   Status: {d.status.value}"
        )
    await message.reply("\n".join(lines))


@router.message(Command("monthly"))
async def cmd_monthly(message: Message):
    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
        summary = await get_monthly_summary(session, user.id)

    lines = [
        "<b>Rekap Bulan Ini:</b>\n",
        f"Utang aktif: {summary.total_active} ({summary.total_amount:,})",
        f"Lunas bulan ini: {summary.paid_this_month} (Rp{summary.paid_amount:,})",
        "",
        "<b>Mendatang:</b>",
    ]
    for d in summary.upcoming[:10]:
        lines.append(f"• {d.platform} Rp{d.amount:,} ({d.due_date})")

    await message.reply("\n".join(lines))


@router.message(Command("upcoming"))
async def cmd_upcoming(message: Message):
    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
        debts = await get_upcoming_debts(session, user.id)

    if not debts:
        await message.reply("Tidak ada utang mendatang dalam 30 hari.")
        return

    lines = ["<b>Utang Mendatang (30 hari):</b>\n"]
    for d in debts:
        lines.append(f"• {d.platform} Rp{d.amount:,} — {d.due_date}")
    await message.reply("\n".join(lines))


@router.message(Command("summary"))
async def cmd_summary(message: Message):
    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
        summary = await get_monthly_summary(session, user.id)

    await message.reply(
        f"Ringkasan:\n"
        f"🟡 Aktif: {summary.total_active} (Rp{summary.total_amount:,})\n"
        f"✅ Lunas bulan ini: {summary.paid_this_month}\n"
        f"🔜 Mendatang: {len(summary.upcoming)} tagihan"
    )
