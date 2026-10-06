"""Pytest configuration and global fixtures for backend test suite."""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
# Import all models to ensure metadata has all tables
import app.models  # noqa: F401
from app.models.company import Company
from app.engine.ingestion_service import IngestionService
from app.fixtures.seed_data import ALL_FIXTURES


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all database tables and seed test data before tests run."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        c_count = await session.scalar(select(func.count(Company.id)))
        if not c_count or c_count == 0:
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
    yield


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a transactional database session for tests."""
    async with AsyncSessionLocal() as session:
        yield session
