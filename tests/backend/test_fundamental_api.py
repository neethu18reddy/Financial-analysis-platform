"""Integration tests for Fundamental Analysis API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import AsyncSessionLocal
from app.engine.ingestion_service import IngestionService
from app.fixtures.seed_data import ALL_FIXTURES


@pytest.fixture(autouse=True)
async def seed_fixtures():
    """Seed test database with golden fixtures."""
    async with AsyncSessionLocal() as session:
        ingestion = IngestionService(session)
        for fixture in ALL_FIXTURES:
            comp = await ingestion.ingest_company(fixture["company"])
            source_docs = []
            for s in fixture.get("source_documents", []):
                doc = await ingestion.ingest_source_document(s)
                source_docs.append(doc)
            primary_doc = source_docs[0] if source_docs else None

            for p_data in fixture.get("periods", []):
                period = await ingestion.ingest_financial_period(comp.id, p_data)
                for is_data in p_data.get("income_statements", []):
                    await ingestion.ingest_income_statement(period, is_data, primary_doc)
                for bs_data in p_data.get("balance_sheets", []):
                    await ingestion.ingest_balance_sheet(period, bs_data, primary_doc)
                for cf_data in p_data.get("cash_flows", []):
                    await ingestion.ingest_cash_flow_statement(period, cf_data, primary_doc)
        await session.commit()


@pytest.mark.asyncio
async def test_full_fundamental_analysis_api():
    """Verify /companies/{ticker}/analysis/full endpoint returns complete analysis."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/companies/RELIANCE/analysis/full")
        assert res.status_code == 200
        data = res.json()
        assert data["ticker"] == "RELIANCE"
        assert len(data["periods_analysis"]) >= 2
        
        # Check latest period profitability
        p0 = data["periods_analysis"][0]
        assert "EBITDA_MARGIN" in p0["profitability"]
        assert "ROCE" in p0["profitability"]
        assert "ROE" in p0["profitability"]
        assert p0["profitability"]["ROCE"]["value"] > 0
        
        # Check working capital
        assert "DSO" in p0["working_capital"]
        assert "CASH_CONVERSION_CYCLE" in p0["working_capital"]
        
        # Check DuPont
        assert p0["dupont"] is not None
        assert p0["dupont"]["dupont_3step"] is not None
        assert p0["dupont"]["dupont_5step"] is not None

        # Check CAGR summary
        assert data["cagr_summary"] is not None
        assert data["cagr_summary"]["revenue_cagr"] is not None


@pytest.mark.asyncio
async def test_dupont_endpoint_api():
    """Verify /companies/{ticker}/analysis/dupont returns breakdown."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/companies/TCS/analysis/dupont")
        assert res.status_code == 200
        data = res.json()
        assert data["ticker"] == "TCS"
        assert len(data["periods"]) >= 1
        p = data["periods"][0]
        assert p["dupont"] is not None
        assert p["dupont"]["dupont_5step"]["operating_margin"] > 0


@pytest.mark.asyncio
async def test_common_size_endpoint_api():
    """Verify /companies/{ticker}/analysis/common-size endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/companies/RELIANCE/analysis/common-size")
        assert res.status_code == 200
        data = res.json()
        assert len(data["periods"]) >= 1
        p = data["periods"][0]
        assert p["common_size_income"] is not None
        assert p["common_size_balance"] is not None
        assert len(p["common_size_income"]["items"]) > 5
