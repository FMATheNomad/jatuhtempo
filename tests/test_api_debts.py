"""
Tests for debt API endpoints: CRUD, ownership, summary, admin permissions.
"""

import uuid
import pytest
from httpx import AsyncClient


class TestDebtsCreate:
    """Tests for POST /api/debts."""

    async def test_create_debt(self, client: AsyncClient, auth_headers):
        payload = {
            "platform": "Kredivo",
            "amount": 500000,
            "due_date": "2026-07-15",
        }
        resp = await client.post("/api/debts", json=payload, headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["platform"] == "Kredivo"
        assert data["amount"] == 500000
        assert data["status"] == "active"
        assert "id" in data

    async def test_create_debt_with_interest(self, client: AsyncClient, auth_headers):
        payload = {
            "platform": "Akulaku",
            "amount": 300000,
            "due_date": "2026-08-01",
            "interest_rate": 2.5,
            "interest_type": "monthly",
        }
        resp = await client.post("/api/debts", json=payload, headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["interest_rate"] == 2.5
        assert data["interest_type"] == "monthly"

    async def test_create_debt_with_installments(self, client: AsyncClient, auth_headers):
        payload = {
            "platform": "Kredivo",
            "amount": 1000000,
            "due_date": "2026-06-30",
            "installment_current": 2,
            "installment_total": 12,
        }
        resp = await client.post("/api/debts", json=payload, headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["installment_current"] == 2
        assert data["installment_total"] == 12

    async def test_create_debt_invalid_date(self, client: AsyncClient, auth_headers):
        payload = {
            "platform": "Kredivo",
            "amount": 500000,
            "due_date": "not-a-date",
        }
        resp = await client.post("/api/debts", json=payload, headers=auth_headers)
        assert resp.status_code == 400, resp.text

    async def test_create_debt_unauthorized(self, client: AsyncClient):
        payload = {
            "platform": "Kredivo",
            "amount": 500000,
            "due_date": "2026-07-15",
        }
        resp = await client.post("/api/debts", json=payload)
        assert resp.status_code == 401, resp.text


class TestDebtsList:
    """Tests for GET /api/debts."""

    async def test_list_debts(self, client: AsyncClient, auth_headers, sample_debts):
        resp = await client.get("/api/debts", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # 3 active + 1 paid

    async def test_list_debts_filter_by_status(self, client: AsyncClient, auth_headers, sample_debts):
        resp = await client.get("/api/debts?status=paid", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert all(d["status"] == "paid" for d in data)

    async def test_list_debts_filter_by_platform(self, client: AsyncClient, auth_headers, sample_debts):
        resp = await client.get("/api/debts?platform=Kredivo", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert all("Kredivo" in d["platform"] for d in data)

    async def test_list_debts_empty(self, client: AsyncClient, auth_headers):
        """User with no debts should get empty list."""
        resp = await client.get("/api/debts", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        assert resp.json() == []


class TestDebtsSummary:
    """Tests for GET /api/debts/summary."""

    async def test_get_summary(self, client: AsyncClient, auth_headers, sample_debts):
        resp = await client.get("/api/debts/summary", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "total_active" in data
        assert "total_amount" in data
        assert "paid_this_month" in data
        assert "upcoming" in data
        assert data["total_active"] >= 3
        assert data["total_amount"] >= 1000000


class TestDebtsOwnership:
    """Critical: verify users can only access their own debts."""

    async def test_cannot_access_other_users_debt(
        self, client: AsyncClient, auth_headers, other_user_debt
    ):
        """Test user should NOT see the other user's debt via home/upcoming."""
        resp = await client.get("/api/debts", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        ids = [d["id"] for d in data]
        assert str(other_user_debt.id) not in ids, "Should not see other user's debt"

    async def test_cannot_update_other_users_debt(
        self, client: AsyncClient, auth_headers, other_user_debt
    ):
        payload = {
            "platform": "Hacked",
            "amount": 999999,
            "due_date": "2026-07-15",
        }
        resp = await client.patch(
            f"/api/debts/{other_user_debt.id}",
            json=payload,
            headers=auth_headers,
        )
        assert resp.status_code == 404, resp.text

    async def test_cannot_delete_other_users_debt(
        self, client: AsyncClient, auth_headers, other_user_debt
    ):
        resp = await client.delete(
            f"/api/debts/{other_user_debt.id}",
            headers=auth_headers,
        )
        assert resp.status_code == 404, resp.text


class TestDebtsDelete:
    """Tests for DELETE /api/debts/{id}."""

    async def test_delete_own_debt(self, client: AsyncClient, auth_headers, sample_debts):
        debt_id = sample_debts[0].id
        resp = await client.delete(f"/api/debts/{debt_id}", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        assert resp.json()["ok"] is True

    async def test_delete_nonexistent(self, client: AsyncClient, auth_headers):
        fake_id = uuid.uuid4()
        resp = await client.delete(f"/api/debts/{fake_id}", headers=auth_headers)
        assert resp.status_code == 404, resp.text

    async def test_delete_invalid_id(self, client: AsyncClient, auth_headers):
        resp = await client.delete("/api/debts/not-a-uuid", headers=auth_headers)
        assert resp.status_code == 404, resp.text

    async def test_delete_unauthorized(self, client: AsyncClient, sample_debts):
        resp = await client.delete(f"/api/debts/{sample_debts[0].id}")
        assert resp.status_code == 401, resp.text


class TestAdminPermissions:
    """Tests for admin-only endpoints."""

    async def test_non_admin_cannot_update_rate(
        self, client: AsyncClient, auth_headers
    ):
        """Regular user should get 403 on admin endpoints."""
        payload = {"avg_rate": 5.0}
        resp = await client.put(
            "/api/admin/platforms/rates/Kredivo",
            json=payload,
            headers=auth_headers,
        )
        assert resp.status_code == 403, resp.text

    async def test_admin_can_update_rate(
        self, client: AsyncClient, admin_auth_headers
    ):
        payload = {"avg_rate": 3.5}
        resp = await client.put(
            "/api/admin/platforms/rates/Kredivo",
            json=payload,
            headers=admin_auth_headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["avg_rate"] == 3.5
        assert data["confidence"] == 1.0

    async def test_admin_can_delete_rate(
        self, client: AsyncClient, admin_auth_headers
    ):
        # Create a rate first
        from app.core.db import async_session_factory
        from app.models.platform_rate import PlatformRate
        async with async_session_factory() as session:
            session.add(PlatformRate(platform="TestPlatform", avg_rate=5.0, sample_count=1, confidence=0.5))
            await session.commit()

        resp = await client.delete(
            "/api/admin/platforms/rates/TestPlatform",
            headers=admin_auth_headers,
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["ok"] is True

    async def test_non_admin_cannot_delete_rate(
        self, client: AsyncClient, auth_headers
    ):
        resp = await client.delete(
            "/api/admin/platforms/rates/Kredivo",
            headers=auth_headers,
        )
        assert resp.status_code == 403, resp.text
