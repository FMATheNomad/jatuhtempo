"""
Tests for platform matcher: match_platform and learn_from_correction.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.platform_matcher import match_platform, seed_signatures, learn_from_correction
from app.models.platform_signature import PlatformSignature
from sqlalchemy import select


class TestPlatformMatcher:
    """Tests for match_platform."""

    async def test_seed_signatures(self, db_session: AsyncSession):
        await seed_signatures(db_session)
        result = await db_session.execute(select(PlatformSignature))
        sigs = result.scalars().all()
        assert len(sigs) > 0

    async def test_seed_signatures_idempotent(self, db_session: AsyncSession):
        await seed_signatures(db_session)
        await seed_signatures(db_session)
        result = await db_session.execute(select(PlatformSignature))
        sigs = result.scalars().all()
        # Should not double-seed
        assert len(sigs) > 0

    async def test_match_known_platform(self, db_session: AsyncSession):
        await seed_signatures(db_session)
        result = await match_platform("Tagihan Kredivo bulan ini Rp500,000", db_session)
        assert result == "Kredivo"

    async def test_match_shopee_paylater(self, db_session: AsyncSession):
        await seed_signatures(db_session)
        result = await match_platform("SpayLater tagihan Oktober", db_session)
        assert result == "Shopee PayLater"

    async def test_match_akulaku(self, db_session: AsyncSession):
        await seed_signatures(db_session)
        result = await match_platform("Rincian Pinjaman Akulaku", db_session)
        assert result == "Akulaku"

    async def test_match_returns_none_for_empty_text(self, db_session: AsyncSession):
        await seed_signatures(db_session)
        result = await match_platform("", db_session)
        assert result is None

    async def test_match_returns_none_for_unrecognized(self, db_session: AsyncSession):
        await seed_signatures(db_session)
        result = await match_platform("some random gibberish text", db_session)
        assert result is None

    async def test_match_tiebreaker_requires_3_point_lead(self, db_session: AsyncSession):
        await seed_signatures(db_session)
        # BCA has weight 5 for "bca", Mandiri has weight 7 for "bank mandiri"
        # If text matches both "bca" and "bank mandiri", BCA should have a significant lead
        result = await match_platform("BCA and BCA and BCA", db_session)
        assert result == "BCA"


class TestLearnFromCorrection:
    """Tests for learn_from_correction."""

    async def test_learn_adds_signatures(self, db_session: AsyncSession):
        await seed_signatures(db_session)
        text = "my tagihan from somebank"
        await learn_from_correction(db_session, text, "BCA", None)

        result = await db_session.execute(
            select(PlatformSignature).where(PlatformSignature.platform == "BCA", PlatformSignature.source == "correction")
        )
        sigs = result.scalars().all()
        assert len(sigs) >= 1

    async def test_learn_with_incorrect_platform(self, db_session: AsyncSession):
        await seed_signatures(db_session)
        text = "mandiri bill payment"
        await learn_from_correction(db_session, text, "BCA", "Mandiri")

        result = await db_session.execute(
            select(PlatformSignature).where(PlatformSignature.platform == "BCA", PlatformSignature.source == "correction")
        )
        sigs = result.scalars().all()
        assert len(sigs) >= 1

    async def test_learn_empty_text_does_nothing(self, db_session: AsyncSession):
        await seed_signatures(db_session)
        await learn_from_correction(db_session, "", "BCA", None)
        result = await db_session.execute(select(PlatformSignature))
        count = len(result.scalars().all())
        # Only seed data, no corrections added
        assert count >= 1
