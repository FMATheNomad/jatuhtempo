"""Test if fresh dict copy fixes JSON persistence on SQLite."""
import os
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite://')
os.environ.setdefault('JWT_SECRET', 'test-secret-key-for-jwt-12345')
os.environ.setdefault('ENCRYPTION_KEY', 'a' * 64)

import asyncio
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.compiler import compiles

@compiles(PG_UUID, "sqlite")
def compile_uuid_sqlite(element, compiler, **kw):
    return "VARCHAR(36)"

engine = create_async_engine("sqlite+aiosqlite://", echo=False)
from app.core.db import Base
from app.models.platform_rate import PlatformRate


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_majority_vote():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Call 1
    async with Session() as session:
        from app.services.platform_rate_service import update_platform_rate
        r1 = await update_platform_rate(session, "Akulaku", 2.0, "daily")
        print(f"After 1st: type_counts={r1.type_counts}, common_type={r1.common_type}")

    # Call 2
    async with Session() as session:
        from app.services.platform_rate_service import update_platform_rate
        r2 = await update_platform_rate(session, "Akulaku", 3.0, "monthly")
        print(f"After 2nd: type_counts={r2.type_counts}, common_type={r2.common_type}")

    # Call 3
    async with Session() as session:
        from app.services.platform_rate_service import update_platform_rate
        r3 = await update_platform_rate(session, "Akulaku", 2.5, "monthly")
        print(f"After 3rd: type_counts={r3.type_counts}, common_type={r3.common_type}")

    assert r3.type_counts == {"daily": 1, "monthly": 2}, f"Got {r3.type_counts}"
    assert r3.common_type == "monthly", f"Got {r3.common_type}"
    print("PASSED!")
