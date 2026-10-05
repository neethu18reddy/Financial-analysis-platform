"""Unit tests for Beneish M-Score 8-Variable Forensic Engine."""

import pytest
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement, StatementType
from app.models.forensic import ForensicRiskLevel
from app.engine.forensic.beneish import BeneishMScoreEngine


def test_beneish_normal_company():
    """Verify Beneish M-Score on a standard stable company (Low Risk)."""
    inc_curr = IncomeStatement(
        id=2, period_id=2, statement_type=StatementType.CONSOLIDATED,
        revenue_from_operations=1100.0, total_revenue=1100.0,
        cost_of_materials_consumed=550.0, employee_benefit_expenses=110.0,
        depreciation_and_amortization=50.0, other_expenses=110.0,
        profit_after_tax=180.0
    )
    bal_curr = BalanceSheet(
        id=2, period_id=2, statement_type=StatementType.CONSOLIDATED,
        trade_receivables=110.0, total_assets=2200.0,
        total_current_assets=600.0, property_plant_equipment=1100.0,
        non_current_borrowings=200.0, current_borrowings=50.0
    )
    cf_curr = CashFlowStatement(
        id=2, period_id=2, statement_type=StatementType.CONSOLIDATED,
        cash_from_operating_activities=200.0
    )

    inc_prev = IncomeStatement(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        revenue_from_operations=1000.0, total_revenue=1000.0,
        cost_of_materials_consumed=500.0, employee_benefit_expenses=100.0,
        depreciation_and_amortization=45.0, other_expenses=100.0,
        profit_after_tax=160.0
    )
    bal_prev = BalanceSheet(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        trade_receivables=100.0, total_assets=2000.0,
        total_current_assets=550.0, property_plant_equipment=1000.0,
        non_current_borrowings=200.0, current_borrowings=50.0
    )

    res = BeneishMScoreEngine.calculate(
        inc_curr=inc_curr, bal_curr=bal_curr, cf_curr=cf_curr,
        inc_prev=inc_prev, bal_prev=bal_prev, is_financial_sector=False
    )

    assert res.is_applicable is True
    assert res.m_score is not None
    assert res.m_score <= -1.78
    assert res.risk_classification == ForensicRiskLevel.LOW
    assert "DSRI" in res.variables
    assert abs(res.variables["DSRI"].value - 1.0) < 0.05
    assert abs(res.variables["SGI"].value - 1.1) < 0.05


def test_beneish_financial_sector_inapplicable():
    """Verify Beneish M-Score is safely marked NOT_APPLICABLE for banking/financial institutions."""
    res = BeneishMScoreEngine.calculate(
        inc_curr=None, bal_curr=None, cf_curr=None,
        inc_prev=None, bal_prev=None, is_financial_sector=True
    )
    assert res.is_applicable is False
    assert res.risk_classification == ForensicRiskLevel.NOT_APPLICABLE
    assert "Banking" in (res.inapplicable_reason or "")
