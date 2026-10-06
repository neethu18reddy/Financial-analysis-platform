"""Pytest configuration and global fixtures for backend test suite."""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
# Import all models to ensure metadata has all tables
import app.models  # noqa: F401


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all database tables before tests run."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a transactional database session for tests."""
    async with AsyncSessionLocal() as session:
        yield session
