"""Unit tests for Piotroski 9-Point F-Score Forensic Engine."""

import pytest
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement, StatementType
from app.models.forensic import ForensicRiskLevel
from app.engine.forensic.piotroski import PiotroskiFScoreEngine


def test_piotroski_strong_company():
    """Verify Piotroski F-Score produces a high score (8 or 9) on fundamentally expanding firm."""
    inc_curr = IncomeStatement(
        id=2, period_id=2, statement_type=StatementType.CONSOLIDATED,
        revenue_from_operations=1500.0, total_revenue=1500.0,
        cost_of_materials_consumed=600.0, depreciation_and_amortization=60.0,
        profit_after_tax=300.0
    )
    bal_curr = BalanceSheet(
        id=2, period_id=2, statement_type=StatementType.CONSOLIDATED,
        total_assets=2500.0, total_current_assets=1200.0, total_current_liabilities=400.0,
        non_current_borrowings=100.0, equity_share_capital=100.0
    )
    cf_curr = CashFlowStatement(
        id=2, period_id=2, statement_type=StatementType.CONSOLIDATED,
        cash_from_operating_activities=350.0  # CFO > Net Income (350 > 300)
    )

    inc_prev = IncomeStatement(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        revenue_from_operations=1000.0, total_revenue=1000.0,
        cost_of_materials_consumed=500.0, depreciation_and_amortization=50.0,
        profit_after_tax=150.0
    )
    bal_prev = BalanceSheet(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        total_assets=2000.0, total_current_assets=800.0, total_current_liabilities=400.0,
        non_current_borrowings=200.0, equity_share_capital=100.0
    )

    res = PiotroskiFScoreEngine.calculate(
        inc_curr=inc_curr, bal_curr=bal_curr, cf_curr=cf_curr,
        inc_prev=inc_prev, bal_prev=bal_prev
    )

    assert res.is_applicable is True
    assert res.f_score >= 8
    assert res.risk_classification == ForensicRiskLevel.LOW
    assert len(res.signals) == 9
    assert res.profitability_score == 4  # ROA>0, CFO>0, ROA_up, CFO>NI


def test_piotroski_distressed_company():
    """Verify Piotroski F-Score on loss-making, deteriorating firm produces a low score."""
    inc_curr = IncomeStatement(
        id=2, period_id=2, statement_type=StatementType.CONSOLIDATED,
        revenue_from_operations=800.0, total_revenue=800.0,
        cost_of_materials_consumed=600.0, depreciation_and_amortization=50.0,
        profit_after_tax=-100.0
    )
    bal_curr = BalanceSheet(
        id=2, period_id=2, statement_type=StatementType.CONSOLIDATED,
        total_assets=2000.0, total_current_assets=400.0, total_current_liabilities=800.0,
        non_current_borrowings=600.0, equity_share_capital=200.0  # Dilution (200 > 100)
    )
    cf_curr = CashFlowStatement(
        id=2, period_id=2, statement_type=StatementType.CONSOLIDATED,
        cash_from_operating_activities=-50.0
    )

    inc_prev = IncomeStatement(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        revenue_from_operations=1000.0, total_revenue=1000.0,
        cost_of_materials_consumed=600.0, depreciation_and_amortization=50.0,
        profit_after_tax=50.0
    )
    bal_prev = BalanceSheet(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        total_assets=2000.0, total_current_assets=600.0, total_current_liabilities=600.0,
        non_current_borrowings=400.0, equity_share_capital=100.0
    )

    res = PiotroskiFScoreEngine.calculate(
        inc_curr=inc_curr, bal_curr=bal_curr, cf_curr=cf_curr,
        inc_prev=inc_prev, bal_prev=bal_prev
    )

    assert res.is_applicable is True
    assert res.f_score <= 3
    assert res.risk_classification == ForensicRiskLevel.HIGH
