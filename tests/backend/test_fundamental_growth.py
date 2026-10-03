"""Unit tests for GrowthEngine YoY and multi-year CAGR calculations."""

import pytest
from app.engine.fundamental.growth import GrowthEngine


def test_yoy_growth_positive_and_negative():
    """Verify standard YoY percentage calculations."""
    # Growth from 100 to 125 (+25%)
    assert GrowthEngine.calculate_yoy(125.0, 100.0) == 25.0

    # Decline from 100 to 80 (-20%)
    assert GrowthEngine.calculate_yoy(80.0, 100.0) == -20.0

    # From 0 base -> None (division by zero protected)
    assert GrowthEngine.calculate_yoy(100.0, 0.0) is None
    assert GrowthEngine.calculate_yoy(100.0, None) is None


def test_cagr_calculation_normal_and_guardrails():
    """Verify CAGR mathematical formula and edge-case guards."""
    # Doubling over 3 years: 100 -> 200 over 3 yrs = (2)^(1/3) - 1 = 25.99%
    cagr_3yr = GrowthEngine.calculate_cagr(200.0, 100.0, 3)
    assert cagr_3yr == 25.99

    # 1 year growth = standard YoY: 100 -> 115 over 1 yr = 15.0%
    cagr_1yr = GrowthEngine.calculate_cagr(115.0, 100.0, 1)
    assert cagr_1yr == 15.0

    # Non-positive base value guardrail
    assert GrowthEngine.calculate_cagr(100.0, 0.0, 2) is None
    assert GrowthEngine.calculate_cagr(100.0, -50.0, 2) is None

    # Zero years guardrail
    assert GrowthEngine.calculate_cagr(100.0, 80.0, 0) is None
