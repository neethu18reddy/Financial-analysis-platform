"""Integration Tests for AI Analyst, PIT, Research Report, and Watchlist Endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_ai_analyst_query_endpoint():
    """Verify POST /api/v1/ai/query endpoint."""
    payload = {
        "ticker": "RELIANCE",
        "question": "What are the primary capital expenditure and 5G network rollout drivers?",
        "include_annual_report_rag": True,
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/ai/query", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["ticker"] == "RELIANCE"
        assert len(data["key_claims"]) > 0
        assert data["confidence_score"] >= 0.85
        assert len(data["supporting_citations"]) > 0


@pytest.mark.asyncio
async def test_said_vs_did_endpoint():
    """Verify GET /api/v1/ai/said-vs-did/{ticker} endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/ai/said-vs-did/TCS")
        assert res.status_code == 200
        data = res.json()
        assert data["ticker"] == "TCS"
        assert data["credibility_score_pct"] >= 80.0
        assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_point_in_time_endpoint():
    """Verify POST /api/v1/ai/point-in-time endpoint."""
    payload = {
        "ticker": "RELIANCE",
        "as_of_year": 2023,
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/ai/point-in-time", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["as_of_year"] == 2023
        assert data["leakage_guard_passed"] is True


@pytest.mark.asyncio
async def test_research_report_endpoint():
    """Verify GET /api/v1/ai/research-report/{id} endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/ai/research-report/1")
        assert res.status_code == 200
        data = res.json()
        assert data["ticker"] == "RELIANCE"
        assert "executive_summary" in data
        assert "dupont_decomposition" in data
        assert "valuation_synthesis" in data


@pytest.mark.asyncio
async def test_watchlist_endpoints():
    """Verify GET /api/v1/watchlist and POST /api/v1/watchlist endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/watchlist")
        assert res.status_code == 200
        items = res.json()
        assert isinstance(items, list)
        assert len(items) >= 1
