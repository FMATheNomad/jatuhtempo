import asyncio
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import init_db
from app.core.scheduler import start_scheduler, set_bot_instance
from app.api.auth import router as auth_router
from app.api.debts import router as debts_router
from app.platforms.telegram.bot import get_bot, start_polling

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting JatuhTempo application")
    await init_db()
    start_scheduler()
    polling_task = None
    if settings.telegram_bot_token:
        set_bot_instance(get_bot())
        polling_task = asyncio.create_task(start_polling())
    else:
        logger.warning("TELEGRAM_BOT_TOKEN not set, bot polling disabled")
    yield
    if polling_task:
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_url] if settings.web_url else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(debts_router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


@app.get("/api/stats")
async def get_stats():
    from app.core.db import async_session_factory
    from sqlalchemy import text
    async with async_session_factory() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        total_users = result.scalar() or 0
    return {
        "product": "jatuhtempo",
        "total_users": total_users,
        "status": "online",
    }
