import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

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
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS polar_customer_id VARCHAR(100)",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(20) NOT NULL DEFAULT 'free'",
    "ALTER TABLE users ALTER COLUMN telegram_id DROP NOT NULL",
    """CREATE TABLE IF NOT EXISTS audit_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id),
        action VARCHAR(50) NOT NULL,
        resource VARCHAR(50) NOT NULL,
        resource_id VARCHAR(100),
        detail TEXT,
        ip_address VARCHAR(50),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255)",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)",
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
    import app.models  # noqa: F401 — import inside function to avoid circular import
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        for stmt in MIGRATIONS:
            try:
                await conn.execute(text(stmt))
                logger.info("Migration applied: %s", stmt[:60])
            except Exception as e:
                logger.warning("Migration skipped (%s): %s", e, stmt[:60])
