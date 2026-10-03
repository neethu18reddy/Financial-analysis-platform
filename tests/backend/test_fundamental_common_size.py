"""Unit tests for CommonSizeEngine vertical percentage statements."""

import pytest
from app.models.financial_statements import IncomeStatement, BalanceSheet, StatementType
from app.engine.fundamental.common_size import CommonSizeEngine


def test_common_size_income_and_balance():
    """Verify common-size percentage calculations."""
    inc = IncomeStatement(
        id=1,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        revenue_from_operations=900.0,
        other_income=100.0,
        total_revenue=1000.0,
        cost_of_materials_consumed=400.0,
        employee_benefit_expenses=200.0,
        total_expenses=800.0,
        profit_before_tax=200.0,
        total_tax_expense=50.0,
        profit_after_tax=150.0,
        net_profit_attributable_to_owners=150.0
    )
    bal = BalanceSheet(
        id=1,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        total_non_current_assets=600.0,
        total_current_assets=400.0,
        total_assets=1000.0,
        total_equity=500.0,
        total_non_current_liabilities=300.0,
        total_current_liabilities=200.0,
        total_liabilities=500.0
    )

    cs_inc = CommonSizeEngine.calculate_income_statement(inc)
    assert cs_inc is not None
    assert cs_inc.base_revenue == 1000.0
    # Revenue from ops is 90%
    rev_item = next(i for i in cs_inc.items if i.line_item_key == "revenue_from_operations")
    assert rev_item.percentage_of_base == 90.0
    # Total Expenses is 80%
    exp_item = next(i for i in cs_inc.items if i.line_item_key == "total_expenses")
    assert exp_item.percentage_of_base == 80.0

    cs_bal = CommonSizeEngine.calculate_balance_sheet(bal)
    assert cs_bal is not None
    assert cs_bal.base_assets == 1000.0
    # Total Non-current assets is 60%
    nca_item = next(i for i in cs_bal.items if i.line_item_key == "total_non_current_assets")
    assert nca_item.percentage_of_base == 60.0
    # Equity is 50%
    eq_item = next(i for i in cs_bal.items if i.line_item_key == "total_equity")
    assert eq_item.percentage_of_base == 50.0
