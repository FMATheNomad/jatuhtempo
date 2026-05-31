import logging
from datetime import datetime, timezone

from sqlalchemy import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.core.db import async_session_factory
from app.models.reminder import Reminder
from app.models.debt import Debt
from app.models.user import User

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
                    msg = (
                        f"Pengingat: {reminder.type}\n"
                        f"Tagihan: {debt.platform}\n"
                        f"Jumlah: Rp{debt.amount:,}\n"
                        f"Jatuh tempo: {debt.due_date}"
                    )
                    await _bot_instance.send_message(chat_id=user.telegram_id, text=msg)

                reminder.sent = True
                await session.commit()
            except Exception as e:
                logger.error(f"Failed to send reminder {reminder.id}: {e}")
                await session.rollback()


def start_scheduler():
    scheduler.add_job(
        check_reminders,
        trigger=IntervalTrigger(minutes=settings.reminder_check_interval_minutes),
        id="check_reminders",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started")
