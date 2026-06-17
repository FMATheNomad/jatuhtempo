import os
import logging
import traceback

from app.core.db import async_session_factory
from app.models.user import User
from sqlalchemy import select

logger = logging.getLogger(__name__)

ADMIN_TELEGRAM_ID = int(os.environ.get("ADMIN_TELEGRAM_ID", "0")) if os.environ.get("ADMIN_TELEGRAM_ID") else None


async def send_alert(subject: str, detail: str = "", exc: Exception | None = None) -> bool:
    """Send error alert via Telegram to admin only. Non-blocking, fails silently."""
    if not ADMIN_TELEGRAM_ID:
        logger.warning("ADMIN_TELEGRAM_ID not set, skipping alert: %s", subject)
        return False

    try:
        from app.platforms.telegram.bot import get_bot

        msg = f"🚨 *JatuhTempo Alert*\n*{subject}*"
        if detail:
            msg += f"\n{detail}"
        if exc:
            tb = "".join(traceback.format_exception_only(type(exc), exc)).strip()
            msg += f"\n`{tb}`"

        bot = get_bot()
        await bot.send_message(chat_id=ADMIN_TELEGRAM_ID, text=msg, parse_mode="Markdown")
        return True
    except Exception as e:
        logger.warning("Failed to send alert: %s", e)
        return False


async def send_startup_alert() -> bool:
    """Notify admin when the app starts up."""
    return await send_alert("✅ App Started", "JatuhTempo is running")


async def send_user_milestone(user_id: str, event: str) -> bool:
    """Notify admin about notable user events (first debt, upgrade, etc)."""
    try:
        async with async_session_factory() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                return False
            email = user.email or "unknown"
            return await send_alert(f"👤 User {event}", f"User: {email}")
    except Exception:
        return False
