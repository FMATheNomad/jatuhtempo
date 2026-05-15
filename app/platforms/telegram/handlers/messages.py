import logging
import uuid
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile

from app.core.config import settings
from app.core.db import async_session_factory
from app.models.debt import DebtSource
from app.models.ocr_log import OcrLog
from app.schemas.debt import DebtCreate
from app.services.ai_parser import parse_debt_from_text
from app.services.debt_service import get_or_create_user, create_debt
from app.services.ocr_service import ocr_image
from app.platforms.telegram.keyboards.inline import debt_keyboard

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.photo)
async def handle_photo(message: Message):
    processing_msg = await message.reply("Memproses screenshot...")

    try:
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)

        media_dir = Path(settings.media_dir)
        media_dir.mkdir(parents=True, exist_ok=True)
        image_path = media_dir / f"{uuid.uuid4()}.jpg"

        await message.bot.download_file(file.file_path, image_path)

        raw_text = await ocr_image(image_path)

        parsed = await parse_debt_from_text(raw_text)

        async with async_session_factory() as session:
            user = await get_or_create_user(session, message.from_user.id, message.from_user.full_name)

            ocr_log = OcrLog(
                user_id=user.id,
                image_path=str(image_path),
                raw_text=raw_text,
                parsed_json=parsed,
            )
            session.add(ocr_log)

            data = DebtCreate(
                platform=parsed.get("platform", "Unknown"),
                amount=parsed.get("amount", 0),
                due_date=parsed.get("due_date"),
                installment_current=parsed.get("installment_current"),
                installment_total=parsed.get("installment_total"),
                category=parsed.get("category"),
                notes=parsed.get("notes"),
            )
            debt = await create_debt(session, user.id, data, source=DebtSource.screenshot)

        await processing_msg.edit_text(
            f"Berhasil diproses!\n"
            f"Platform: {debt.platform}\n"
            f"Jumlah: Rp{debt.amount:,}\n"
            f"Jatuh tempo: {debt.due_date}",
            reply_markup=debt_keyboard(debt.id),
        )

        try:
            image_path.unlink()
        except OSError:
            pass

    except Exception as e:
        logger.exception("Failed to process screenshot")
        await processing_msg.edit_text(f"Gagal memproses screenshot: {str(e)}")
