"""Unit Tests for Multi-Scenario and 2D Sensitivity Valuation Engines."""

import pytest
from app.models.valuation import ScenarioType
from app.engine.valuation.scenarios import ScenarioValuationEngine, calculate_scenario_analysis
from app.engine.valuation.sensitivity import SensitivityValuationEngine


def test_scenario_analysis_probability_weighting():
    """Verify Bear, Base, Bull scenarios and probability-weighted fair value."""
    engine = ScenarioValuationEngine()
    result = engine.calculate(
        company_id=1,
        ticker="TCS",
        current_market_price=4000.0,
        base_revenue=240000.0,
        shares_outstanding_crores=361.8,
        base_growth_pct=10.0,
        base_margin_pct=25.0,
        base_wacc_pct=10.5,
        base_terminal_growth_pct=5.0,
    )
    
    assert len(result.scenarios) == 3
    bear = next(s for s in result.scenarios if s.scenario_type == ScenarioType.BEAR)
    base = next(s for s in result.scenarios if s.scenario_type == ScenarioType.BASE)
    bull = next(s for s in result.scenarios if s.scenario_type == ScenarioType.BULL)
    
    assert bear.estimated_fair_value_per_share < base.estimated_fair_value_per_share
    assert base.estimated_fair_value_per_share < bull.estimated_fair_value_per_share
    
    expected_weighted = (bear.estimated_fair_value_per_share * 0.25) + (base.estimated_fair_value_per_share * 0.50) + (bull.estimated_fair_value_per_share * 0.25)
    assert round(result.probability_weighted_fair_value, 2) == round(expected_weighted, 2)
    assert result.risk_reward_skew in ["FAVORABLE", "SYMMETRIC", "UNFAVORABLE"]


def test_sensitivity_wacc_vs_terminal_growth_grid():
    """Verify 2D sensitivity matrix structure (5x5) and monotonicity."""
    engine = SensitivityValuationEngine()
    matrix = engine.build_wacc_vs_terminal_growth_matrix(
        company_id=1,
        ticker="TCS",
        current_market_price=4000.0,
        base_revenue=240000.0,
        shares_outstanding_crores=361.8,
        base_wacc_pct=11.0,
        base_terminal_growth_pct=5.0,
    )
    
    assert len(matrix.row_values) == 5
    assert len(matrix.col_values) == 5
    assert len(matrix.grid) == 5
    assert len(matrix.grid[0]) == 5
    
    # As WACC increases (down rows), fair value should decrease
    top_left = matrix.grid[0][0].fair_value_per_share
    bottom_left = matrix.grid[4][0].fair_value_per_share
    assert top_left > bottom_left

    # As terminal growth increases (across columns), fair value should increase
    top_right = matrix.grid[0][4].fair_value_per_share
    assert top_right > top_left


def test_sensitivity_growth_vs_margin_grid():
    """Verify 2D growth vs margin sensitivity matrix."""
    engine = SensitivityValuationEngine()
    matrix = engine.build_growth_vs_margin_matrix(
        company_id=1,
        ticker="TCS",
        current_market_price=4000.0,
        base_revenue=240000.0,
        shares_outstanding_crores=361.8,
        base_growth_pct=12.0,
        base_margin_pct=22.0,
    )
    
    assert len(matrix.row_values) == 5
    assert len(matrix.col_values) == 5
    # As growth and margin expand, fair value expands
    val_low = matrix.grid[0][0].fair_value_per_share
    val_high = matrix.grid[4][4].fair_value_per_share
    assert val_high > val_low
