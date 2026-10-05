"""Unit tests for Altman Z-Score & Emerging Market Z''-Score Engine."""

import pytest
from app.models.financial_statements import IncomeStatement, BalanceSheet, StatementType
from app.models.forensic import ForensicRiskLevel
from app.engine.forensic.altman import AltmanZScoreEngine


def test_altman_safe_zone_company():
    """Verify Emerging Market Z''-score places healthy, profitable company in Safe Zone."""
    inc = IncomeStatement(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        revenue_from_operations=5000.0, total_revenue=5000.0,
        operating_profit=1000.0, finance_costs=50.0, profit_before_tax=950.0
    )
    bal = BalanceSheet(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        total_assets=6000.0, total_current_assets=3000.0, total_current_liabilities=1000.0,
        other_equity_and_reserves=2500.0, equity_share_capital=500.0,
        total_equity=3000.0, total_liabilities=3000.0
    )

    res = AltmanZScoreEngine.calculate(inc=inc, bal=bal, is_financial_sector=False)

    assert res.is_applicable is True
    assert res.z_score is not None
    assert res.z_score > 2.60
    assert res.zone == "Safe Zone"
    assert res.risk_classification == ForensicRiskLevel.LOW


def test_altman_distress_zone_company():
    """Verify highly leveraged loss-making firm with negative working capital lands in Distress Zone."""
    inc = IncomeStatement(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        revenue_from_operations=1000.0, total_revenue=1000.0,
        operating_profit=-200.0, finance_costs=300.0, profit_before_tax=-500.0
    )
    bal = BalanceSheet(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        total_assets=4000.0, total_current_assets=500.0, total_current_liabilities=2000.0,  # Negative WC = -1500
        other_equity_and_reserves=-500.0, equity_share_capital=500.0,
        total_equity=0.0, total_liabilities=4000.0
    )

    res = AltmanZScoreEngine.calculate(inc=inc, bal=bal, is_financial_sector=False)

    assert res.is_applicable is True
    assert res.z_score is not None
    assert res.z_score < 1.10
    assert res.zone == "Distress Zone"
    assert res.risk_classification == ForensicRiskLevel.HIGH
