"""Unit tests for WorkingCapitalEngine (DSO, DIO, DPO, CCC, Asset Turnover)."""

import pytest
from app.models.financial_statements import IncomeStatement, BalanceSheet, StatementType
from app.engine.fundamental.working_capital import WorkingCapitalEngine


def test_working_capital_cycles():
    """Verify DSO, DIO, DPO, Cash Conversion Cycle and Liquidity Ratios."""
    inc = IncomeStatement(
        id=1,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        total_revenue=3650.0,
        revenue_from_operations=3650.0,
        cost_of_materials_consumed=1825.0,
        purchases_of_stock_in_trade=0.0,
        changes_in_inventories=0.0
    )
    bal = BalanceSheet(
        id=1,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        trade_receivables=365.0,      # DSO = (365 / 3650) * 365 = 36.5 days
        inventories=182.5,            # DIO = (182.5 / 1825) * 365 = 36.5 days
        trade_payables=91.25,         # DPO = (91.25 / 1825) * 365 = 18.25 -> 18.3 days
        total_assets=7300.0,          # Asset Turnover = 3650 / 7300 = 0.50x
        total_current_assets=1000.0,
        total_current_liabilities=500.0 # Current Ratio = 1000 / 500 = 2.0x, Quick Ratio = (1000 - 182.5) / 500 = 1.64x
    )

    metrics = WorkingCapitalEngine.calculate_all(inc, bal)

    assert abs(metrics["DSO"].value - 36.5) < 0.05
    assert abs(metrics["DIO"].value - 36.5) < 0.05
    assert abs(metrics["DPO"].value - 18.25) < 0.1
    assert abs(metrics["CASH_CONVERSION_CYCLE"].value - 54.75) < 0.2
    assert metrics["ASSET_TURNOVER"].value == 0.50
    assert metrics["CURRENT_RATIO"].value == 2.0
    assert metrics["QUICK_RATIO"].value == 1.64
