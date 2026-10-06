"""Integration Tests for Valuation FastAPI Endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_valuation_summary_endpoint():
    """Verify GET /api/v1/companies/{id}/valuation/summary endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/companies/1/valuation/summary")
        assert response.status_code == 200
        data = response.json()
        assert "company_id" in data
        assert "ticker" in data
        assert "composite_central_fair_value" in data
        assert "composite_fair_value_range_low" in data
        assert "composite_fair_value_range_high" in data
        assert data["dcf_result"] is not None
        assert data["reverse_dcf_result"] is not None
        assert data["multiples_result"] is not None


@pytest.mark.asyncio
async def test_custom_dcf_endpoint():
    """Verify POST /api/v1/companies/{id}/valuation/dcf endpoint."""
    payload = {
        "forecast_years": 5,
        "constant_revenue_growth_pct": 12.0,
        "target_ebit_margin_pct": 19.0,
        "wacc_pct": 11.0,
        "terminal_growth_rate_pct": 5.0,
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/companies/1/valuation/dcf?market_price=2900", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["valuation_method"] == "DCF_FCFF"
        assert data["estimated_fair_value_per_share"] > 0
        assert len(data["projections"]) == 5
        assert "terminal_diagnostics" in data


@pytest.mark.asyncio
async def test_reverse_dcf_endpoint():
    """Verify POST /api/v1/companies/{id}/valuation/reverse-dcf endpoint."""
    payload = {
        "current_market_price": 2800.0,
        "target_ebit_margin_pct": 18.5,
        "wacc_pct": 11.2,
        "terminal_growth_rate_pct": 5.0,
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/companies/1/valuation/reverse-dcf", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["current_market_price"] == 2800.0
        assert "implied_revenue_cagr_pct" in data
        assert "plausibility_assessment" in data


@pytest.mark.asyncio
async def test_multiples_and_sensitivity_endpoints():
    """Verify relative multiples and 2D sensitivity matrix endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Multiples
        resp_mult = await ac.get("/api/v1/companies/1/valuation/multiples?market_price=2900")
        assert resp_mult.status_code == 200
        data_mult = resp_mult.json()
        assert len(data_mult["multiples"]) >= 4

        # WACC vs TG Sensitivity
        resp_sens = await ac.post("/api/v1/companies/1/valuation/sensitivity/wacc-terminal-growth?base_wacc_pct=11.2&base_terminal_growth_pct=5.0")
        assert resp_sens.status_code == 200
        data_sens = resp_sens.json()
        assert len(data_sens["grid"]) == 5
        assert len(data_sens["grid"][0]) == 5
