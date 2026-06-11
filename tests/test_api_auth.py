"""
Tests for authentication API endpoints: register, login-web, /me, rate limiting.
"""

import pytest
from httpx import AsyncClient


class TestAuthRegister:
    """Tests for POST /api/auth/register."""

    async def test_register_success(self, client: AsyncClient):
        payload = {"email": "newuser@example.com", "password": "supersecret", "nama": "New User"}
        resp = await client.post("/api/auth/register", json=payload)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "session_token" in data
        assert data["email"] == "newuser@example.com"
        assert data["nama"] == "New User"
        assert "user_id" in data

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        payload = {"email": "testuser@example.com", "password": "testpass123"}
        resp = await client.post("/api/auth/register", json=payload)
        assert resp.status_code == 409, resp.text
        assert "sudah terdaftar" in resp.text.lower()

    async def test_register_invalid_email(self, client: AsyncClient):
        payload = {"email": "not-an-email", "password": "testpass123"}
        resp = await client.post("/api/auth/register", json=payload)
        assert resp.status_code == 400, resp.text

    async def test_register_short_password(self, client: AsyncClient):
        payload = {"email": "shortpw@example.com", "password": "12345"}
        resp = await client.post("/api/auth/register", json=payload)
        assert resp.status_code == 400, resp.text


class TestAuthLoginWeb:
    """Tests for POST /api/auth/login-web."""

    async def test_login_success(self, client: AsyncClient, test_user):
        payload = {"email": "testuser@example.com", "password": "testpass123"}
        resp = await client.post("/api/auth/login-web", json=payload)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "session_token" in data
        assert data["email"] == "testuser@example.com"
        assert data["nama"] == "Test User"

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        payload = {"email": "testuser@example.com", "password": "wrongpassword"}
        resp = await client.post("/api/auth/login-web", json=payload)
        assert resp.status_code == 401, resp.text

    async def test_login_nonexistent_user(self, client: AsyncClient):
        payload = {"email": "nobody@example.com", "password": "testpass123"}
        resp = await client.post("/api/auth/login-web", json=payload)
        assert resp.status_code == 401, resp.text

    async def test_login_missing_fields(self, client: AsyncClient):
        resp = await client.post("/api/auth/login-web", json={"email": "", "password": ""})
        assert resp.status_code == 400, resp.text


class TestAuthMe:
    """Tests for GET /api/auth/me."""

    async def test_get_me_authenticated(self, client: AsyncClient, auth_headers):
        resp = await client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["email"] == "testuser@example.com"
        assert data["nama"] == "Test User"
        assert "subscription_status" in data
        assert "is_admin" in data

    async def test_get_me_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401, resp.text

    async def test_get_me_invalid_token(self, client: AsyncClient):
        headers = {"Authorization": "Bearer invalidtoken"}
        resp = await client.get("/api/auth/me", headers=headers)
        assert resp.status_code == 401, resp.text


class TestAuthRateLimiting:
    """Verify rate limiting on auth endpoints (IP-based, 10 req/60s)."""

    async def test_register_rate_limit(self, client: AsyncClient):
        """Send many rapid requests — last should be 429."""
        payload = {"email": "ratelimit@test.com", "password": "testpass123"}
        statuses = []
        for _ in range(15):
            resp = await client.post("/api/auth/register", json=payload)
            statuses.append(resp.status_code)
            if resp.status_code == 429:
                break
        # At least one request should be rate limited
        assert 429 in statuses, f"Expected a 429, got statuses: {statuses}"
