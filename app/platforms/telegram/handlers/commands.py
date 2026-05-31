import shlex
from datetime import date, datetime, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.db import async_session_factory
from app.core.ratelimit import check_rate_limit
from app.schemas.debt import DebtCreate
from app.services.debt_service import get_or_create_user, create_debt, get_user_debts, get_monthly_summary, get_upcoming_debts, delete_debt
from app.models.debt import DebtSource
from app.platforms.telegram.keyboards.inline import debt_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    if not check_rate_limit(message.from_user.id):
        return
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
    if not check_rate_limit(message.from_user.id):
        return
    await message.reply(
        "Perintah yang tersedia:\n"
        "/start - Mulai bot\n"
        "/help - Bantuan ini\n"
        "/add - Tambah utang baru\n"
        "/debts - Lihat daftar utang\n"
        "/monthly - Rekap bulan ini\n"
        "/upcoming - Utang 30 hari ke depan\n"
        "/summary - Ringkasan singkat\n"
        "/delete <id> - Hapus utang\n\n"
        "Atau kirim screenshot tagihan untuk parsing otomatis."
    )


@router.message(Command("add"))
async def cmd_add(message: Message):
    if not check_rate_limit(message.from_user.id):
        return
    text = message.text.removeprefix("/add").strip()
    if not text:
        await message.reply(
            "Gunakan format:\n"
            "/add <platform> <amount> <YYYY-MM-DD> [--cicilan X/Y] [--kategori <kat>] [--notes <catatan>]\n\n"
            "Contoh: /add Akulaku 500000 2026-06-15 --cicilan 3/12 --kategori pinjol"
        )
        return

    try:
        parts = shlex.split(text)
    except ValueError:
        await message.reply("Format tidak valid. Periksa tanda kutip.")
        return

    if len(parts) < 3:
        await message.reply(
            "Format tidak lengkap. Minimal: /add <platform> <amount> <YYYY-MM-DD>"
        )
        return

    platform = parts[0]
    try:
        amount = int(parts[1])
    except ValueError:
        await message.reply("Jumlah harus angka.")
        return

    try:
        due_date = date.fromisoformat(parts[2])
    except ValueError:
        await message.reply("Tanggal harus format YYYY-MM-DD.")
        return

    installment_current = None
    installment_total = None
    category = None
    notes = None

    i = 3
    while i < len(parts):
        if parts[i] == "--cicilan" and i + 1 < len(parts):
            cicilan = parts[i + 1]
            if "/" in cicilan:
                try:
                    installment_current = int(cicilan.split("/")[0])
                    installment_total = int(cicilan.split("/")[1])
                except ValueError:
                    await message.reply("Format cicilan harus X/Y, contoh: --cicilan 3/12")
                    return
            i += 2
        elif parts[i] == "--kategori" and i + 1 < len(parts):
            category = parts[i + 1]
            i += 2
        elif parts[i] == "--notes" and i + 1 < len(parts):
            notes = parts[i + 1]
            i += 2
        else:
            i += 1

    data = DebtCreate(
        platform=platform,
        amount=amount,
        due_date=due_date,
        installment_current=installment_current,
        installment_total=installment_total,
        category=category,
        notes=notes,
    )

    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
        debt = await create_debt(session, user.id, data, source=DebtSource.manual)

    msg = (
        f"Utang tercatat!\n"
        f"Platform: {debt.platform}\n"
        f"Jumlah: Rp{debt.amount:,}\n"
        f"Jatuh tempo: {debt.due_date}"
    )
    if debt.installment_current and debt.installment_total:
        msg += f"\nCicilan: {debt.installment_current}/{debt.installment_total}"
    if debt.category:
        msg += f"\nKategori: {debt.category}"
    if debt.notes:
        msg += f"\nCatatan: {debt.notes}"

    await message.reply(msg, reply_markup=debt_keyboard(debt.id))


@router.message(Command("debts"))
async def cmd_debts(message: Message):
    if not check_rate_limit(message.from_user.id):
        return
    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
        debts = await get_user_debts(session, user.id)

    if not debts:
        await message.reply("Belum ada utang tercatat.")
        return

    lines = ["<b>Daftar Utang:</b>\n"]
    for d in debts:
        status_emoji = {"active": "🟡", "paid": "✅", "late": "🔴"}
        cicilan = f" ({d.installment_current}/{d.installment_total})" if d.installment_current and d.installment_total else ""
        lines.append(
            f"{status_emoji.get(d.status.value, '⚪')} <b>{d.platform}</b>{cicilan}\n"
            f"   Rp{d.amount:,} | Jatuh tempo: {d.due_date}\n"
            f"   Status: {d.status.value}"
        )
    await message.reply("\n".join(lines))


@router.message(Command("monthly"))
async def cmd_monthly(message: Message):
    if not check_rate_limit(message.from_user.id):
        return
    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
        summary = await get_monthly_summary(session, user.id)

    lines = [
        "<b>Rekap Bulan Ini:</b>\n",
        f"🟡 Utang aktif: {summary.total_active} (Rp{summary.total_amount:,})",
        f"✅ Lunas bulan ini: {summary.paid_this_month} (Rp{summary.paid_amount:,})",
        "",
        "<b>Mendatang:</b>",
    ]
    for d in summary.upcoming[:10]:
        cicilan = f" ({d.installment_current}/{d.installment_total})" if d.installment_current and d.installment_total else ""
        lines.append(f"• {d.platform}{cicilan} Rp{d.amount:,} ({d.due_date})")

    await message.reply("\n".join(lines))


@router.message(Command("upcoming"))
async def cmd_upcoming(message: Message):
    if not check_rate_limit(message.from_user.id):
        return
    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
        debts = await get_upcoming_debts(session, user.id)

    if not debts:
        await message.reply("Tidak ada utang mendatang dalam 30 hari.")
        return

    lines = ["<b>Utang Mendatang (30 hari):</b>\n"]
    for d in debts:
        cicilan = f" ({d.installment_current}/{d.installment_total})" if d.installment_current and d.installment_total else ""
        lines.append(f"• {d.platform}{cicilan} Rp{d.amount:,} — {d.due_date}")
    await message.reply("\n".join(lines))


@router.message(Command("summary"))
async def cmd_summary(message: Message):
    if not check_rate_limit(message.from_user.id):
        return
    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
        summary = await get_monthly_summary(session, user.id)

    await message.reply(
        f"<b>Ringkasan:</b>\n"
        f"🟡 Aktif: {summary.total_active} (Rp{summary.total_amount:,})\n"
        f"✅ Lunas bulan ini: {summary.paid_this_month}\n"
        f"🔜 Mendatang: {len(summary.upcoming)} tagihan"
    )


@router.message(Command("delete"))
async def cmd_delete(message: Message):
    if not check_rate_limit(message.from_user.id):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Gunakan: /delete <id_utang>\n\nID utang bisa dilihat dari /debts.")
        return

    import uuid
    try:
        debt_id = uuid.UUID(args[1].strip())
    except ValueError:
        await message.reply("ID utang tidak valid. Gunakan UUID yang benar.")
        return

    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
        deleted = await delete_debt(session, debt_id, user.id)

    if deleted:
        await message.reply("Utang berhasil dihapus.")
    else:
        await message.reply("Utang tidak ditemukan atau bukan milik Anda.")
