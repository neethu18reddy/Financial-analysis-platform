"""Unit tests for deterministic financial validator engine."""

import pytest
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement, StatementType
from app.models.financial_period import FinancialPeriod, PeriodType, ReportingStandard, FinancialUnit
from app.models.validation import ValidationStatus, ValidationCategory
from app.engine.validator import DeterministicValidator
from datetime import date


def test_balance_sheet_reconciliation_valid():
    """Test that a perfectly balanced balance sheet passes all reconciliation checks."""
    bs = BalanceSheet(
        id=1,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        total_non_current_assets=700.0,
        total_current_assets=300.0,
        total_assets=1000.0,
        total_equity=500.0,
        total_non_current_liabilities=300.0,
        total_current_liabilities=200.0,
        total_liabilities=500.0,
        total_equity_and_liabilities=1000.0
    )
    results = DeterministicValidator.validate_balance_sheet(bs)
    assert len(results) == 3
    assert all(r.status == ValidationStatus.PASSED for r in results)
    assert results[0].rule_name == "BS_EQUITY_LIABILITIES_EQUAL_ASSETS"
    assert results[0].discrepancy == 0.0


def test_balance_sheet_reconciliation_fails_on_imbalance():
    """Test that an imbalanced balance sheet triggers deterministic failure without silent repair."""
    bs = BalanceSheet(
        id=2,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        total_non_current_assets=700.0,
        total_current_assets=300.0,
        total_assets=1000.0,
        total_equity=500.0,
        total_non_current_liabilities=250.0,  # Sum is 950 != 1000
        total_current_liabilities=200.0,
        total_liabilities=450.0,
        total_equity_and_liabilities=950.0
    )
    results = DeterministicValidator.validate_balance_sheet(bs)
    failed_results = [r for r in results if r.status == ValidationStatus.FAILED]
    assert len(failed_results) >= 1
    assert any(r.rule_name == "BS_EQUITY_LIABILITIES_EQUAL_ASSETS" for r in failed_results)
    assert failed_results[0].discrepancy == 50.0


def test_cash_flow_continuity_reconciliation():
    """Test cash flow beginning + net change == ending cash."""
    cf_valid = CashFlowStatement(
        id=1,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        cash_from_operating_activities=150.0,
        cash_from_investing_activities=-80.0,
        cash_from_financing_activities=-30.0,
        net_increase_in_cash=40.0,
        foreign_exchange_effect=0.0,
        cash_beginning_of_period=100.0,
        cash_end_of_period=140.0
    )
    results = DeterministicValidator.validate_cash_flow(cf_valid)
    assert len(results) == 2
    assert all(r.status == ValidationStatus.PASSED for r in results)


def test_cash_flow_continuity_detects_gap():
    """Test cash flow continuity failure detection."""
    cf_broken = CashFlowStatement(
        id=2,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        cash_from_operating_activities=150.0,
        cash_from_investing_activities=-80.0,
        cash_from_financing_activities=-30.0,
        net_increase_in_cash=40.0,
        foreign_exchange_effect=0.0,
        cash_beginning_of_period=100.0,
        cash_end_of_period=200.0  # Intentional discrepancy: 100 + 40 = 140 != 200
    )
    results = DeterministicValidator.validate_cash_flow(cf_broken)
    continuity_res = next(r for r in results if r.rule_name == "CF_CASH_CONTINUITY")
    assert continuity_res.status == ValidationStatus.FAILED
    assert continuity_res.discrepancy == 60.0


def test_income_statement_math_validation():
    """Test revenue and PAT math reconciliation."""
    inc = IncomeStatement(
        id=1,
        period_id=1,
        statement_type=StatementType.CONSOLIDATED,
        revenue_from_operations=1000.0,
        other_income=50.0,
        total_revenue=1050.0,
        total_expenses=800.0,
        profit_before_exceptional_items_and_tax=250.0,
        exceptional_items=0.0,
        profit_before_tax=250.0,
        total_tax_expense=62.5,
        profit_after_tax=187.5,
        net_profit_attributable_to_owners=187.5
    )
    results = DeterministicValidator.validate_income_statement(inc)
    assert all(r.status == ValidationStatus.PASSED for r in results)


def test_period_chronology_validation():
    """Test chronological period ordering and detection of inverted periods."""
    p1 = FinancialPeriod(
        id=1,
        company_id=1,
        fiscal_year=2023,
        period_label="FY 2022-23",
        period_type=PeriodType.ANNUAL,
        start_date=date(2022, 4, 1),
        end_date=date(2023, 3, 31),
        canonical_unit=FinancialUnit.CRORES
    )
    p2 = FinancialPeriod(
        id=2,
        company_id=1,
        fiscal_year=2024,
        period_label="FY 2023-24",
        period_type=PeriodType.ANNUAL,
        start_date=date(2023, 4, 1),
        end_date=date(2024, 3, 31),
        canonical_unit=FinancialUnit.CRORES
    )
    # Valid chronology
    res_valid = DeterministicValidator.validate_period_chronology([p1, p2])
    assert len(res_valid) == 1
    assert res_valid[0].status == ValidationStatus.PASSED

    # Inverted chronology
    res_invalid = DeterministicValidator.validate_period_chronology([p2, p1])
    # Sorted chronologically internally, but if dates are conflicting:
    p_bad = FinancialPeriod(
        id=3,
        company_id=1,
        fiscal_year=2025,
        period_label="FY Bad",
        period_type=PeriodType.ANNUAL,
        start_date=date(2022, 1, 1),
        end_date=date(2022, 1, 2),  # Earlier end date
        canonical_unit=FinancialUnit.CRORES
    )
    res_bad = DeterministicValidator.validate_period_chronology([p1, p_bad])
    assert any(r.status == ValidationStatus.FAILED for r in res_bad)
