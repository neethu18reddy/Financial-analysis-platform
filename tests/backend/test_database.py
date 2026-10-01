"""Tests for database engine, connectivity, and session factory."""

import pytest
from sqlalchemy import text
from backend.app.db.session import engine, check_database_connectivity, get_db
from backend.app.db.base import Base


@pytest.mark.asyncio
async def test_database_connectivity_check():
    """Verifies that check_database_connectivity returns healthy status."""
    health_result = await check_database_connectivity()
    assert isinstance(health_result, dict)
    assert health_result["status"] == "healthy"
    assert health_result["connected"] is True
    assert health_result["error"] is None
    assert health_result["dialect"] in ["sqlite", "postgresql"]


@pytest.mark.asyncio
async def test_database_direct_execution():
    """Verifies direct SQL query execution on the async database engine."""
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 42 AS answer"))
        row = result.mappings().first()
        assert row is not None
        assert row["answer"] == 42


@pytest.mark.asyncio
async def test_get_db_session_generator():
    """Verifies that the get_db generator yields an active AsyncSession."""
    async for session in get_db():
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1
        break


def test_base_metadata_registry():
    """Verifies that declarative Base has metadata configured."""
    assert Base.metadata is not None
