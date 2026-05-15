import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.config import settings
from app.platforms.telegram.handlers import commands, messages

logger = logging.getLogger(__name__)

bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


def register_handlers():
    dp.include_router(commands.router)
    dp.include_router(messages.router)


async def start_polling():
    register_handlers()
    logger.info("Starting Telegram bot polling")
    await dp.start_polling(bot, skip_updates=True)
