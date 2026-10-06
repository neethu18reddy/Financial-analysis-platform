"""Unit Tests for Specialized Financial Institutions (Banks/NBFCs) Valuation Engine."""

import pytest
from app.models.valuation import ValuationMethod
from app.engine.valuation.financial_institutions import BankValuationEngine


def test_bank_ddm_and_justified_pb_valuation():
    """Verify DDM projections, terminal dividend capitalization, and Gordon P/B."""
    engine = BankValuationEngine()
    result = engine.calculate(
        company_id=1,
        ticker="HDFCBANK",
        sector="Financial Services - Private Sector Banking",
        current_market_price=1600.0,
        book_value_per_share=600.0,
        current_roe_pct=17.0,
        shares_outstanding_crores=760.0,
        forecast_years=5,
        loan_growth_pct=15.0,
        cost_of_equity_pct=12.0,
        terminal_growth_pct=5.5,
        tier1_retention_pct=65.0,
    )
    
    assert result.ticker == "HDFCBANK"
    assert result.is_financial_institution is True
    assert result.valuation_method == ValuationMethod.DDM_BANKS
    assert len(result.projections) == 5
    assert result.ddm_fair_value_per_share > 0
    
    # Justified P/B = (ROE - g) / (Ke - g) = (0.17 - 0.055) / (0.12 - 0.055) = 0.115 / 0.065 = 1.769x
    assert round(result.justified_pb_multiple, 2) == 1.77
    assert round(result.justified_pb_fair_value_per_share, 2) == round(600.0 * 1.77, 2)
    assert len(result.methodology_notes) > 0
