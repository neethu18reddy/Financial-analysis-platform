"""Tests for Management Said vs Did and Point-in-Time Future-Leakage Prevention."""

import pytest
from app.db.session import AsyncSessionLocal
from app.engine.ai.said_vs_did_engine import SaidVsDidEngine
from app.engine.ai.ai_analyst_service import AIAnalystService
from app.models.ai_analyst import PointInTimeAnalysisRequest


@pytest.mark.asyncio
async def test_said_vs_did_engine_tracking():
    """Verify management guidance tracking and credibility score calculation."""
    async with AsyncSessionLocal() as session:
        engine = SaidVsDidEngine(session)
        
        # Test Reliance Said vs Did
        resp_ril = await engine.get_said_vs_did("RELIANCE")
        assert resp_ril.ticker == "RELIANCE"
        assert resp_ril.total_commitments >= 2
        assert resp_ril.credibility_score_pct >= 80.0
        assert any(item.category.value == "CAPEX_EXPANSION" for item in resp_ril.items)

        # Test TCS Buyback
        resp_tcs = await engine.get_said_vs_did("TCS")
        assert resp_tcs.ticker == "TCS"
        assert any(item.category.value == "DIVIDEND_PAYOUT" and item.delivery_status.value == "MET" for item in resp_tcs.items)


@pytest.mark.asyncio
async def test_point_in_time_future_leakage_prevention():
    """Verify that Point-in-Time analysis as of FY23 strictly excludes FY24 data."""
    async with AsyncSessionLocal() as session:
        service = AIAnalystService(session)

        req = PointInTimeAnalysisRequest(
            ticker="RELIANCE",
            as_of_year=2023,
            custom_question="Evaluate balance sheet and leverage as of FY23",
        )
        pit_resp = await service.run_point_in_time_simulation(req)

        assert pit_resp.as_of_year == 2023
        assert pit_resp.leakage_guard_passed is True
        assert all(y <= 2023 for y in pit_resp.available_fiscal_years)
        # Any future periods present in DB must be explicitly listed in future_data_excluded
        assert all(y > 2023 for y in pit_resp.future_data_excluded)
        assert 2024 in pit_resp.future_data_excluded
