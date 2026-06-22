import logging
import uuid
from datetime import date, datetime, timezone

from aiogram import Router, F
from aiogram.types import Message

from app.core.config import settings
from app.core.db import async_session_factory
from app.core.ratelimit import check_rate_limit
from app.core.temp_store import store_ocr
from app.models.debt import Debt
from app.services.ai_parser import parse_debt_from_text
from app.services.debt_service import get_or_create_user
from app.services.ocr_service import ocr_image
from app.platforms.telegram.keyboards.inline import confirm_keyboard
from sqlalchemy import select, func

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.photo)
async def handle_photo(message: Message):
    if not check_rate_limit(message.from_user.id, cooldown=3.0):
        await message.reply("⏳ Mohon tunggu 3 detik antar foto.")
        return

    processing_msg = await message.reply("Memproses screenshot...")

    try:
        # OCR limit check for free users
        async with async_session_factory() as session:
            user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)
            if user.subscription_status != "pro":
                today = date.today()
                start_month = today.replace(day=1)
                count_q = await session.execute(
                    select(func.count()).where(
                        Debt.user_id == user.id,
                        Debt.source == "screenshot",
                        Debt.created_at >= start_month,
                    )
                )
                monthly_count = count_q.scalar() or 0
                if monthly_count >= 5:
                    await processing_msg.edit_text(
                        "📸 Batas scan tagihan gratis bulan ini sudah habis (5x).\n\n"
                        "Upgrade ke Pro untuk scan unlimited:\n"
                        "➡️ Buka web dashboard → Pengaturan → Upgrade"
                    )
                    return

        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)

        max_bytes = settings.max_image_size_mb * 1024 * 1024
        if file.file_size and file.file_size > max_bytes:
            await processing_msg.edit_text(
                f"Gambar terlalu besar (maks {settings.max_image_size_mb}MB). "
                "Kirim gambar dengan resolusi lebih rendah."
            )
            return

        media_dir = Path(settings.media_dir)
        media_dir.mkdir(parents=True, exist_ok=True)
        image_path = media_dir / f"{uuid.uuid4()}.jpg"

        await message.bot.download_file(file.file_path, image_path)

        raw_text = await ocr_image(image_path)

        if not raw_text or len(raw_text) < 20:
            await processing_msg.edit_text(
                "Tidak bisa membaca teks dari gambar. "
                "Pastikan gambar tagihan cukup jelas dan gunakan /add untuk input manual."
            )
            try:
                image_path.unlink()
            except OSError:
                pass
            return

        parsed = await parse_debt_from_text(raw_text)

        warnings = []
        if parsed.get("amount") is None:
            warnings.append("Jumlah tidak terbaca")
        if parsed.get("platform") is None:
            warnings.append("Platform tidak terdeteksi")
        if parsed.get("due_date") == str(date.today()):
            warnings.append("Tanggal jatuh tempo fallback ke hari ini (gagal terbaca)")

        amt = parsed.get("amount")
        amt_str = f"Rp{amt:,}" if amt is not None else "?"
        preview = (
            f"📋 <b>Preview Hasil OCR:</b>\n"
            f"🏷 Platform: {parsed.get('platform') or '?'}\n"
            f"💰 Jumlah: {amt_str}\n"
            f"📅 Jatuh tempo: {parsed.get('due_date', '?')}"
        )
        cicilan = ""
        if parsed.get("installment_current") and parsed.get("installment_total"):
            cicilan = f"\n📊 Cicilan: {parsed['installment_current']}/{parsed['installment_total']}"
        kategori = f"\n📂 Kategori: {parsed['category']}" if parsed.get("category") else ""
        preview += cicilan + kategori

        if warnings:
            preview += "\n\n⚠️ <b>Peringatan:</b>\n" + "\n".join(f"• {w}" for w in warnings)

        preview += "\n\nSimpan data ini?"

        store_ocr(message.from_user.id, {
            "parsed": parsed,
            "raw_text": raw_text,
            "image_path": str(image_path),
        })

        await processing_msg.edit_text(preview, reply_markup=confirm_keyboard())

    except Exception:
        logger.exception("Failed to process screenshot")
        await processing_msg.edit_text("Gagal memproses screenshot. Pastikan gambar berisi tagihan yang jelas.")
