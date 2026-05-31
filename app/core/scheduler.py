import logging
import random
from datetime import datetime, timezone

from sqlalchemy import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.core.config import settings
from app.core.db import async_session_factory
from app.models.reminder import Reminder
from app.models.debt import Debt
from app.models.user import User
from app.platforms.telegram.keyboards.inline import debt_keyboard

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

_bot_instance = None


def set_bot_instance(bot):
    global _bot_instance
    _bot_instance = bot


async def check_reminders():
    if _bot_instance is None:
        return

    now = datetime.now(timezone.utc)
    async with async_session_factory() as session:
        result = await session.execute(
            select(Reminder).where(Reminder.remind_at <= now, Reminder.sent == False)
        )
        reminders = result.scalars().all()

        for reminder in reminders:
            try:
                debt = await session.get(Debt, reminder.debt_id)
                user = await session.get(User, reminder.user_id)
                if debt and user:
                    label_map = {
                        "H-7": "⏰ 7 hari lagi",
                        "H-3": "⏰ 3 hari lagi",
                        "H-1": "⏰ Besok!",
                        "due": "⚠️ Jatuh tempo hari ini!",
                        "overdue": "🚨 Sudah terlambat!",
                    }
                    label = label_map.get(reminder.type, reminder.type)
                    msg = (
                        f"{label}\n"
                        f"Tagihan: {debt.platform}\n"
                        f"Jumlah: Rp{debt.amount:,}\n"
                        f"Jatuh tempo: {debt.due_date}"
                    )
                    await _bot_instance.send_message(
                        chat_id=user.telegram_id,
                        text=msg,
                        reply_markup=debt_keyboard(debt.id),
                    )

                reminder.sent = True
                await session.commit()
            except Exception as e:
                logger.error(f"Failed to send reminder {reminder.id}: {e}")
                await session.rollback()


async def check_wa_unlinked():
    if _bot_instance is None:
        return

    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(
                User.phone_number.is_(None),
                User.wa_reminder_optout == False,
            )
        )
        users = result.scalars().all()

    if not users:
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏸ Jangan ingatkan lagi", callback_data="wa_optout")]
        ]
    )

    msg = (
        "🔔 <b>Hubungkan WhatsApp</b>\n\n"
        "Kamu belum menghubungkan nomor WhatsApp.\n"
        "Segera hubungkan agar bisa menerima pengingat via WhatsApp juga.\n\n"
        "Gunakan: /wa 08123456789"
    )

    for user in users:
        try:
            await _bot_instance.send_message(
                chat_id=user.telegram_id,
                text=msg,
                reply_markup=keyboard,
            )
        except Exception as e:
            logger.warning(f"Failed to send WA reminder to {user.telegram_id}: {e}")


def start_scheduler():
    scheduler.add_job(
        check_reminders,
        trigger=IntervalTrigger(minutes=settings.reminder_check_interval_minutes),
        id="check_reminders",
        replace_existing=True,
    )
    scheduler.add_job(
        check_wa_unlinked,
        trigger=IntervalTrigger(hours=random.choice([4, 5, 6, 7, 8])),
        id="check_wa_unlinked",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started")
