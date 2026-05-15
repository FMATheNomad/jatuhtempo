import asyncio
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.db import init_db
from app.core.scheduler import start_scheduler, set_bot_instance
from app.platforms.telegram.bot import bot, start_polling

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting JatuhTempo application")
    await init_db()
    start_scheduler()
    set_bot_instance(bot)
    polling_task = asyncio.create_task(start_polling())
    yield
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}
