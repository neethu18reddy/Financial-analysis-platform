"""Tests for Institutional Research Report Generator and Watchlist Engine."""

import pytest
from app.db.session import AsyncSessionLocal
from app.engine.ai.research_report_generator import CompanyResearchReportGenerator
from app.engine.ai.watchlist_engine import WatchlistEngine


@pytest.mark.asyncio
async def test_company_research_report_generator():
    """Verify generation of comprehensive 14-section institutional research report."""
    async with AsyncSessionLocal() as session:
        generator = CompanyResearchReportGenerator(session)
        report = await generator.generate_report(company_id=1)

        assert report.ticker == "RELIANCE"
        assert report.legal_name is not None
        assert len(report.executive_summary) > 50
        assert "cagr_summary" in report.growth_analysis
        assert "cash_quality_metrics" in report.cash_flow_quality
        assert "composite_central_fair_value" in report.valuation_synthesis
        assert len(report.annual_report_evidence) >= 1
        assert len(report.research_caveats_and_uncertainty) >= 2


@pytest.mark.asyncio
async def test_watchlist_engine_operations_and_alerts():
    """Verify watchlist additions, deletions, and automated metric alert screening."""
    async with AsyncSessionLocal() as session:
        engine = WatchlistEngine(session)

        # 1. List initial seeds
        items = await engine.list_watchlist()
        assert len(items) >= 3
        tickers = [i.ticker for i in items]
        assert "RELIANCE" in tickers
        assert "TCS" in tickers

        # 2. Verify alert presence
        ril_item = next(i for i in items if i.ticker == "RELIANCE")
        assert len(ril_item.active_alerts) >= 1

        # 3. Add custom item
        added = await engine.add_to_watchlist("INFY", notes="Observing BFSI demand")
        assert added.ticker == "INFY"

        # 4. Remove item
        removed = await engine.remove_from_watchlist("INFY")
        assert removed is True
