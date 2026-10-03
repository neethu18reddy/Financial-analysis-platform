"""Unit tests for DuPontEngine (3-step and 5-step decomposition)."""

import pytest
from app.models.financial_statements import IncomeStatement, BalanceSheet, StatementType
from app.engine.fundamental.dupont import DuPontEngine


def test_dupont_decomposition_math_identity():
    """Verify 3-step and 5-step mathematical identities equal reported ROE."""
    inc = IncomeStatement(
        id=1,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        total_revenue=1000.0,
        revenue_from_operations=1000.0,
        finance_costs=20.0,
        profit_before_tax=180.0,      # EBIT = 180 + 20 = 200
        total_tax_expense=45.0,
        profit_after_tax=135.0,
        net_profit_attributable_to_owners=135.0
    )
    bal = BalanceSheet(
        id=1,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        total_assets=2000.0,
        total_equity=800.0            # Direct reported ROE = 135 / 800 = 16.88%
    )

    res = DuPontEngine.calculate(inc, bal)
    assert res is not None

    # 3-Step:
    # Net Margin = 135 / 1000 = 13.5%
    # Asset Turnover = 1000 / 2000 = 0.50x
    # Leverage = 2000 / 800 = 2.50x
    # Product = 0.135 * 0.50 * 2.50 = 0.16875 -> 16.88%
    d3 = res.dupont_3step
    assert d3 is not None
    assert d3.net_profit_margin == 13.5
    assert d3.asset_turnover == 0.5
    assert d3.financial_leverage == 2.5
    assert d3.roe_calculated == 16.88
    assert d3.roe_reported == 16.88

    # 5-Step:
    # Tax Burden = 135 / 180 = 0.75
    # Interest Burden = 180 / 200 = 0.90
    # Operating Margin = 200 / 1000 = 20.0%
    # Asset Turnover = 0.50
    # Leverage = 2.50
    # Product = 0.75 * 0.90 * 0.20 * 0.50 * 2.50 = 0.16875 -> 16.88%
    d5 = res.dupont_5step
    assert d5 is not None
    assert d5.tax_burden == 0.75
    assert d5.interest_burden == 0.90
    assert d5.operating_margin == 20.0
    assert d5.asset_turnover == 0.5
    assert d5.financial_leverage == 2.5
    assert d5.roe_calculated == 16.88
