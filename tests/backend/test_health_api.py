"""Tests for Health and Root API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.config import settings


@pytest.mark.asyncio
async def test_root_probe_endpoint():
    """Verifies the root GET / probe endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "online"
        assert payload["service"] == settings.PROJECT_NAME
        assert payload["version"] == settings.VERSION
        assert payload["docs"] == f"{settings.API_V1_STR}/docs"


@pytest.mark.asyncio
async def test_api_v1_health_endpoint():
    """Verifies the primary /api/v1/health endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(f"{settings.API_V1_STR}/health")
        assert response.status_code == 200
        payload = response.json()

        assert payload["status"] == "healthy"
        assert payload["project_name"] == settings.PROJECT_NAME
        assert payload["version"] == settings.VERSION
        assert payload["environment"] == settings.ENVIRONMENT

        # Database health block
        assert "database" in payload
        assert payload["database"]["status"] == "healthy"
        assert payload["database"]["connected"] is True
        assert payload["database"]["dialect"] in ["sqlite", "postgresql"]

        # System info block
        assert "system_info" in payload
        assert "python_version" in payload["system_info"]
        assert "os" in payload["system_info"]

        # Custom response headers injected by middleware
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time-Ms" in response.headers
