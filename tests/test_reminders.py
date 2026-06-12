"""
Tests for reminder service: auto-creation on debt create.
"""

import pytest
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.reminder import Reminder
from app.models.debt import DebtStatus
from app.schemas.debt import DebtCreate
from app.services.debt_service import create_debt, update_debt_status


class TestReminderCreation:
    """Verify reminders are auto-created when a debt is created."""

    async def test_create_debt_creates_5_reminders(self, db_session: AsyncSession, test_user):
        data = DebtCreate(
            platform="Kredivo",
            amount=250000,
            due_date=date.today() + timedelta(days=10),
        )
        debt = await create_debt(db_session, test_user.id, data)

        result = await db_session.execute(
            select(Reminder).where(Reminder.debt_id == debt.id)
        )
        reminders = result.scalars().all()
        assert len(reminders) == 5
        types = [r.type for r in reminders]
        assert sorted(types) == ["H-1", "H-3", "H-7", "due", "overdue"]

    async def test_reminder_types_are_correct(self, db_session: AsyncSession, test_user):
        due = date.today() + timedelta(days=7)
        data = DebtCreate(
            platform="GoPay Later",
            amount=100000,
            due_date=due,
        )
        debt = await create_debt(db_session, test_user.id, data)

        result = await db_session.execute(
            select(Reminder).where(Reminder.debt_id == debt.id).order_by(Reminder.remind_at)
        )
        reminders = result.scalars().all()

        expected_dates = {
            "H-7": due - timedelta(days=7),
            "H-3": due - timedelta(days=3),
            "H-1": due - timedelta(days=1),
            "due": due,
            "overdue": due + timedelta(days=1),
        }

        for r in reminders:
            expected_date = expected_dates.get(r.type)
            assert expected_date is not None, f"Unexpected reminder type: {r.type}"
            assert r.remind_at.date() == expected_date

    async def test_reminders_unsent_by_default(self, db_session: AsyncSession, test_user):
        data = DebtCreate(
            platform="Akulaku",
            amount=500000,
            due_date=date.today() + timedelta(days=14),
        )
        debt = await create_debt(db_session, test_user.id, data)

        result = await db_session.execute(
            select(Reminder).where(Reminder.debt_id == debt.id)
        )
        reminders = result.scalars().all()
        assert all(r.sent is False for r in reminders)

    async def test_debt_delete_cascades_reminders(self, db_session: AsyncSession, test_user):
        from app.services.debt_service import delete_debt

        data = DebtCreate(
            platform="Kredivo",
            amount=250000,
            due_date=date.today() + timedelta(days=10),
        )
        debt = await create_debt(db_session, test_user.id, data)

        await delete_debt(db_session, debt.id, test_user.id)

        result = await db_session.execute(
            select(Reminder).where(Reminder.debt_id == debt.id)
        )
        reminders = result.scalars().all()
        assert len(reminders) == 0

    async def test_paid_status_update_does_not_delete_reminders(self, db_session: AsyncSession, test_user):
        data = DebtCreate(
            platform="Kredivo",
            amount=250000,
            due_date=date.today() + timedelta(days=5),
        )
        debt = await create_debt(db_session, test_user.id, data)

        await update_debt_status(db_session, debt.id, DebtStatus.paid, test_user.id)

        result = await db_session.execute(
            select(Reminder).where(Reminder.debt_id == debt.id)
        )
        reminders = result.scalars().all()
        assert len(reminders) == 5
