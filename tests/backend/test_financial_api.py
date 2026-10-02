"""Integration tests for Financial Data Engine API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import AsyncSessionLocal
from app.engine.ingestion_service import IngestionService
from app.fixtures.seed_data import ALL_FIXTURES


@pytest.fixture(autouse=True)
async def seed_test_database():
    """Ensure fixtures are ingested into test database before running API tests."""
    async with AsyncSessionLocal() as session:
        ingestion = IngestionService(session)
        for fixture in ALL_FIXTURES:
            comp_data = fixture["company"]
            company = await ingestion.ingest_company(comp_data)
            
            source_docs = []
            for s_data in fixture.get("source_documents", []):
                doc = await ingestion.ingest_source_document(s_data)
                source_docs.append(doc)
            primary_doc = source_docs[0] if source_docs else None

            for p_data in fixture.get("periods", []):
                period = await ingestion.ingest_financial_period(company.id, p_data)
                for is_data in p_data.get("income_statements", []):
                    await ingestion.ingest_income_statement(period, is_data, primary_doc)
                for bs_data in p_data.get("balance_sheets", []):
                    await ingestion.ingest_balance_sheet(period, bs_data, primary_doc)
                for cf_data in p_data.get("cash_flows", []):
                    await ingestion.ingest_cash_flow_statement(period, cf_data, primary_doc)

            for ca_data in fixture.get("corporate_actions", []):
                await ingestion.ingest_corporate_action(company.id, ca_data)

        await session.commit()


@pytest.mark.asyncio
async def test_list_companies_api():
    """Verify company listing endpoint returns companies with proper search filtering."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/companies")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        tickers = [c["ticker"] for c in data]
        assert "RELIANCE" in tickers
        assert "TCS" in tickers

        # Test search filter
        search_res = await client.get("/api/v1/companies?search=Reliance")
        assert search_res.status_code == 200
        search_data = search_res.json()
        assert len(search_data) == 1
        assert search_data[0]["ticker"] == "RELIANCE"


@pytest.mark.asyncio
async def test_get_company_detail_api():
    """Verify company profile and securities resolution."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/companies/RELIANCE")
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "RELIANCE"
        assert data["isin"] == "INE002A01018"
        assert len(data["securities"]) >= 1
        assert data["securities"][0]["symbol"] == "RELIANCE"


@pytest.mark.asyncio
async def test_get_financial_statements_api():
    """Verify multi-period financial statements endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/companies/RELIANCE/statements?statement_type=CONSOLIDATED")
        assert response.status_code == 200
        data = response.json()
        assert data["company"]["ticker"] == "RELIANCE"
        assert data["statement_type"] == "CONSOLIDATED"
        assert len(data["periods_data"]) >= 1

        period_0 = data["periods_data"][0]
        assert period_0["income_statement"] is not None
        assert period_0["balance_sheet"] is not None
        assert period_0["cash_flow"] is not None
        assert period_0["income_statement"]["total_revenue"] > 0


@pytest.mark.asyncio
async def test_get_validation_report_api():
    """Verify validation audit endpoint flags failures accurately."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # TCS should be fully reconciled
        tcs_res = await client.get("/api/v1/companies/TCS/validation-report")
        assert tcs_res.status_code == 200
        tcs_val = tcs_res.json()
        assert tcs_val["total_checks"] > 0
        assert tcs_val["is_fully_reconciled"] is True

        # Broken Balance Sheet Corp should fail
        broken_res = await client.get("/api/v1/companies/SYNTH_BROKEN_BS/validation-report")
        assert broken_res.status_code == 200
        broken_val = broken_res.json()
        assert broken_val["failed_checks"] >= 1
        assert broken_val["is_fully_reconciled"] is False


@pytest.mark.asyncio
async def test_get_sources_api():
    """Verify source registry listing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/sources")
        assert response.status_code == 200
        sources = response.json()
        provider_ids = [s["provider_id"] for s in sources]
        assert "NSE_INDIA" in provider_ids
        assert "BSE_INDIA" in provider_ids
        assert "MCA_XBRL" in provider_ids


@pytest.mark.asyncio
async def test_get_corporate_actions_api():
    """Verify corporate actions endpoint returns splits, bonuses, dividends."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/companies/RELIANCE/corporate-actions")
        assert response.status_code == 200
        actions = response.json()
        assert len(actions) >= 1
        types = [a["action_type"] for a in actions]
        assert "BONUS_ISSUE" in types or "DIVIDEND" in types
