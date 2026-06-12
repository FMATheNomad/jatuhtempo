"""
Test fixtures for JatuhTempo backend tests.
"""
import os
# Disable rate limiting for tests
os.environ["TESTING"] = "true"
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only-32chars!"

import uuid
import os
import asyncio
from datetime import date, timedelta, datetime, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.compiler import compiles


# --- Make PostgreSQL UUID compile as VARCHAR on SQLite ---
@compiles(PG_UUID, "sqlite")
def compile_uuid_sqlite(element, compiler, **kw):
    return "VARCHAR(36)"


# --- Override settings BEFORE any app imports ---
os.environ.setdefault("APP_NAME", "JatuhTempo-Test")
os.environ.setdefault("APP_VERSION", "0.0.0-test")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite://")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-jwt-12345")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("WEB_URL", "http://localhost:3000")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "")
os.environ.setdefault("ADMIN_EMAILS", "admin@test.com")
os.environ.setdefault("ENCRYPTION_KEY", "a" * 64)
os.environ.setdefault("CRYPTO_SALT", "test-salt")
os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")
os.environ.setdefault("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
os.environ.setdefault("SENTRY_DSN", "")

# Now safe to import app modules (pydantic-settings reads env vars)
from app.core.config import settings
from app.core.db import Base

# Re-create engine with in-memory SQLite
test_engine = create_async_engine("sqlite+aiosqlite://", echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

# CRITICAL: Override the app's global session factory so API endpoints use the test DB
import app.core.db as db_module
db_module.engine = test_engine
db_module.async_session_factory = TestSessionLocal

from app.models.user import User
from app.models.debt import Debt, DebtStatus, DebtSource
from app.models.platform_rate import PlatformRate
from app.models.payment import Payment
from app.models.reminder import Reminder


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the whole test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    """Create all tables once per session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_db(async_engine):
    """Delete all data before each test to ensure isolation."""
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a session per test. Data is cleaned by clean_db."""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user with known credentials."""
    import bcrypt as _bcrypt
    user = User(
        email="testuser@example.com",
        nama="Test User",
        password_hash=_bcrypt.hashpw(
            "testpass123".encode("utf-8"), _bcrypt.gensalt()
        ).decode("utf-8"),
        subscription_status="free",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin test user."""
    import bcrypt as _bcrypt
    user = User(
        email="admin@test.com",
        nama="Admin User",
        password_hash=_bcrypt.hashpw(
            "adminpass".encode("utf-8"), _bcrypt.gensalt()
        ).decode("utf-8"),
        subscription_status="pro",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def other_user(db_session: AsyncSession) -> User:
    """A second user for ownership tests."""
    import bcrypt as _bcrypt
    user = User(
        email="other@example.com",
        nama="Other User",
        password_hash=_bcrypt.hashpw(
            "otherpass".encode("utf-8"), _bcrypt.gensalt()
        ).decode("utf-8"),
        subscription_status="free",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_debts(db_session: AsyncSession, test_user: User) -> list[Debt]:
    """Create sample debts for the test user."""
    today = date.today()
    debts = [
        Debt(
            user_id=test_user.id,
            platform="Kredivo",
            amount=350000,
            due_date=today + timedelta(days=5),
            installment_current=3,
            installment_total=12,
            status=DebtStatus.active,
            interest_rate=2.5,
            interest_type="monthly",
        ),
        Debt(
            user_id=test_user.id,
            platform="Shopee PayLater",
            amount=150000,
            due_date=today + timedelta(days=12),
            status=DebtStatus.active,
        ),
        Debt(
            user_id=test_user.id,
            platform="Akulaku",
            amount=500000,
            due_date=today + timedelta(days=3),
            status=DebtStatus.active,
            interest_rate=3.0,
            interest_type="monthly",
        ),
        Debt(
            user_id=test_user.id,
            platform="BCA",
            amount=1250000,
            due_date=today + timedelta(days=20),
            status=DebtStatus.paid,
            paid_at=datetime.now(timezone.utc),
        ),
    ]
    for d in debts:
        db_session.add(d)
    await db_session.commit()
    for d in debts:
        await db_session.refresh(d)
    return debts


@pytest_asyncio.fixture
async def other_user_debt(db_session: AsyncSession, other_user: User) -> Debt:
    """Create a debt owned by the other user (for cross-ownership tests)."""
    debt = Debt(
        user_id=other_user.id,
        platform="GoPay Later",
        amount=75000,
        due_date=date.today() + timedelta(days=2),
        status=DebtStatus.active,
    )
    db_session.add(debt)
    await db_session.commit()
    await db_session.refresh(debt)
    return debt


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    """Generate valid Bearer token headers for the test user."""
    from app.core.auth import create_session_token
    token = create_session_token(None, test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_auth_headers(admin_user: User) -> dict:
    """Generate valid Bearer token headers for the admin user."""
    from app.core.auth import create_session_token
    token = create_session_token(None, admin_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTP client against the FastAPI app."""
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
