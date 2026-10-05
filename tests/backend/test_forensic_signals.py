"""Unit tests for granular forensic anomaly screening signals."""

import pytest
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement, StatementType
from app.models.forensic import ForensicRiskLevel
from app.engine.forensic.signals import ForensicSignalsEngine


def test_channel_stuffing_receivables_divergence_signal():
    """Verify that when receivables surge while revenue is flat, a HIGH risk divergence signal is flagged."""
    inc_curr = IncomeStatement(
        id=2, period_id=2, statement_type=StatementType.CONSOLIDATED,
        revenue_from_operations=1050.0, total_revenue=1050.0,  # Rev growth = +5%
        profit_after_tax=100.0
    )
    bal_curr = BalanceSheet(
        id=2, period_id=2, statement_type=StatementType.CONSOLIDATED,
        trade_receivables=300.0, total_assets=2000.0  # Rec growth = +50% (300 vs 200)
    )

    inc_prev = IncomeStatement(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        revenue_from_operations=1000.0, total_revenue=1000.0,
        profit_after_tax=100.0
    )
    bal_prev = BalanceSheet(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        trade_receivables=200.0, total_assets=2000.0
    )

    signals = ForensicSignalsEngine.evaluate_all(
        inc_curr=inc_curr, bal_curr=bal_curr, cf_curr=None,
        inc_prev=inc_prev, bal_prev=bal_prev
    )

    rec_sig = next((s for s in signals if s.signal_key == "RECEIVABLE_REVENUE_DIVERGENCE"), None)
    assert rec_sig is not None
    assert rec_sig.risk_level == ForensicRiskLevel.HIGH
    assert rec_sig.value > 20.0  # Divergence +45%


def test_sloan_accrual_anomaly_signal():
    """Verify Sloan Accrual signal flags high risk when net income heavily outpaces operating cash flow."""
    inc = IncomeStatement(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        profit_after_tax=500.0, total_revenue=2000.0
    )
    bal = BalanceSheet(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        total_assets=3000.0
    )
    cf = CashFlowStatement(
        id=1, period_id=1, statement_type=StatementType.CONSOLIDATED,
        cash_from_operating_activities=50.0  # Accruals = 500 - 50 = 450. (450 / 3000) * 100 = 15% > 10%
    )

    signals = ForensicSignalsEngine.evaluate_all(inc_curr=inc, bal_curr=bal, cf_curr=cf)

    sloan_sig = next((s for s in signals if s.signal_key == "SLOAN_ACCRUAL_ANOMALY"), None)
    assert sloan_sig is not None
    assert sloan_sig.risk_level == ForensicRiskLevel.ELEVATED
    assert sloan_sig.value >= 15.0
