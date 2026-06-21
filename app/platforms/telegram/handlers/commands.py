import shlex
import uuid
from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.config import settings
from app.core.db import async_session_factory
from app.core.ratelimit import check_rate_limit
from app.core.auth import create_login_token
from app.models.debt import DebtSource, DebtStatus
from app.schemas.debt import DebtCreate
from app.services.debt_service import (
    get_or_create_user, create_debt, update_debt, update_user_wa,
    get_user_debts, get_user_debt_by_id,
    get_monthly_summary, get_upcoming_debts, delete_debt,
)
from app.services.payment_service import get_payments_for_debt
from app.services.platform_rate_service import get_platform_rate
from app.platforms.telegram.keyboards.inline import debt_keyboard

router = Router()


RATE_MSG = "⏳ Mohon tunggu sebelum menggunakan perintah lagi."


@router.message(Command("start"))
async def cmd_start(message: Message):
    if not check_rate_limit(message.from_user.id):
        await message.reply(RATE_MSG)
        return
    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
        debts = await get_user_debts(session, user.id)

    if debts:
        active = sum(1 for d in debts if d.status.value == "active")
        paid = sum(1 for d in debts if d.status.value == "paid")
        late = sum(1 for d in debts if d.status.value == "late")
        await message.reply(
            f"Selamat datang kembali di JatuhTempo Beta, {message.from_user.full_name}!\n\n"
            f"📊 Statistik utang Anda:\n"
            f"🟡 Aktif: {active}\n"
            f"✅ Lunas: {paid}\n"
            f"🔴 Terlambat: {late}\n"
            f"📋 Total: {len(debts)}\n\n"
            "Contoh penggunaan:\n"
            "📸 Kirim screenshot tagihan → otomatis terbaca\n"
            "➕ /add Kredivo 350000 2026-07-15\n"
            "📋 /debts --status active\n\n"
            "Perintah lainnya: /help"
        )
    else:
        await message.reply(
            "👋 Halo! Saya JatuhTempo Beta, asisten manajemen utang Anda.\n\n"
            "Mulai dengan cara termudah:\n\n"
            "📸 Kirim screenshot tagihan → AI baca otomatis\n"
            "➕ Atau ketik: /add Kredivo 350000 2026-07-15\n\n"
            "Contoh lain:\n"
            "/debts — Lihat daftar utang\n"
            "/summary — Ringkasan singkat\n\n"
            "Butuh bantuan? Ketik /help"
        )


@router.message(Command("help"))
async def cmd_help(message: Message):
    if not check_rate_limit(message.from_user.id):
        await message.reply(RATE_MSG)
        return
    await message.reply(
        "Berikut perintah yang bisa kamu gunakan:\n\n"
        "📸 <b>Kirim foto screenshot</b> — otomatis dibaca AI\n\n"
        "➕ <b>/add</b> — Tambah utang\n"
        "   Contoh: /add Kredivo 350000 2026-07-15\n"
        "   Opsional: /add ... --bunga 2.5 --bunga-type monthly\n\n"
        "📋 <b>/debts</b> — Lihat semua utang\n"
        "   Filter: /debts --status active\n\n"
        "✏️ <b>/edit</b> — Edit utang\n"
        "🗑 <b>/delete</b> — Hapus utang\n"
        "📜 <b>/history</b> — Riwayat pembayaran\n\n"
        "📊 <b>/monthly</b> — Rekap bulan ini\n"
        "🔜 <b>/upcoming</b> — Utang 30 hari ke depan\n"
        "📄 <b>/summary</b> — Ringkasan singkat\n\n"
        "🔑 <b>/login</b> — Login ke web dashboard\n"
        "📱 <b>/wa</b> — Atur nomor WhatsApp\n\n"
        "📖 <b>/faq</b> — Pertanyaan umum\n\n"
        "🌐 Butuh info lebih lengkap? Kunjungi:\n"
        "❓ FAQ: https://jatuhtempo.up.railway.app/faq\n"
        "📘 Dokumentasi: https://jatuhtempo.up.railway.app/docs\n"
        "⚖️ Syarat & Ketentuan: https://jatuhtempo.up.railway.app/legal/terms\n\n"
        "ID utang (8 karakter) bisa dilihat dari /debts"
    )





