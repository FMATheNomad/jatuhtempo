"""
Tests for payment service and audit service.
"""

import uuid
import pytest
from datetime import datetime, timezone, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.payment_service import create_payment, get_payments_for_debt
from app.services.audit_service import log_audit
from app.models.payment import Payment
from app.models.audit_log import AuditLog
from app.models.debt import Debt, DebtStatus


class TestPaymentService:
    """Tests for payment_service."""

    async def test_create_payment(self, db_session: AsyncSession, test_user, sample_debts):
        debt = sample_debts[0]
        payment = await create_payment(db_session, debt.id, test_user.id, 100000, notes="test payment")
        assert payment.id is not None
        assert payment.debt_id == debt.id
        assert payment.user_id == test_user.id
        assert payment.amount_paid == 100000
        assert payment.notes == "test payment"

    async def test_get_payments_for_debt(self, db_session: AsyncSession, test_user, sample_debts):
        debt = sample_debts[0]
        await create_payment(db_session, debt.id, test_user.id, 50000)
        await create_payment(db_session, debt.id, test_user.id, 75000, notes="second payment")

        payments = await get_payments_for_debt(db_session, debt.id, test_user.id)
        assert len(payments) == 2
        assert payments[0].amount_paid == 75000  # DESC order, most recent first

    async def test_get_payments_for_other_user_excluded(self, db_session: AsyncSession, test_user, other_user, sample_debts):
        debt = sample_debts[0]
        await create_payment(db_session, debt.id, test_user.id, 50000)
        # Other user should not see this payment
        payments = await get_payments_for_debt(db_session, debt.id, other_user.id)
        assert len(payments) == 0

    async def test_get_payments_empty(self, db_session: AsyncSession, test_user, sample_debts):
        debt_id = sample_debts[0].id
        payments = await get_payments_for_debt(db_session, debt_id, test_user.id)
        assert payments == []


class TestAuditService:
    """Tests for audit_service."""

    async def test_log_audit(self, db_session: AsyncSession, test_user):
        await log_audit(db_session, test_user.id, "create", "debt", "debt-123", "test detail", "127.0.0.1")

        result = await db_session.execute(
            select(AuditLog).where(AuditLog.resource_id == "debt-123")
        )
        log = result.scalar_one_or_none()
        assert log is not None
        assert log.user_id == test_user.id
        assert log.action == "create"
        assert log.resource == "debt"
        assert log.resource_id == "debt-123"
        assert log.detail == "test detail"
        assert log.ip_address == "127.0.0.1"

    async def test_log_audit_without_user(self, db_session: AsyncSession):
        await log_audit(db_session, None, "system", "health", detail="server start")

        result = await db_session.execute(
            select(AuditLog).where(AuditLog.action == "system")
        )
        log = result.scalar_one_or_none()
        assert log is not None
        assert log.user_id is None
        assert log.action == "system"
