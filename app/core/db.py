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
    """CREATE TABLE IF NOT EXISTS platform_signatures (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        platform VARCHAR(100) NOT NULL,
        keyword VARCHAR(255) NOT NULL,
        weight INTEGER NOT NULL DEFAULT 1,
        source VARCHAR(20) NOT NULL DEFAULT 'manual',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""",
    "CREATE INDEX IF NOT EXISTS idx_platform_sig_platform ON platform_signatures(platform)",
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
    "ALTER TABLE debts ADD COLUMN IF NOT EXISTS interest_rate FLOAT",
    "ALTER TABLE debts ADD COLUMN IF NOT EXISTS interest_type VARCHAR(10)",
    """CREATE TABLE IF NOT EXISTS platform_rates (
        platform VARCHAR(100) PRIMARY KEY,
        avg_rate FLOAT NOT NULL DEFAULT 0.0,
        common_type VARCHAR(10),
        sample_count INTEGER NOT NULL DEFAULT 0,
        confidence FLOAT NOT NULL DEFAULT 0.0,
        type_counts JSONB
    )""",
    # Fix type_counts for platform_rates on existing databases
    "ALTER TABLE platform_rates ADD COLUMN IF NOT EXISTS type_counts JSONB",
    # FIX A: Additional migrations from production audit
    "ALTER TABLE debts ADD COLUMN IF NOT EXISTS installment_current INTEGER",
    "ALTER TABLE debts ADD COLUMN IF NOT EXISTS installment_total INTEGER",
    "ALTER TABLE debts ADD COLUMN IF NOT EXISTS category VARCHAR(100)",
    "ALTER TABLE debts ADD COLUMN IF NOT EXISTS notes VARCHAR(500)",
    "ALTER TABLE debts ADD COLUMN IF NOT EXISTS source VARCHAR(20) NOT NULL DEFAULT 'manual'",
    "ALTER TABLE debts ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()",
    "ALTER TABLE debts ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS nama VARCHAR(255)",
    "ALTER TABLE payments ADD COLUMN IF NOT EXISTS notes VARCHAR(500)",
    """CREATE TABLE IF NOT EXISTS reminders (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        debt_id UUID NOT NULL REFERENCES debts(id) ON DELETE CASCADE,
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        remind_at TIMESTAMPTZ NOT NULL,
        type VARCHAR(20) NOT NULL,
        sent BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""",
    """CREATE TABLE IF NOT EXISTS ocr_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL REFERENCES users(id),
        image_path TEXT,
        raw_text TEXT,
        parsed_json JSONB,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )""",
    "ALTER TABLE platform_rates ADD COLUMN IF NOT EXISTS rate_std FLOAT NOT NULL DEFAULT 0.0",
    "ALTER TABLE platform_rates ADD COLUMN IF NOT EXISTS min_rate FLOAT",
    "ALTER TABLE platform_rates ADD COLUMN IF NOT EXISTS max_rate FLOAT",
    "ALTER TABLE platform_rates ADD COLUMN IF NOT EXISTS last_rate_update TIMESTAMPTZ",
    "ALTER TABLE platform_rates ADD COLUMN IF NOT EXISTS outlier_count INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255)",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMPTZ",
]


async def init_db():
    import app.models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        for stmt in MIGRATIONS:
            try:
                await conn.execute(text(stmt))
                logger.info("Migration applied: %s", stmt[:60])
            except Exception as e:
                logger.warning("Migration skipped (%s): %s", e, stmt[:60])
    async with async_session_factory() as session:
        from app.services.platform_matcher import seed_signatures
        await seed_signatures(session)

        # Seed demo user with 5 debts
        from app.models.user import User
        from app.models.debt import Debt, DebtStatus
        from sqlalchemy import select
        from datetime import date, timedelta

        demo_email = "demo@jatuhtempo.app"
        result = await session.execute(select(User).where(User.email == demo_email))
        existing = result.scalar_one_or_none()
    if not existing:
        import bcrypt as _bcrypt_demo
        demo_user = User(
            email=demo_email,
            nama="Demo User",
            password_hash=_bcrypt_demo.hashpw("demo123".encode('utf-8'), _bcrypt_demo.gensalt()).decode('utf-8'),
        )
        session.add(demo_user)
        # We need the user ID; use flush instead of commit
        await session.flush()
        today = date.today()
        demo_debts = [
                Debt(user_id=demo_user.id, platform="Kredivo", amount=350000, due_date=today + timedelta(days=5), installment_current=3, installment_total=12, status=DebtStatus.active, interest_rate=2.5, interest_type="monthly"),
                Debt(user_id=demo_user.id, platform="Shopee PayLater", amount=150000, due_date=today + timedelta(days=12), status=DebtStatus.active),
                Debt(user_id=demo_user.id, platform="Akulaku", amount=500000, due_date=today + timedelta(days=3), installment_current=1, installment_total=6, status=DebtStatus.active, interest_rate=3.0, interest_type="monthly"),
                Debt(user_id=demo_user.id, platform="BCA Kartu Kredit", amount=1250000, due_date=today + timedelta(days=20), status=DebtStatus.active),
                Debt(user_id=demo_user.id, platform="GoPay Later", amount=75000, due_date=today + timedelta(days=2), status=DebtStatus.active),
            ]
        for d in demo_debts:
            session.add(d)
        await session.commit()
        logger.info("Seeded demo user: demo@jatuhtempo.app / demo123 with 5 debts")
