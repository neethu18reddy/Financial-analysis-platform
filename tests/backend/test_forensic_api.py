"""Integration tests for Forensic Intelligence REST API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_forensic_summary_api():
    """Verify GET /api/v1/companies/{id}/forensics/summary returns structured multi-period scorecard."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/companies/RELIANCE/forensics/summary?statement_type=CONSOLIDATED")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ticker"] == "RELIANCE"
        assert "overall_forensic_stance" in data
        assert "historical_scorecards" in data
        assert len(data["historical_scorecards"]) > 0

        latest = data["latest_scorecard"]
        assert latest is not None
        assert "piotroski_f_score" in latest
        assert "altman_z_score" in latest
        assert "screening_signals" in latest


@pytest.mark.asyncio
async def test_forensic_piotroski_endpoint():
    """Verify GET /api/v1/companies/{id}/forensics/piotroski returns 9-point breakdown."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/companies/RELIANCE/forensics/piotroski")
        assert resp.status_code == 200
        data = resp.json()
        assert "periods" in data
        assert len(data["periods"]) > 0
        p0 = data["periods"][0]
        assert "piotroski" in p0


@pytest.mark.asyncio
async def test_forensic_beneish_endpoint():
    """Verify GET /api/v1/companies/{id}/forensics/beneish returns 8-variable model output."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/companies/RELIANCE/forensics/beneish")
        assert resp.status_code == 200
        data = resp.json()
        assert data["threshold"] == -1.78
        assert "periods" in data


@pytest.mark.asyncio
async def test_forensic_signals_endpoint():
    """Verify GET /api/v1/companies/{id}/forensics/signals returns anomaly indicators."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/companies/RELIANCE/forensics/signals")
        assert resp.status_code == 200
        data = resp.json()
        assert "periods" in data
        assert len(data["periods"]) > 0
        assert "signals" in data["periods"][0]
