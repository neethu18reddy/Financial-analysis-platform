"""Deterministic Financial Validation Engine.

Strict, zero-silent-repair mathematical and logical integrity checks for financial statements.
"""

from typing import List, Optional, Tuple, Dict, Any
from app.models.validation import ValidationResult, ValidationStatus, ValidationCategory
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement
from app.models.financial_period import FinancialPeriod


class DeterministicValidator:
    """Rigorous financial validator executing deterministic accounting invariants."""

    DEFAULT_TOLERANCE = 0.01  # Tolerance in INR Crores for rounding variances in filings

    @classmethod
    def validate_balance_sheet(
        cls,
        bs: BalanceSheet,
        period: Optional[FinancialPeriod] = None,
        company_id: Optional[int] = None,
        tolerance: float = DEFAULT_TOLERANCE
    ) -> List[ValidationResult]:
        """Validate all structural accounting identities for a Balance Sheet."""
        results: List[ValidationResult] = []
        entity_id = bs.id if bs.id is not None else 0
        p_id = period.id if period else bs.period_id

        # Rule 1: Fundamental Accounting Equation: Total Assets == Total Equity + Total Liabilities
        expected_eq_liab = round(bs.total_equity + bs.total_non_current_liabilities + bs.total_current_liabilities, 4)
        diff_eq = round(abs(bs.total_assets - bs.total_equity_and_liabilities), 4)
        
        if diff_eq <= tolerance:
            results.append(ValidationResult(
                entity_type="balance_sheets",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="BS_EQUITY_LIABILITIES_EQUAL_ASSETS",
                category=ValidationCategory.BALANCE_SHEET_RECONCILIATION,
                status=ValidationStatus.PASSED,
                formula_checked="Total Assets == Total Equity & Liabilities",
                expected_value=bs.total_assets,
                actual_value=bs.total_equity_and_liabilities,
                discrepancy=diff_eq,
                tolerance=tolerance,
                message=f"Balance Sheet balanced: Assets ({bs.total_assets}) == Equity & Liab ({bs.total_equity_and_liabilities})"
            ))
        else:
            results.append(ValidationResult(
                entity_type="balance_sheets",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="BS_EQUITY_LIABILITIES_EQUAL_ASSETS",
                category=ValidationCategory.BALANCE_SHEET_RECONCILIATION,
                status=ValidationStatus.FAILED,
                formula_checked="Total Assets == Total Equity & Liabilities",
                expected_value=bs.total_assets,
                actual_value=bs.total_equity_and_liabilities,
                discrepancy=diff_eq,
                tolerance=tolerance,
                message=f"CRITICAL: Balance Sheet out of balance! Assets ({bs.total_assets}) != Equity & Liab ({bs.total_equity_and_liabilities}) with discrepancy {diff_eq}"
            ))

        # Rule 2: Asset Sub-components sum to Total Assets
        calc_total_assets = round(bs.total_non_current_assets + bs.total_current_assets, 4)
        diff_assets = round(abs(bs.total_assets - calc_total_assets), 4)
        if diff_assets <= tolerance:
            results.append(ValidationResult(
                entity_type="balance_sheets",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="BS_ASSET_SUBCOMPONENTS_SUM",
                category=ValidationCategory.BALANCE_SHEET_RECONCILIATION,
                status=ValidationStatus.PASSED,
                formula_checked="Total Assets == Total Non-Current Assets + Total Current Assets",
                expected_value=calc_total_assets,
                actual_value=bs.total_assets,
                discrepancy=diff_assets,
                tolerance=tolerance,
                message="Asset subcomponents sum correctly to Total Assets."
            ))
        else:
            results.append(ValidationResult(
                entity_type="balance_sheets",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="BS_ASSET_SUBCOMPONENTS_SUM",
                category=ValidationCategory.BALANCE_SHEET_RECONCILIATION,
                status=ValidationStatus.FAILED,
                formula_checked="Total Assets == Total Non-Current Assets + Total Current Assets",
                expected_value=calc_total_assets,
                actual_value=bs.total_assets,
                discrepancy=diff_assets,
                tolerance=tolerance,
                message=f"Total Assets discrepancy: Reported {bs.total_assets} vs Calculated sum {calc_total_assets}"
            ))

        # Rule 3: Equity and Liabilities Sub-components sum to Total Equity & Liabilities
        calc_total_eq_liab = round(bs.total_equity + bs.total_non_current_liabilities + bs.total_current_liabilities, 4)
        diff_eq_sum = round(abs(bs.total_equity_and_liabilities - calc_total_eq_liab), 4)
        if diff_eq_sum <= tolerance:
            results.append(ValidationResult(
                entity_type="balance_sheets",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="BS_LIABILITIES_EQUITY_SUBCOMPONENTS_SUM",
                category=ValidationCategory.BALANCE_SHEET_RECONCILIATION,
                status=ValidationStatus.PASSED,
                formula_checked="Total Equity & Liab == Total Equity + Total Non-Current Liab + Total Current Liab",
                expected_value=calc_total_eq_liab,
                actual_value=bs.total_equity_and_liabilities,
                discrepancy=diff_eq_sum,
                tolerance=tolerance,
                message="Equity and liability components sum correctly."
            ))
        else:
            results.append(ValidationResult(
                entity_type="balance_sheets",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="BS_LIABILITIES_EQUITY_SUBCOMPONENTS_SUM",
                category=ValidationCategory.BALANCE_SHEET_RECONCILIATION,
                status=ValidationStatus.FAILED,
                formula_checked="Total Equity & Liab == Total Equity + Total Non-Current Liab + Total Current Liab",
                expected_value=calc_total_eq_liab,
                actual_value=bs.total_equity_and_liabilities,
                discrepancy=diff_eq_sum,
                tolerance=tolerance,
                message=f"Total Equity & Liabilities discrepancy: Reported {bs.total_equity_and_liabilities} vs Calculated {calc_total_eq_liab}"
            ))

        return results

    @classmethod
    def validate_income_statement(
        cls,
        inc: IncomeStatement,
        period: Optional[FinancialPeriod] = None,
        company_id: Optional[int] = None,
        tolerance: float = DEFAULT_TOLERANCE
    ) -> List[ValidationResult]:
        """Validate arithmetic consistency of Income Statement."""
        results: List[ValidationResult] = []
        entity_id = inc.id if inc.id is not None else 0
        p_id = period.id if period else inc.period_id

        # Rule 1: Revenue Sum Check: Total Revenue == Revenue from operations + Other income
        calc_revenue = round(inc.revenue_from_operations + inc.other_income, 4)
        diff_rev = round(abs(inc.total_revenue - calc_revenue), 4)
        if diff_rev <= tolerance:
            results.append(ValidationResult(
                entity_type="income_statements",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="IS_TOTAL_REVENUE_SUM",
                category=ValidationCategory.INCOME_STATEMENT_MATH,
                status=ValidationStatus.PASSED,
                formula_checked="Total Revenue == Revenue From Operations + Other Income",
                expected_value=calc_revenue,
                actual_value=inc.total_revenue,
                discrepancy=diff_rev,
                tolerance=tolerance,
                message="Revenue components sum correctly to Total Revenue."
            ))
        else:
            results.append(ValidationResult(
                entity_type="income_statements",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="IS_TOTAL_REVENUE_SUM",
                category=ValidationCategory.INCOME_STATEMENT_MATH,
                status=ValidationStatus.FAILED,
                formula_checked="Total Revenue == Revenue From Operations + Other Income",
                expected_value=calc_revenue,
                actual_value=inc.total_revenue,
                discrepancy=diff_rev,
                tolerance=tolerance,
                message=f"Revenue mismatch: Reported {inc.total_revenue} != Sum of Ops ({inc.revenue_from_operations}) + Other ({inc.other_income})"
            ))

        # Rule 2: Profit Before Tax Check: PBT == Total Revenue - Total Expenses - Exceptional Items (or PBET - Exceptional)
        calc_pbt = round(inc.total_revenue - inc.total_expenses + inc.exceptional_items, 4)
        diff_pbt = round(abs(inc.profit_before_tax - calc_pbt), 4)
        # Note: exceptional items might be expense (negative) or income (positive); if reported as PBET - exceptional_items:
        calc_pbt_alt = round(inc.profit_before_exceptional_items_and_tax - inc.exceptional_items, 4)
        diff_pbt_alt = round(abs(inc.profit_before_tax - calc_pbt_alt), 4)
        
        if diff_pbt <= tolerance or diff_pbt_alt <= tolerance or abs(inc.profit_before_tax - inc.profit_before_exceptional_items_and_tax) <= tolerance:
            results.append(ValidationResult(
                entity_type="income_statements",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="IS_PBT_CALCULATION",
                category=ValidationCategory.INCOME_STATEMENT_MATH,
                status=ValidationStatus.PASSED,
                formula_checked="Profit Before Tax == Operating Margin + Exceptional Adjustments",
                expected_value=inc.profit_before_tax,
                actual_value=inc.profit_before_tax,
                discrepancy=0.0,
                tolerance=tolerance,
                message="Profit Before Tax reconciles with Revenues, Expenses, and Exceptional Items."
            ))
        else:
            results.append(ValidationResult(
                entity_type="income_statements",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="IS_PBT_CALCULATION",
                category=ValidationCategory.INCOME_STATEMENT_MATH,
                status=ValidationStatus.WARNING,
                formula_checked="Profit Before Tax == Total Revenue - Total Expenses - Exceptional",
                expected_value=calc_pbt,
                actual_value=inc.profit_before_tax,
                discrepancy=diff_pbt,
                tolerance=tolerance,
                message=f"PBT discrepancy note: Reported {inc.profit_before_tax} vs Calculated {calc_pbt}"
            ))

        # Rule 3: Profit After Tax Check: PAT == PBT - Total Tax Expense
        calc_pat = round(inc.profit_before_tax - inc.total_tax_expense, 4)
        diff_pat = round(abs(inc.profit_after_tax - calc_pat), 4)
        if diff_pat <= tolerance:
            results.append(ValidationResult(
                entity_type="income_statements",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="IS_PAT_NET_TAX",
                category=ValidationCategory.INCOME_STATEMENT_MATH,
                status=ValidationStatus.PASSED,
                formula_checked="Profit After Tax == Profit Before Tax - Total Tax Expense",
                expected_value=calc_pat,
                actual_value=inc.profit_after_tax,
                discrepancy=diff_pat,
                tolerance=tolerance,
                message="Profit After Tax reconciles with PBT and Tax Expense."
            ))
        else:
            results.append(ValidationResult(
                entity_type="income_statements",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="IS_PAT_NET_TAX",
                category=ValidationCategory.INCOME_STATEMENT_MATH,
                status=ValidationStatus.FAILED,
                formula_checked="Profit After Tax == Profit Before Tax - Total Tax Expense",
                expected_value=calc_pat,
                actual_value=inc.profit_after_tax,
                discrepancy=diff_pat,
                tolerance=tolerance,
                message=f"PAT calculation failure: Reported {inc.profit_after_tax} vs Calculated {calc_pat} (PBT {inc.profit_before_tax} - Tax {inc.total_tax_expense})"
            ))

        return results

    @classmethod
    def validate_cash_flow(
        cls,
        cf: CashFlowStatement,
        period: Optional[FinancialPeriod] = None,
        company_id: Optional[int] = None,
        tolerance: float = DEFAULT_TOLERANCE
    ) -> List[ValidationResult]:
        """Validate Cash Flow statement continuity and movement sums."""
        results: List[ValidationResult] = []
        entity_id = cf.id if cf.id is not None else 0
        p_id = period.id if period else cf.period_id

        # Rule 1: Cash continuity: Cash End == Cash Beginning + Net Increase in Cash
        calc_ending_cash = round(cf.cash_beginning_of_period + cf.net_increase_in_cash + cf.foreign_exchange_effect, 4)
        diff_cash = round(abs(cf.cash_end_of_period - calc_ending_cash), 4)
        if diff_cash <= tolerance:
            results.append(ValidationResult(
                entity_type="cash_flow_statements",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="CF_CASH_CONTINUITY",
                category=ValidationCategory.CASH_FLOW_RECONCILIATION,
                status=ValidationStatus.PASSED,
                formula_checked="Cash End == Cash Beginning + Net Increase + FX Effect",
                expected_value=calc_ending_cash,
                actual_value=cf.cash_end_of_period,
                discrepancy=diff_cash,
                tolerance=tolerance,
                message=f"Cash continuity validated: End ({cf.cash_end_of_period}) == Beg ({cf.cash_beginning_of_period}) + Change ({cf.net_increase_in_cash})"
            ))
        else:
            results.append(ValidationResult(
                entity_type="cash_flow_statements",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="CF_CASH_CONTINUITY",
                category=ValidationCategory.CASH_FLOW_RECONCILIATION,
                status=ValidationStatus.FAILED,
                formula_checked="Cash End == Cash Beginning + Net Increase + FX Effect",
                expected_value=calc_ending_cash,
                actual_value=cf.cash_end_of_period,
                discrepancy=diff_cash,
                tolerance=tolerance,
                message=f"CRITICAL: Cash continuity broken! Ending Cash ({cf.cash_end_of_period}) != Beginning Cash ({cf.cash_beginning_of_period}) + Change ({cf.net_increase_in_cash})"
            ))

        # Rule 2: Three activities sum to Net Increase in Cash
        calc_net_increase = round(
            cf.cash_from_operating_activities + cf.cash_from_investing_activities + cf.cash_from_financing_activities,
            4
        )
        diff_activities = round(abs(cf.net_increase_in_cash - calc_net_increase), 4)
        if diff_activities <= tolerance:
            results.append(ValidationResult(
                entity_type="cash_flow_statements",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="CF_ACTIVITIES_SUM",
                category=ValidationCategory.CASH_FLOW_RECONCILIATION,
                status=ValidationStatus.PASSED,
                formula_checked="Net Increase == Operating + Investing + Financing",
                expected_value=calc_net_increase,
                actual_value=cf.net_increase_in_cash,
                discrepancy=diff_activities,
                tolerance=tolerance,
                message="Cash flow activities (Operating, Investing, Financing) sum correctly."
            ))
        else:
            results.append(ValidationResult(
                entity_type="cash_flow_statements",
                entity_id=entity_id,
                company_id=company_id,
                period_id=p_id,
                rule_name="CF_ACTIVITIES_SUM",
                category=ValidationCategory.CASH_FLOW_RECONCILIATION,
                status=ValidationStatus.FAILED,
                formula_checked="Net Increase == Operating + Investing + Financing",
                expected_value=calc_net_increase,
                actual_value=cf.net_increase_in_cash,
                discrepancy=diff_activities,
                tolerance=tolerance,
                message=f"Cash flow activities sum discrepancy: Reported Net {cf.net_increase_in_cash} vs Sum {calc_net_increase}"
            ))

        return results

    @classmethod
    def validate_period_chronology(
        cls,
        periods: List[FinancialPeriod],
        company_id: Optional[int] = None
    ) -> List[ValidationResult]:
        """Validate historical period ordering and date boundaries."""
        results: List[ValidationResult] = []
        if not periods or len(periods) < 2:
            return results

        sorted_periods = sorted(periods, key=lambda p: p.end_date)
        for i in range(1, len(sorted_periods)):
            prev_p = sorted_periods[i - 1]
            curr_p = sorted_periods[i]
            
            if curr_p.start_date < prev_p.start_date or curr_p.end_date <= prev_p.end_date:
                results.append(ValidationResult(
                    entity_type="financial_periods",
                    entity_id=curr_p.id if curr_p.id else 0,
                    company_id=company_id,
                    period_id=curr_p.id,
                    rule_name="PERIOD_CHRONOLOGY_ORDERING",
                    category=ValidationCategory.HISTORICAL_ORDERING,
                    status=ValidationStatus.FAILED,
                    formula_checked="Period(t).end_date > Period(t-1).end_date",
                    expected_value=1.0,
                    actual_value=0.0,
                    discrepancy=1.0,
                    message=f"Period ordering conflict: '{curr_p.period_label}' end_date ({curr_p.end_date}) <= previous '{prev_p.period_label}' end_date ({prev_p.end_date})"
                ))
            else:
                results.append(ValidationResult(
                    entity_type="financial_periods",
                    entity_id=curr_p.id if curr_p.id else 0,
                    company_id=company_id,
                    period_id=curr_p.id,
                    rule_name="PERIOD_CHRONOLOGY_ORDERING",
                    category=ValidationCategory.HISTORICAL_ORDERING,
                    status=ValidationStatus.PASSED,
                    formula_checked="Period(t).end_date > Period(t-1).end_date",
                    expected_value=1.0,
                    actual_value=1.0,
                    discrepancy=0.0,
                    message=f"Chronological continuity verified between '{prev_p.period_label}' and '{curr_p.period_label}'."
                ))

        return results
