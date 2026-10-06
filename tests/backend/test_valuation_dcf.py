"""Unit Tests for DCF Valuation Engine (FCFF / WACC / Terminal Value Diagnostics)."""

import pytest
from app.models.valuation import (
    DCFValuationInputs,
    TerminalValueMethod,
    ValuationMethod,
)
from app.engine.valuation.dcf import DCFValuationEngine, calculate_dcf_valuation
from app.engine.valuation.base import BaseValuationEngine


def test_wacc_calculation_and_capm():
    """Verify CAPM cost of equity and WACC calculation correctness."""
    ke = BaseValuationEngine.calculate_capm_cost_of_equity(
        risk_free_rate_pct=7.10,
        beta=1.20,
        equity_risk_premium_pct=6.00,
    )
    # Ke = 7.10 + 1.20 * 6.00 = 14.30%
    assert round(ke, 2) == 14.30

    wacc = BaseValuationEngine.calculate_wacc(
        cost_of_equity_pct=14.30,
        pre_tax_cost_of_debt_pct=8.50,
        effective_tax_rate_pct=25.0,  # Kd after tax = 8.5 * 0.75 = 6.375%
        debt_to_capital_pct=20.0,     # 80% equity, 20% debt
    )
    # WACC = (0.80 * 14.30) + (0.20 * 6.375) = 11.44 + 1.275 = 12.715%
    assert round(wacc, 3) == 12.715


def test_gordon_terminal_value_and_guardrails():
    """Verify Gordon Growth formula and rejection of g >= WACC."""
    # TV = (100 * 1.05) / (0.12 - 0.05) = 105 / 0.07 = 1500.0
    tv = BaseValuationEngine.calculate_gordon_terminal_value(
        final_fcf=100.0,
        discount_rate_pct=12.0,
        terminal_growth_rate_pct=5.0,
    )
    assert round(tv, 2) == 1500.0

    # Test singularity error when g >= WACC
    with pytest.raises(ValueError, match="must strictly exceed"):
        BaseValuationEngine.calculate_gordon_terminal_value(
            final_fcf=100.0,
            discount_rate_pct=5.0,
            terminal_growth_rate_pct=5.5,
        )


def test_dcf_full_pipeline_reliance_golden_case():
    """Verify complete DCF valuation calculation for a large-cap company."""
    inputs = DCFValuationInputs(
        forecast_years=5,
        base_revenue=900000.0,
        constant_revenue_growth_pct=10.0,
        target_ebit_margin_pct=18.0,
        effective_tax_rate_pct=25.0,
        reinvestment_rate_pct=30.0,
        wacc_pct=11.5,
        terminal_growth_rate_pct=5.0,
        shares_outstanding_crores=676.5,
        total_debt_crores=300000.0,
        cash_and_investments_crores=150000.0,
    )
    
    engine = DCFValuationEngine()
    result = engine.calculate(
        company_id=1,
        ticker="RELIANCE",
        inputs=inputs,
        current_market_price=2900.0,
    )
    
    assert result.ticker == "RELIANCE"
    assert result.valuation_method == ValuationMethod.DCF_FCFF
    assert len(result.projections) == 5
    assert result.enterprise_value > 0
    assert result.net_debt == 150000.0  # 300000 - 150000
    assert result.estimated_fair_value_per_share > 0
    assert result.terminal_diagnostics.enterprise_value == result.enterprise_value
    assert result.terminal_diagnostics.terminal_value_pct_of_ev > 0
    assert result.upside_downside_pct is not None


def test_dcf_exit_multiple_terminal_value():
    """Verify DCF using Exit Multiple method."""
    inputs = DCFValuationInputs(
        forecast_years=5,
        base_revenue=10000.0,
        constant_revenue_growth_pct=12.0,
        target_ebit_margin_pct=20.0,
        wacc_pct=12.0,
        terminal_value_method=TerminalValueMethod.EXIT_MULTIPLE,
        exit_ev_ebitda_multiple=12.0,
        shares_outstanding_crores=50.0,
        total_debt_crores=2000.0,
        cash_and_investments_crores=1000.0,
    )
    
    result = calculate_dcf_valuation(
        company_id=2,
        ticker="TEST_CO",
        inputs=inputs,
        current_market_price=500.0,
    )
    
    assert result.terminal_diagnostics.implied_exit_ev_ebitda_multiple == 12.0
    assert result.estimated_fair_value_per_share > 0
