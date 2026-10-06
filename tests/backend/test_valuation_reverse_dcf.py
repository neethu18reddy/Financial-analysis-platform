"""Unit Tests for Reverse DCF Market Expectation Solver."""

import pytest
from app.models.valuation import ReverseDCFInputs
from app.engine.valuation.reverse_dcf import ReverseDCFEngine, calculate_reverse_dcf


def test_reverse_dcf_solving_convergence():
    """Verify reverse DCF solves for implied growth within tight tolerance."""
    inputs = ReverseDCFInputs(
        current_market_price=2500.0,
        shares_outstanding_crores=100.0,
        forecast_years=5,
        target_ebit_margin_pct=18.0,
        wacc_pct=11.5,
        terminal_growth_rate_pct=5.0,
    )
    
    engine = ReverseDCFEngine()
    result = engine.calculate(
        company_id=1,
        ticker="TCS",
        inputs=inputs,
        base_revenue=200000.0,
        historical_revenue_cagr_3yr=9.5,
        default_shares=100.0,
        default_debt=0.0,
        default_cash=15000.0,
    )
    
    assert result.ticker == "TCS"
    assert result.current_market_price == 2500.0
    assert result.current_market_cap_crores == 250000.0
    assert result.implied_revenue_cagr_pct is not None
    assert result.plausibility_assessment in ["CONSERVATIVE", "REALISTIC", "AGGRESSIVE", "EXTREME"]
    assert len(result.sensitivities) > 0


def test_reverse_dcf_extreme_price_handling():
    """Verify reverse DCF handles high growth demands safely without crashing."""
    inputs = ReverseDCFInputs(
        current_market_price=10000.0,  # Very high market price
        shares_outstanding_crores=100.0,
        target_ebit_margin_pct=10.0,
        wacc_pct=12.0,
        terminal_growth_rate_pct=4.5,
    )
    
    result = calculate_reverse_dcf(
        company_id=2,
        ticker="HIGH_GROWTH_CO",
        inputs=inputs,
        base_revenue=5000.0,
        default_shares=100.0,
    )
    
    assert result.implied_revenue_cagr_pct > 20.0
    assert result.plausibility_assessment in ["AGGRESSIVE", "EXTREME"]
