"""Tests for global error handling and exception formatting."""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_404_not_found_handling():
    """Verifies that non-existent routes return structured JSON error responses."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/non-existent-api-endpoint")
        assert response.status_code == 404
        payload = response.json()
        assert payload["success"] is False
        assert "error" in payload
        assert payload["error"]["code"] == 404
        assert "request_id" in payload
