import asyncio
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

from app.core.config import settings
from app.core.db import init_db
from app.core.scheduler import start_scheduler, set_bot_instance
from app.core.ratelimit_mw import RateLimitMiddleware
from app.core.security_mw import SecurityHeadersMiddleware
from app.api.auth import router as auth_router
from app.api.debts import router as debts_router
from app.api.polar import router as polar_router
from app.platforms.telegram.bot import get_bot

logger = logging.getLogger(__name__)


async def start_bot_polling_safe():
    try:
        await asyncio.sleep(2)
        from app.platforms.telegram.bot import start_polling
        await start_polling()
    except Exception as e:
        logger.warning("Bot polling skipped: %s", e)

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting JatuhTempo application")
    await init_db()
    start_scheduler()
    polling_task = None
    try:
        from app.services.alert_service import send_startup_alert
        asyncio.create_task(send_startup_alert())
    except Exception:
        pass
    if settings.telegram_bot_token:
        set_bot_instance(get_bot())
        polling_task = asyncio.create_task(start_bot_polling_safe())
    else:
        logger.warning("TELEGRAM_BOT_TOKEN not set, bot polling disabled")
    yield
    if polling_task:
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass


if settings.sentry_dsn:
    try:
        import sentry_sdk
        sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.1)
        logger.info("Sentry initialized")
    except Exception:
        logger.warning("Sentry import failed, continuing without")

app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan, docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_url] if settings.web_url else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

app.include_router(auth_router)
app.include_router(debts_router)
app.include_router(polar_router)


@app.get("/health")
async def health():
    from app.core.db import async_session_factory
    from sqlalchemy import text
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version, "database": "connected" if db_ok else "disconnected"}


@app.get("/api/stats")
async def get_stats():
    from app.core.db import async_session_factory
    from sqlalchemy import text
    async with async_session_factory() as session:
        users = await session.execute(text("SELECT COUNT(*) FROM users"))
        total_users = users.scalar() or 0
        debts = await session.execute(text("SELECT COUNT(*) FROM debts"))
        total_debts = debts.scalar() or 0
        paid = await session.execute(text("SELECT COUNT(*) FROM debts WHERE status = 'paid'"))
        total_paid = paid.scalar() or 0
    return {
        "product": "jatuhtempo",
        "total_users": total_users,
        "total_debts": total_debts,
        "total_paid": total_paid,
        "status": "online",
    }


import os

_404_HTML = """<!DOCTYPE html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>404 — JatuhTempo</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-slate-50 dark:bg-slate-900 min-h-screen flex items-center justify-center px-4"><div class="text-center max-w-md"><div class="text-8xl mb-4">🔍</div><h1 class="text-3xl font-bold text-slate-900 dark:text-white mb-2">Halaman Tidak Ditemukan</h1><p class="text-slate-500 dark:text-slate-400 mb-8">Halaman yang kamu cari tidak ada atau sudah dipindahkan.</p><a href="/" class="inline-flex items-center justify-center h-12 px-8 rounded-xl bg-teal-600 text-white font-medium hover:bg-teal-700 transition-colors">Kembali ke Beranda</a></div></body></html>"""


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    return HTMLResponse(content=_404_HTML, status_code=404)


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    try:
        from app.services.alert_service import send_alert
        asyncio.create_task(send_alert(
            subject=f"500 Error: {request.method} {request.url.path}",
            detail=f"IP: {request.client.host if request.client else 'unknown'}",
            exc=exc if isinstance(exc, Exception) else None,
        ))
    except Exception:
        pass
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    return HTMLResponse(
        content="""<!DOCTYPE html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Error — JatuhTempo</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-slate-50 dark:bg-slate-900 min-h-screen flex items-center justify-center px-4"><div class="text-center max-w-md"><div class="text-8xl mb-4">😔</div><h1 class="text-3xl font-bold text-slate-900 dark:text-white mb-2">Terjadi Kesalahan</h1><p class="text-slate-500 dark:text-slate-400 mb-8">Kami sudah mencatat error ini. Silakan coba lagi.</p><a href="/" class="inline-flex items-center justify-center h-12 px-8 rounded-xl bg-teal-600 text-white font-medium hover:bg-teal-700 transition-colors">Kembali ke Beranda</a></div></body></html>""",
        status_code=500,
    )


web_out = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web-out")
if os.path.isdir(web_out):
    app.mount("/", StaticFiles(directory=web_out, html=True), name="web")
