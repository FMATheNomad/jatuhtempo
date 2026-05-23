import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.config import settings
from app.platforms.telegram.handlers import commands, messages

logger = logging.getLogger(__name__)

dp = Dispatcher()
_bot: Bot | None = None


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    return _bot


def register_handlers():
    dp.include_router(commands.router)
    dp.include_router(messages.router)


async def start_polling():
    if not settings.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN not set, skipping bot polling")
        return
    register_handlers()
    bot = get_bot()
    logger.info("Starting Telegram bot polling")
    await dp.start_polling(bot, skip_updates=True)
