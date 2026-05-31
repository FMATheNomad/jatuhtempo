import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
import app.models  # noqa: F401 — ensure all models are loaded for metadata.create_all

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


MIGRATIONS = [
    "ALTER TABLE debts ADD COLUMN IF NOT EXISTS paid_at TIMESTAMPTZ",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20)",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS wa_linked_at TIMESTAMPTZ",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS wa_reminder_optout BOOLEAN NOT NULL DEFAULT FALSE",
    """CREATE TABLE IF NOT EXISTS payments (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        debt_id UUID NOT NULL REFERENCES debts(id) ON DELETE CASCADE,
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        amount_paid INTEGER NOT NULL,
        paid_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        notes VARCHAR(500)
    )""",
]


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        for stmt in MIGRATIONS:
            try:
                await conn.execute(text(stmt))
                logger.info("Migration applied: %s", stmt[:60])
            except Exception as e:
                logger.warning("Migration skipped (%s): %s", e, stmt[:60])
