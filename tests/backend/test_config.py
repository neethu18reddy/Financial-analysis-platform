"""Tests for application settings and configuration management."""

import pytest
from backend.app.core.config import Settings


def test_default_settings():
    """Verifies default settings structure and critical variables."""
    s = Settings()
    assert s.PROJECT_NAME == "Indian Equities Fundamental Analysis Platform"
    assert s.VERSION == "0.1.0"
    assert s.API_V1_STR == "/api/v1"
    assert s.BACKEND_PORT == 8000
    assert isinstance(s.CORS_ORIGINS, list)
    assert len(s.CORS_ORIGINS) >= 1
    assert s.DATABASE_URL.startswith("sqlite") or s.DATABASE_URL.startswith("postgresql")


def test_cors_origins_parsing():
    """Verifies that comma-separated string CORS origins are correctly parsed."""
    s = Settings(CORS_ORIGINS="http://localhost:3000, http://localhost:8080")
    assert "http://localhost:3000" in s.CORS_ORIGINS
    assert "http://localhost:8080" in s.CORS_ORIGINS