@router.message(Command("debts"))
async def cmd_debts(message: Message):
    if not check_rate_limit(message.from_user.id):
        await message.reply(RATE_MSG)
        return

    text = message.text.removeprefix("/debts").strip()
    status_filter = None
    platform_filter = None

    if text:
        try:
            parts = shlex.split(text)
        except ValueError:
            await message.reply("Format tidak valid.")
            return
        i = 0
        while i < len(parts):
            if parts[i] == "--status" and i + 1 < len(parts):
                val = parts[i + 1].lower()
                if val not in ("active", "paid", "late"):
                    await message.reply("Filter status: active, paid, atau late.")
                    return
                status_filter = DebtStatus(val)
                i += 2
            elif parts[i] == "--platform" and i + 1 < len(parts):
                platform_filter = parts[i + 1]
                i += 2
            else:
                i += 1

    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
        debts = await get_user_debts(session, user.id, status=status_filter, platform=platform_filter)

    if not debts:
        msg = "Tidak ada utang"
        if status_filter or platform_filter:
            msg += " dengan filter tersebut"
        await message.reply(msg + ".")
        return

    title = "<b>Daftar Utang</b>"
    if status_filter:
        title += f" — {status_filter.value}"
    if platform_filter:
        title += f" — {platform_filter}"
    lines = [title + "\n"]

    for d in debts:
        status_emoji = {"active": "🟡", "paid": "✅", "late": "🔴"}
        short_id = str(d.id)[:8]
        cicilan = f" ({d.installment_current}/{d.installment_total})" if d.installment_current and d.installment_total else ""
        bunga = ""
        if d.interest_rate:
            bunga_type = {"daily": "/hari", "monthly": "/bln", "yearly": "/thn", "flat": "/flat"}.get(d.interest_type, "")
            bunga = f" | {d.interest_rate}%{bunga_type}"
        extra = ""
        if d.category:
            extra += f" | {d.category}"
        if d.notes:
            extra += f"\n   📝 {d.notes}"
        lines.append(
            f"{status_emoji.get(d.status.value, '⚪')} <b>{d.platform}</b>{cicilan}{bunga}\n"
            f"   Rp{d.amount:,} | Jatuh tempo: {d.due_date}\n"
            f"   ID: <code>{short_id}</code> | {d.status.value}{extra}"
        )
    await message.reply("\n".join(lines))


@router.message(Command("monthly"))
async def cmd_monthly(message: Message):
    if not check_rate_limit(message.from_user.id):
        await message.reply(RATE_MSG)
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
        bunga = ""
        if d.interest_rate:
            bunga_type = {"daily": "/hari", "monthly": "/bln", "yearly": "/thn", "flat": "/flat"}.get(d.interest_type, "")
            bunga = f" {d.interest_rate}%{bunga_type}"
        lines.append(f"• {d.platform}{cicilan}{bunga} Rp{d.amount:,} ({d.due_date})")

    await message.reply("\n".join(lines))


@router.message(Command("upcoming"))
async def cmd_upcoming(message: Message):
    if not check_rate_limit(message.from_user.id):
        await message.reply(RATE_MSG)
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
        bunga = ""
        if d.interest_rate:
            bunga_type = {"daily": "/hari", "monthly": "/bln", "yearly": "/thn", "flat": "/flat"}.get(d.interest_type, "")
            bunga = f" {d.interest_rate}%{bunga_type}"
        lines.append(f"• {d.platform}{cicilan}{bunga} Rp{d.amount:,} — {d.due_date}")
    await message.reply("\n".join(lines))


