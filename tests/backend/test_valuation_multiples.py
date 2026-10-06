"""Unit Tests for Relative Multiples Valuation Engine."""

import pytest
from app.engine.valuation.multiples import MultiplesValuationEngine, calculate_multiples_valuation


def test_multiples_valuation_suite_calculations():
    """Verify calculation of P/E, EV/EBITDA, P/B, EV/Sales implied fair values."""
    engine = MultiplesValuationEngine()
    result = engine.calculate(
        company_id=1,
        ticker="RELIANCE",
        current_market_price=2900.0,
        eps=105.0,
        book_value_per_share=1150.0,
        ebitda_per_share=260.0,
        revenue_per_share=1350.0,
        net_debt_per_share=220.0,
    )
    
    assert result.ticker == "RELIANCE"
    assert len(result.multiples) == 4
    
    # Check each multiple
    pe_item = next(m for m in result.multiples if "P/E" in m.multiple_name)
    assert pe_item.current_multiple == round(2900.0 / 105.0, 2)
    assert pe_item.implied_fair_value_per_share > 0
    
    ev_item = next(m for m in result.multiples if "EV/EBITDA" in m.multiple_name)
    assert ev_item.implied_fair_value_per_share > 0
    
    pb_item = next(m for m in result.multiples if "P/B" in m.multiple_name)
    assert pb_item.implied_fair_value_per_share > 0
    
    assert result.composite_median_fair_value > 0
    assert len(result.methodology_notes) > 0


def test_custom_target_multiples():
    """Verify overriding target multiple yields exact mathematical multiplication."""
    result = calculate_multiples_valuation(
        company_id=2,
        ticker="TEST",
        current_market_price=1000.0,
        eps=50.0,
        book_value_per_share=200.0,
        ebitda_per_share=80.0,
        revenue_per_share=500.0,
    )
    
    engine = MultiplesValuationEngine()
    custom_res = engine.calculate(
        company_id=2,
        ticker="TEST",
        current_market_price=1000.0,
        eps=50.0,
        book_value_per_share=200.0,
        ebitda_per_share=80.0,
        revenue_per_share=500.0,
        custom_target_pe=20.0,
    )
    
    pe_item = next(m for m in custom_res.multiples if "P/E" in m.multiple_name)
    # Fair Value = 50.0 * 20.0 = 1000.0
    assert pe_item.implied_fair_value_per_share == 1000.0
