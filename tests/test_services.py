"""
Tests for service-layer logic: debt creation, platform rate EMA/outlier/majority.
"""

import uuid
import pytest
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.debt_service import create_debt, get_user_debts
from app.services.platform_rate_service import (
    update_platform_rate, get_platform_rate, get_all_platform_rates
)
from app.schemas.debt import DebtCreate
from app.models.debt import DebtSource, DebtStatus


class TestDebtServiceCreate:
    """Tests for debt_service.create_debt."""

    async def test_create_minimal_debt(self, db_session: AsyncSession, test_user):
        data = DebtCreate(platform="Kredivo", amount=250000, due_date=date.today() + timedelta(days=10))
        debt = await create_debt(db_session, test_user.id, data)
        assert debt.id is not None
        assert debt.platform == "Kredivo"
        assert debt.amount == 250000
        assert debt.user_id == test_user.id
        assert debt.status == DebtStatus.active
        assert debt.source == DebtSource.manual

    async def test_create_full_debt(self, db_session: AsyncSession, test_user):
        data = DebtCreate(
            platform="Akulaku",
            amount=500000,
            due_date=date.today() + timedelta(days=20),
            interest_rate=3.0,
            interest_type="monthly",
            installment_current=1,
            installment_total=6,
            category="paylater",
            notes="Test notes",
        )
        debt = await create_debt(db_session, test_user.id, data)
        assert debt.interest_rate == 3.0
        assert debt.installment_current == 1
        assert debt.installment_total == 6
        assert debt.category == "paylater"
        assert debt.notes == "Test notes"

    async def test_create_debt_creates_reminders(self, db_session: AsyncSession, test_user):
        """Verify reminders are auto-created."""
        from app.models.reminder import Reminder
        from sqlalchemy import select

        data = DebtCreate(platform="GoPay Later", amount=100000, due_date=date.today() + timedelta(days=7))
        debt = await create_debt(db_session, test_user.id, data)

        result = await db_session.execute(
            select(Reminder).where(Reminder.debt_id == debt.id)
        )
        reminders = result.scalars().all()
        assert len(reminders) >= 3  # H-7, H-3, H-1, due, overdue
        types = [r.type for r in reminders]
        assert "H-7" in types
        assert "due" in types


class TestDebtServiceList:
    """Tests for debt_service.get_user_debts."""

    async def test_list_user_debts(self, db_session: AsyncSession, test_user, sample_debts):
        debts = await get_user_debts(db_session, test_user.id)
        assert len(debts) == len(sample_debts)

    async def test_list_filter_by_status(self, db_session: AsyncSession, test_user, sample_debts):
        paid = await get_user_debts(db_session, test_user.id, status=DebtStatus.paid)
        assert all(d.status == DebtStatus.paid for d in paid)
        assert len(paid) == 1  # BCA is paid

    async def test_list_filter_by_platform(self, db_session: AsyncSession, test_user, sample_debts):
        kredivo = await get_user_debts(db_session, test_user.id, platform="Kredivo")
        assert len(kredivo) >= 1
        assert all("Kredivo" in d.platform for d in kredivo)

    async def test_list_empty_for_new_user(self, db_session: AsyncSession):
        """New user with no debts should return empty list."""
        import bcrypt as _bcrypt
        from app.models.user import User
        new_user = User(
            email="newuser@test.com",
            nama="New",
            password_hash=_bcrypt.hashpw("pass".encode(), _bcrypt.gensalt()).decode(),
        )
        db_session.add(new_user)
        await db_session.commit()

        debts = await get_user_debts(db_session, new_user.id)
        assert debts == []


class TestPlatformRateService:
    """Tests for platform_rate_service.update_platform_rate logic.

    Tests:
    - EMA decay formula
    - Outlier rejection (rate > 50 or < 0.1)
    - Majority vote for common_type
    - Confidence calculation
    """

    async def test_first_rate_creates_entry(self, db_session: AsyncSession):
        rate = await update_platform_rate(db_session, "Kredivo", 2.5, "monthly")
        assert rate is not None
        assert rate.platform == "Kredivo"
        assert rate.avg_rate == 2.5
        assert rate.common_type == "monthly"
        assert rate.sample_count == 1

    async def test_ema_decay(self, db_session: AsyncSession):
        """After multiple entries, avg_rate should be an EMA, not a simple average.

        Push 2.0 then 4.0. With alpha = min(0.3, 1/(n+1)):
        - After 1st: avg = 2.0, n=1
        - After 2nd: alpha = min(0.3, 1/2) = 0.3, avg = 0.7*2.0 + 0.3*4.0 = 1.4 + 1.2 = 2.6
        """
        await update_platform_rate(db_session, "GoPay Later", 2.0, "monthly")
        rate = await update_platform_rate(db_session, "GoPay Later", 4.0, "monthly")
        expected = 0.7 * 2.0 + 0.3 * 4.0
        assert rate.avg_rate == pytest.approx(expected, abs=0.01)

    async def test_outlier_high_rejected(self, db_session: AsyncSession):
        """Rate > 50 should be rejected."""
        result = await update_platform_rate(db_session, "TestHigh", 99.9, "monthly")
        assert result is None

    async def test_outlier_low_rejected(self, db_session: AsyncSession):
        """Rate < 0.1 should be rejected."""
        result = await update_platform_rate(db_session, "TestLow", 0.01, "monthly")
        assert result is None

    async def test_outlier_boundary_accepted(self, db_session: AsyncSession):
        """Rate = 0.1 (boundary) should be accepted."""
        rate = await update_platform_rate(db_session, "TestBoundary", 0.1, "flat")
        assert rate is not None
        assert rate.avg_rate == 0.1

    async def test_outlier_boundary_high_accepted(self, db_session: AsyncSession):
        """Rate = 50.0 (boundary) should be accepted."""
        rate = await update_platform_rate(db_session, "TestBoundaryHigh", 50.0, "flat")
        assert rate is not None
        assert rate.avg_rate == 50.0

    async def test_majority_vote_for_type(self, db_session: AsyncSession):
        """common_type should be the most frequently submitted type."""
        await update_platform_rate(db_session, "Akulaku", 2.0, "daily")
        await update_platform_rate(db_session, "Akulaku", 3.0, "monthly")
        rate = await update_platform_rate(db_session, "Akulaku", 2.5, "monthly")
        assert rate.common_type == "monthly"  # monthly=2 > daily=1

    async def test_confidence_calculation(self, db_session: AsyncSession):
        """confidence = min(1.0, sample_count / 20)."""
        # After 10 entries: confidence = 10/20 = 0.5
        for i in range(10):
            await update_platform_rate(db_session, "TestConfidence", 3.0, "flat")
        rate = await get_platform_rate(db_session, "TestConfidence")
        assert rate.confidence == pytest.approx(0.5, abs=0.01)
        assert rate.sample_count == 10

    async def test_confidence_caps_at_1(self, db_session: AsyncSession):
        """confidence should not exceed 1.0."""
        for i in range(30):
            await update_platform_rate(db_session, "TestCap", 3.0, "flat")
        rate = await get_platform_rate(db_session, "TestCap")
        assert rate.confidence == 1.0

    async def test_get_all_platform_rates(self, db_session: AsyncSession):
        await update_platform_rate(db_session, "A", 1.0, "flat")
        await update_platform_rate(db_session, "B", 2.0, "monthly")
        rates = await get_all_platform_rates(db_session)
        assert len(rates) >= 2
        platforms = [r.platform for r in rates]
        assert "A" in platforms
        assert "B" in platforms