@router.message(Command("summary"))
async def cmd_summary(message: Message):
    if not check_rate_limit(message.from_user.id):
        await message.reply(RATE_MSG)
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
        await message.reply(RATE_MSG)
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "🗑 Hapus utang\n\n"
            "Ketik: /delete <id>\n"
            "ID bisa dilihat dari /debts (8 karakter).\n\n"
            "Contoh: /delete a1b2c3d4"
        )
        return

    raw_id = args[1].strip()

    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)

        try:
            debt_id = uuid.UUID(raw_id)
        except ValueError:
            debts = await get_user_debts(session, user.id)
            matched = [d for d in debts if str(d.id).startswith(raw_id)]
            if len(matched) == 0:
                await message.reply("ID tidak ditemukan. Gunakan /debts untuk melihat ID utang.")
                return
            if len(matched) > 1:
                await message.reply(f"Ditemukan {len(matched)} utang dengan ID '{raw_id}'. Gunakan ID yang lebih spesifik.")
                return
            debt_id = matched[0].id

        deleted = await delete_debt(session, debt_id, user.id)

    if deleted:
        await message.reply("Utang berhasil dihapus.")
    else:
        await message.reply("Utang tidak ditemukan atau bukan milik Anda.")


@router.message(Command("edit"))
async def cmd_edit(message: Message):
    if not check_rate_limit(message.from_user.id):
        await message.reply(RATE_MSG)
        return
    text = message.text.removeprefix("/edit").strip()
    if not text:
        await message.reply(
            "✏️ Edit utang\n\n"
            "Ketik: /edit <id> [--amount N] [--due_date YYYY-MM-DD] [--status paid/late]\n\n"
            "Contoh: /edit a1b2c3d4 --amount 250000 --status paid\n\n"
            "Semua field bisa diedit:\n"
            "--amount, --due_date, --platform, --status\n"
            "--cicilan, --kategori, --notes\n"
            "--bunga, --bunga-type\n\n"
            "ID bisa dilihat dari /debts (8 karakter)"
        )
        return

    try:
        parts = shlex.split(text)
    except ValueError:
        await message.reply("Format tidak valid. Periksa tanda kutip.")
        return

    raw_id = parts[0]
    rest = parts[1:]

    if not rest:
        await message.reply("Tidak ada field yang diubah. Lihat panduan /edit.")
        return

    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)

        try:
            debt_id = uuid.UUID(raw_id)
        except ValueError:
            debts = await get_user_debts(session, user.id)
            matched = [d for d in debts if str(d.id).startswith(raw_id)]
            if len(matched) == 0:
                await message.reply("ID tidak ditemukan. Gunakan /debts untuk melihat ID.")
                return
            if len(matched) > 1:
                await message.reply(f"Ditemukan {len(matched)} utang. Gunakan ID yang lebih spesifik.")
                return
            debt_id = matched[0].id

        debt = await get_user_debt_by_id(session, debt_id, user.id)
        if not debt:
            await message.reply("Utang tidak ditemukan atau bukan milik Anda.")
            return

        update_kwargs = {}
        changed = []
        i = 0
        while i < len(rest):
            if rest[i] == "--amount" and i + 1 < len(rest):
                try:
                    update_kwargs["amount"] = int(rest[i + 1])
                    changed.append(f"jumlah → Rp{update_kwargs['amount']:,}")
                except ValueError:
                    await message.reply("Jumlah harus angka.")
                    return
                i += 2
            elif rest[i] == "--due_date" and i + 1 < len(rest):
                try:
                    update_kwargs["due_date"] = date.fromisoformat(rest[i + 1])
                    changed.append(f"jatuh tempo → {update_kwargs['due_date']}")
                except ValueError:
                    await message.reply("Tanggal harus format YYYY-MM-DD.")
                    return
                i += 2
            elif rest[i] == "--platform" and i + 1 < len(rest):
                update_kwargs["platform"] = rest[i + 1]
                changed.append(f"platform → {update_kwargs['platform']}")
                i += 2
            elif rest[i] == "--status" and i + 1 < len(rest):
                val = rest[i + 1].lower()
                if val not in ("active", "paid", "late"):
                    await message.reply("Status harus: active, paid, atau late.")
                    return
                update_kwargs["status"] = DebtStatus(val)
                changed.append(f"status → {val}")
                i += 2
            elif rest[i] == "--cicilan" and i + 1 < len(rest):
                cicilan = rest[i + 1]
                if cicilan.lower() == "hapus":
                    update_kwargs["installment_current"] = None
                    update_kwargs["installment_total"] = None
                    changed.append("cicilan dihapus")
                elif "/" in cicilan:
                    try:
                        update_kwargs["installment_current"] = int(cicilan.split("/")[0])
                        update_kwargs["installment_total"] = int(cicilan.split("/")[1])
                        changed.append(f"cicilan → {cicilan}")
                    except ValueError:
                        await message.reply("Format cicilan harus X/Y, contoh: --cicilan 3/12")
                        return
                else:
                    await message.reply("Format cicilan harus X/Y atau 'hapus'.")
                    return
                i += 2
            elif rest[i] == "--kategori" and i + 1 < len(rest):
                val = rest[i + 1]
                if val.lower() == "hapus":
                    update_kwargs["category"] = None
                    changed.append("kategori dihapus")
                else:
                    update_kwargs["category"] = val
                    changed.append(f"kategori → {val}")
                i += 2
            elif rest[i] == "--notes" and i + 1 < len(rest):
                val = rest[i + 1]
                if val.lower() == "hapus":
                    update_kwargs["notes"] = None
                    changed.append("catatan dihapus")
                else:
                    update_kwargs["notes"] = val
                    changed.append(f"catatan → {val}")
                i += 2
            elif rest[i] == "--bunga" and i + 1 < len(rest):
                val = rest[i + 1]
                if val.lower() == "hapus":
                    update_kwargs["interest_rate"] = None
                    changed.append("bunga dihapus")
                else:
                    try:
                        update_kwargs["interest_rate"] = float(val)
                        changed.append(f"bunga → {val}%")
                    except ValueError:
                        await message.reply("Bunga harus angka, contoh: --bunga 2.5")
                        return
                i += 2
            elif rest[i] == "--bunga-type" and i + 1 < len(rest):
                val = rest[i + 1]
                if val.lower() == "hapus":
                    update_kwargs["interest_type"] = None
                    changed.append("tipe bunga dihapus")
                elif val.lower() in ("daily", "monthly", "yearly", "flat"):
                    update_kwargs["interest_type"] = val.lower()
                    changed.append(f"tipe bunga → {val}")
                else:
                    await message.reply("Tipe bunga: daily, monthly, yearly, flat, atau 'hapus'.")
                    return
                i += 2
            else:
                i += 1

        if not update_kwargs:
            await message.reply("Tidak ada field valid yang diubah.")
            return

        updated = await update_debt(session, debt_id, user.id, **update_kwargs)

    if updated:
        msg = "✅ <b>Utang diperbarui:</b>\n" + "\n".join(f"• {c}" for c in changed)
        await message.reply(msg, reply_markup=debt_keyboard(updated.id))
    else:
        await message.reply("Gagal memperbarui utang.")


