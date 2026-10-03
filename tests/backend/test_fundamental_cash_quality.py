"""Unit tests for CashQualityEngine (CFO/PAT, FCF/PAT, Sloan Accruals)."""

import pytest
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement, StatementType
from app.engine.fundamental.cash_quality import CashQualityEngine


def test_cash_quality_metrics():
    """Verify CFO/PAT, FCF/PAT, and Sloan Accruals calculations."""
    inc = IncomeStatement(
        id=1,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        total_revenue=1000.0,
        profit_after_tax=100.0,
        net_profit_attributable_to_owners=100.0
    )
    bal = BalanceSheet(
        id=1,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        total_assets=1000.0,
        non_current_borrowings=200.0,
        current_borrowings=0.0
    )
    cf = CashFlowStatement(
        id=1,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        cash_from_operating_activities=120.0,
        capital_expenditure=40.0,
        free_cash_flow=80.0
    )

    metrics = CashQualityEngine.calculate_all(inc, bal, cf)

    # 1. CFO to PAT = 120 / 100 = 1.20x
    assert metrics["CFO_TO_PAT"].value == 1.20
    assert metrics["CFO_TO_PAT"].is_valid is True

    # 2. FCF to PAT = 80 / 100 = 0.80x
    assert metrics["FCF_TO_PAT"].value == 0.80

    # 3. Sloan Accruals = (PAT 100 - CFO 120) / Total Assets 1000 = -20 / 1000 = -2.0%
    assert metrics["SLOAN_ACCRUALS_RATIO"].value == -2.0

    # 4. FCF Margin = 80 / 1000 = 8.0%
    assert metrics["FCF_MARGIN"].value == 8.0

    # 5. CFO to Debt = 120 / 200 = 0.60x
    assert metrics["CFO_TO_DEBT"].value == 0.60
