"""Unit tests for ProfitabilityEngine calculations."""

import pytest
from app.models.financial_statements import IncomeStatement, BalanceSheet, StatementType
from app.engine.fundamental.profitability import ProfitabilityEngine


def test_profitability_margins_normal():
    """Verify gross margin, EBITDA margin, EBIT margin, and PAT margin calculations."""
    inc = IncomeStatement(
        id=1,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        revenue_from_operations=1000.0,
        other_income=50.0,
        total_revenue=1050.0,
        cost_of_materials_consumed=400.0,
        purchases_of_stock_in_trade=100.0,
        changes_in_inventories=0.0,
        employee_benefit_expenses=150.0,
        finance_costs=20.0,
        depreciation_and_amortization=30.0,
        other_expenses=100.0,
        total_expenses=800.0,
        profit_before_tax=250.0,
        total_tax_expense=62.5,
        profit_after_tax=187.5,
        net_profit_attributable_to_owners=187.5
    )
    bal = BalanceSheet(
        id=1,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        total_assets=2000.0,
        total_equity=1200.0,
        total_current_liabilities=300.0,
        total_non_current_liabilities=500.0,
        non_current_borrowings=400.0,
        current_borrowings=100.0,
        cash_and_cash_equivalents=200.0,
        bank_balances_other=100.0
    )

    metrics = ProfitabilityEngine.calculate_all(inc, bal)

    # 1. Gross Margin: (1000 - 500) / 1000 = 50.0%
    assert metrics["GROSS_MARGIN"].value == 50.0
    assert metrics["GROSS_MARGIN"].is_valid is True

    # 2. EBITDA: PBT (250) + Finance (20) + D&A (30) = 300. Margin: 300 / 1050 = 28.57%
    assert metrics["EBITDA_MARGIN"].value == 28.57

    # 3. EBIT: PBT (250) + Finance (20) = 270. Margin: 270 / 1050 = 25.71%
    assert metrics["EBIT_MARGIN"].value == 25.71

    # 4. PAT Margin: 187.5 / 1050 = 17.86%
    assert metrics["PAT_MARGIN"].value == 17.86

    # 5. ROA: 187.5 / 2000 = 9.38%
    assert metrics["ROA"].value == 9.38

    # 6. ROE: 187.5 / 1200 = 15.62%
    assert abs(metrics["ROE"].value - 15.625) < 0.02

    # 7. ROCE: EBIT (270) / (Total Assets 2000 - Current Liab 300) = 270 / 1700 = 15.88%
    assert metrics["ROCE"].value == 15.88

    # 8. ROIC: Invested Capital = Equity (1200) + Debt (500) - Cash (300) = 1400. NOPAT = EBIT (270) * (1 - 62.5/250 = 0.75) = 202.5.
    # ROIC = 202.5 / 1400 = 14.46%
    assert metrics["ROIC"].value == 14.46


def test_profitability_zero_revenue_guardrail():
    """Verify zero denominator safeguards for empty or negative revenues."""
    inc_zero = IncomeStatement(
        id=2,
        period_id=2,
        statement_type=StatementType.CONSOLIDATED,
        revenue_from_operations=0.0,
        total_revenue=0.0,
        profit_before_tax=0.0
    )
    metrics = ProfitabilityEngine.calculate_all(inc_zero, None)
    assert metrics["GROSS_MARGIN"].is_valid is False
    assert metrics["GROSS_MARGIN"].value is None
    assert metrics["EBITDA_MARGIN"].is_valid is False