@router.message(Command("history"))
async def cmd_history(message: Message):
    if not check_rate_limit(message.from_user.id):
        await message.reply(RATE_MSG)
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Gunakan: /history <id>\n\nID bisa dilihat dari /debts.")
        return

    raw_id = args[1].strip()

    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)

        try:
            debt_id = uuid.UUID(raw_id)
        except ValueError:
            debts = await get_user_debts(session, user.id)
            matched = [d for d in debts if str(d.id).startswith(raw_id)]
            if len(matched) == 0:
                await message.reply("ID tidak ditemukan.")
                return
            if len(matched) > 1:
                await message.reply("Gunakan ID yang lebih spesifik.")
                return
            debt_id = matched[0].id

        debt = await get_user_debt_by_id(session, debt_id, user.id)
        if not debt:
            await message.reply("Utang tidak ditemukan.")
            return

        payments = await get_payments_for_debt(session, debt_id, user.id)

    header = (
        f"<b>Riwayat Pembayaran</b>\n"
        f"{debt.platform} — Rp{debt.amount:,}\n"
        f"Status: {debt.status.value}\n\n"
    )

    if not payments:
        await message.reply(header + "Belum ada pembayaran tercatat.")
        return

    lines = [header]
    total_paid = 0
    for p in payments:
        total_paid += p.amount_paid
        note = f" — {p.notes}" if p.notes else ""
        lines.append(
            f"✓ Rp{p.amount_paid:,} — {p.paid_at.strftime('%d %b %Y %H:%M')}{note}"
        )

    remaining = debt.amount - total_paid
    lines.append(f"\n<b>Total dibayar:</b> Rp{total_paid:,}")
    if remaining > 0 and debt.status.value != "paid":
        lines.append(f"<b>Sisa:</b> Rp{remaining:,}")

    await message.reply("\n".join(lines))


@router.message(Command("login"))
async def cmd_login(message: Message):
    if not check_rate_limit(message.from_user.id):
        await message.reply(RATE_MSG)
        return
    token = create_login_token(message.from_user.id)
    link = f"{settings.web_url}/login?token={token}"
    await message.reply(
        f"🔑 <b>Akses Web Dashboard</b>\n\n"
        f"Klik link ini untuk masuk ke dashboard:\n"
        f"{link}\n\n"
        f"Link berlaku 5 menit. Kalo sudah punya akun web, ini akan menautkan akun Telegram kamu."
    )


@router.message(Command("wa"))
async def cmd_wa(message: Message):
    if not check_rate_limit(message.from_user.id):
        await message.reply(RATE_MSG)
        return
    text = message.text.removeprefix("/wa").strip()
    async with async_session_factory() as session:
        if not text:
            user = await get_or_create_user(session, message.from_user.id)
            if user.phone_number:
                await message.reply(
                    f"📱 Nomor WA Anda: {user.phone_number}\n"
                    f"Gunakan /wa hapus untuk menghapus."
                )
            else:
                await message.reply(
                    "Gunakan: /wa <nomor>\n"
                    "Contoh: /wa 08123456789\n\n"
                    "Nomor akan digunakan untuk pengingat via WhatsApp."
                )
            return

        if text.lower() == "hapus":
            await update_user_wa(session, message.from_user.id, phone_number="")
            await message.reply("Nomor WhatsApp berhasil dihapus.")
            return

    import re
    digits = re.sub(r"\D", "", text)
    if not digits.startswith("0") or len(digits) < 10:
        await message.reply("Nomor tidak valid. Gunakan format: 08123456789")
        return
    formatted = f"+62{digits[1:]}"

    async with async_session_factory() as session:
        await update_user_wa(session, message.from_user.id, phone_number=formatted)
    await message.reply(f"✅ Nomor WhatsApp tersimpan: {formatted}")


@router.message(Command("strategy"))
async def cmd_strategy(message: Message):
    if not check_rate_limit(message.from_user.id):
        await message.reply(RATE_MSG)
        return
    async with async_session_factory() as session:
        user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
        debts = await get_user_debts(session, user.id, status=DebtStatus.active)

    if not debts:
        await message.reply("Tidak ada utang aktif. Tambah dulu dengan /add.")
        return

    # Snowball order: sort by amount ascending
    sorted_debts = sorted(debts, key=lambda d: d.amount)

    total_debt = sum(d.amount for d in sorted_debts)

    # Estimate monthly payment per debt
    total_monthly = 0
    for d in sorted_debts:
        if d.installment_total and d.installment_total > 0:
            total_monthly += d.amount // d.installment_total
        else:
            total_monthly += d.amount

    lines = [
        "<b>📊 Strategi Snowball</b>\n",
        "Urutan lunasi (dari terkecil ke terbesar):\n",
    ]

    for i, d in enumerate(sorted_debts, 1):
        cicilan = f" ({d.installment_current}/{d.installment_total})" if d.installment_current and d.installment_total else ""
        monthly_est = ""
        if d.installment_total and d.installment_total > 0:
            monthly_est = f" ~Rp{d.amount // d.installment_total:,}/bln"
        lines.append(
            f"{i}. <b>{d.platform}</b>{cicilan}\n"
            f"   Rp{d.amount:,}{monthly_est} | Jatuh tempo: {d.due_date}"
        )

    lines.extend([
        "",
        f"<b>Total utang:</b> Rp{total_debt:,}",
        f"<b>Estimasi total per bulan:</b> Rp{total_monthly:,}",
        "",
        "💡 <b>Tips:</b> Lunasi urutan 1 dulu sambil bayar minimum sisanya.",
        "",
        "🔗 Untuk simulasi lengkap (extra payment, income-based):",
        "👉 https://jatuhtempo.up.railway.app/strategy",
    ])

    await message.reply("\n".join(lines))
