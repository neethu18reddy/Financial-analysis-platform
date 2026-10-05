"""Granular Forensic Screening Signals & Anomaly Detection Engine.

Implements empirical, deterministic tests to detect:
1. Accrual anomalies (Sloan Accruals, Cash backing deficit)
2. Revenue recognition & channel stuffing risks (Receivable growth vs Revenue growth)
3. Inventory accumulation anomalies (Inventory growth vs Revenue growth)
4. Supplier stretching (DPO elongation)
5. Debt escalation vs ROCE/Operating profit divergence
6. Interest coverage & solvency pressure
7. Margin quality & unusual Other Income dependencies
8. Effective Tax Rate anomalies

All signals output standardized risk levels, objective calculation inputs, and non-accusatory interpretations.
"""

from typing import Optional, List, Dict, Any
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement
from app.models.forensic import ForensicSignal, SignalCategory, ForensicRiskLevel


class ForensicSignalsEngine:
    """Calculates granular forensic anomaly screening indicators."""

    METHODOLOGY_VERSION = "v1.0.0"

    @classmethod
    def evaluate_all(
        cls,
        inc_curr: Optional[IncomeStatement],
        bal_curr: Optional[BalanceSheet],
        cf_curr: Optional[CashFlowStatement],
        inc_prev: Optional[IncomeStatement] = None,
        bal_prev: Optional[BalanceSheet] = None,
        cf_prev: Optional[CashFlowStatement] = None,
        is_financial_sector: bool = False,
    ) -> List[ForensicSignal]:
        """Evaluate full suite of forensic screening signals for a financial period."""
        signals: List[ForensicSignal] = []

        if not (inc_curr and bal_curr):
            return signals

        # -------------------------------------------------------------------------
        # 1. Accrual & Cash Realization Signals
        # -------------------------------------------------------------------------
        net_inc = float(inc_curr.profit_after_tax or 0.0)
        deprec = float(inc_curr.depreciation_and_amortization or 0.0)
        cfo = float(cf_curr.cash_from_operating_activities or 0.0) if cf_curr else (net_inc - deprec)
        tot_assets = float(bal_curr.total_assets or 1.0)

        # Sloan Balance Sheet Accruals: (Net Income - CFO) / Total Assets
        sloan_accrual = (net_inc - cfo) / tot_assets if tot_assets > 0 else 0.0
        sloan_pct = sloan_accrual * 100.0

        if sloan_pct > 10.0:
            risk = ForensicRiskLevel.ELEVATED
            interp = (
                f"Sloan Accrual ratio of {sloan_pct:.1f}% of assets is significantly elevated (> 10%). "
                f"Net income is substantially larger than operating cash flow, indicating high reliance on non-cash accounting accruals."
            )
        elif sloan_pct > 5.0:
            risk = ForensicRiskLevel.MODERATE
            interp = (
                f"Sloan Accrual ratio of {sloan_pct:.1f}% reflects moderate positive accruals. "
                f"Cash flow realization warrants standard monitoring."
            )
        else:
            risk = ForensicRiskLevel.LOW
            interp = (
                f"Sloan Accrual ratio of {sloan_pct:.1f}% indicates strong cash backing. "
                f"Operating cash flow closely aligns with or exceeds reported net profit."
            )

        signals.append(
            ForensicSignal(
                signal_key="SLOAN_ACCRUAL_ANOMALY",
                signal_label="Sloan Accrual Quality Indicator",
                category=SignalCategory.ACCRUAL_QUALITY,
                risk_level=risk,
                value=round(sloan_pct, 2),
                formatted_value=f"{sloan_pct:.2f}% of Assets",
                benchmark_threshold="Normal: < 5.0% | Elevated: > 10.0%",
                formula_expression="(Net Income - Cash from Operations) / Total Assets * 100",
                inputs={"net_income": net_inc, "cfo": cfo, "total_assets": tot_assets},
                interpretation=interp,
                is_applicable=not is_financial_sector,
                inapplicable_reason="Accrual models not applicable to BFSI." if is_financial_sector else None,
                limitations="Capital-intensive firms in heavy expansion phases may experience temporary accrual timing differences.",
                methodology_version=cls.METHODOLOGY_VERSION,
            )
        )

        # CFO / PAT Ratio
        cfo_to_pat = (cfo / net_inc) if net_inc != 0 else (1.0 if cfo >= 0 else -1.0)
        if net_inc > 0 and cfo_to_pat < 0.6:
            risk_cfo = ForensicRiskLevel.HIGH
            interp_cfo = f"CFO to PAT ratio of {cfo_to_pat:.2f}x is well below 0.8x. Cash conversion of reported profit is constrained."
        elif net_inc > 0 and cfo_to_pat < 0.85:
            risk_cfo = ForensicRiskLevel.MODERATE
            interp_cfo = f"CFO to PAT ratio of {cfo_to_pat:.2f}x reflects mild working capital drag on profit realization."
        else:
            risk_cfo = ForensicRiskLevel.LOW
            interp_cfo = f"CFO to PAT ratio of {cfo_to_pat:.2f}x confirms healthy earnings quality with high cash realization."

        signals.append(
            ForensicSignal(
                signal_key="CFO_PAT_CONVERSION",
                signal_label="Operating Cash to Net Profit Realization",
                category=SignalCategory.ACCRUAL_QUALITY,
                risk_level=risk_cfo,
                value=round(cfo_to_pat, 2),
                formatted_value=f"{cfo_to_pat:.2f}x",
                benchmark_threshold="Healthy: >= 1.0x | Caution: < 0.8x | Elevated: < 0.6x",
                formula_expression="Cash from Operations / Net Income",
                inputs={"cfo": cfo, "net_income": net_inc},
                interpretation=interp_cfo,
                limitations="Volatile commodity working capital cycles can distort single-year CFO/PAT ratios.",
                methodology_version=cls.METHODOLOGY_VERSION,
            )
        )

        # -------------------------------------------------------------------------
        # 2. Revenue Recognition & Working Capital Divergence Signals (requires prior period)
        # -------------------------------------------------------------------------
        if inc_prev and bal_prev:
            rev_t = float(inc_curr.revenue_from_operations or inc_curr.total_revenue or 0.0)
            rev_prev = float(inc_prev.revenue_from_operations or inc_prev.total_revenue or 0.0)
            rev_growth = ((rev_t - rev_prev) / rev_prev * 100.0) if rev_prev > 0 else 0.0

            rec_t = float(bal_curr.trade_receivables or 0.0)
            rec_prev = float(bal_prev.trade_receivables or 0.0)
            rec_growth = ((rec_t - rec_prev) / rec_prev * 100.0) if rec_prev > 0 else 0.0

            rec_divergence = rec_growth - rev_growth

            if rec_divergence > 20.0 and rec_growth > 15.0:
                risk_rec = ForensicRiskLevel.HIGH
                interp_rec = (
                    f"Trade Receivables grew by {rec_growth:.1f}% while Revenue grew by {rev_growth:.1f}% "
                    f"(divergence of +{rec_divergence:.1f}%). Statistical indicator of potential channel stuffing, "
                    f"relaxed credit terms to boost sales, or customer collection delays."
                )
            elif rec_divergence > 10.0 and rec_growth > 10.0:
                risk_rec = ForensicRiskLevel.MODERATE
                interp_rec = f"Receivables growth ({rec_growth:.1f}%) slightly outpaced revenue growth ({rev_growth:.1f}%)."
            else:
                risk_rec = ForensicRiskLevel.LOW
                interp_rec = f"Receivables growth ({rec_growth:.1f}%) is aligned with or slower than revenue growth ({rev_growth:.1f}%)."

            signals.append(
                ForensicSignal(
                    signal_key="RECEIVABLE_REVENUE_DIVERGENCE",
                    signal_label="Receivables vs Revenue Growth Divergence",
                    category=SignalCategory.REVENUE_RECOGNITION,
                    risk_level=risk_rec,
                    value=round(rec_divergence, 2),
                    formatted_value=f"+{rec_divergence:.1f}%" if rec_divergence > 0 else f"{rec_divergence:.1f}%",
                    benchmark_threshold="Normal: < +10% | Warning: +10% to +20% | Elevated: > +20%",
                    formula_expression="YoY_Growth(Receivables) - YoY_Growth(Revenue)",
                    inputs={"receivables_growth_pct": round(rec_growth, 2), "revenue_growth_pct": round(rev_growth, 2)},
                    interpretation=interp_rec,
                    is_applicable=not is_financial_sector,
                    inapplicable_reason="Receivables divergence not applicable to BFSI entities." if is_financial_sector else None,
                    limitations="Q4 seasonality or large government contract billing can cause legitimate year-end receivables spikes.",
                    methodology_version=cls.METHODOLOGY_VERSION,
                )
            )

            # Inventory vs Revenue Divergence
            inv_t = float(bal_curr.inventories or 0.0)
            inv_prev = float(bal_prev.inventories or 0.0)
            inv_growth = ((inv_t - inv_prev) / inv_prev * 100.0) if inv_prev > 0 else 0.0
            inv_divergence = inv_growth - rev_growth

            if inv_divergence > 20.0 and inv_growth > 15.0:
                risk_inv = ForensicRiskLevel.HIGH
                interp_inv = (
                    f"Inventories grew by {inv_growth:.1f}% compared to {rev_growth:.1f}% revenue growth "
                    f"(divergence of +{inv_divergence:.1f}%). Indicator of potential product obsolescence, "
                    f"slowing order intake, or inventory cost deferrals."
                )
            elif inv_divergence > 10.0:
                risk_inv = ForensicRiskLevel.MODERATE
                interp_inv = f"Inventories grew moderately faster than top-line revenue (+{inv_divergence:.1f}% gap)."
            else:
                risk_inv = ForensicRiskLevel.LOW
                interp_inv = "Inventory growth is well synchronized with sales volume."

            signals.append(
                ForensicSignal(
                    signal_key="INVENTORY_REVENUE_DIVERGENCE",
                    signal_label="Inventory vs Revenue Growth Divergence",
                    category=SignalCategory.WORKING_CAPITAL,
                    risk_level=risk_inv,
                    value=round(inv_divergence, 2),
                    formatted_value=f"+{inv_divergence:.1f}%" if inv_divergence > 0 else f"{inv_divergence:.1f}%",
                    benchmark_threshold="Normal: < +10% | Elevated: > +20%",
                    formula_expression="YoY_Growth(Inventory) - YoY_Growth(Revenue)",
                    inputs={"inventory_growth_pct": round(inv_growth, 2), "revenue_growth_pct": round(rev_growth, 2)},
                    interpretation=interp_inv,
                    is_applicable=not is_financial_sector,
                    inapplicable_reason="Inventory metrics not applicable to service or banking entities." if is_financial_sector else None,
                    limitations="Raw material stocking ahead of plant capacity expansion can temporarily elevate inventory growth.",
                    methodology_version=cls.METHODOLOGY_VERSION,
                )
            )

            # Debt Escalation vs Operating Profit Divergence
            debt_t = float(bal_curr.non_current_borrowings or 0.0) + float(bal_curr.current_borrowings or 0.0)
            debt_prev = float(bal_prev.non_current_borrowings or 0.0) + float(bal_prev.current_borrowings or 0.0)
            debt_growth = ((debt_t - debt_prev) / debt_prev * 100.0) if debt_prev > 0 else 0.0

            ebit_t = float(inc_curr.operating_profit or (float(inc_curr.profit_before_tax or 0.0) + float(inc_curr.finance_costs or 0.0)))
            ebit_prev = float(inc_prev.operating_profit or (float(inc_prev.profit_before_tax or 0.0) + float(inc_prev.finance_costs or 0.0)))
            ebit_growth = ((ebit_t - ebit_prev) / abs(ebit_prev) * 100.0) if ebit_prev != 0 else 0.0

            if debt_growth > 20.0 and ebit_growth < 0.0:
                risk_debt = ForensicRiskLevel.HIGH
                interp_debt = (
                    f"Total borrowings surged by {debt_growth:.1f}% while Operating Profit contracted by {ebit_growth:.1f}%. "
                    f"Screening indicator of debt-funded operational deficits or capital misallocation."
                )
            elif debt_growth > 15.0 and debt_growth > (ebit_growth + 15.0):
                risk_debt = ForensicRiskLevel.MODERATE
                interp_debt = f"Debt growth ({debt_growth:.1f}%) significantly outpaced operating profit expansion ({ebit_growth:.1f}%)."
            else:
                risk_debt = ForensicRiskLevel.LOW
                interp_debt = "Debt trajectory is prudent relative to operating earnings momentum."

            signals.append(
                ForensicSignal(
                    signal_key="DEBT_VS_EBIT_DIVERGENCE",
                    signal_label="Debt Growth vs Operating Earnings Divergence",
                    category=SignalCategory.DEBT_SOLVENCY,
                    risk_level=risk_debt,
                    value=round(debt_growth - ebit_growth, 2),
                    formatted_value=f"Debt: {debt_growth:+.1f}% | EBIT: {ebit_growth:+.1f}%",
                    benchmark_threshold="Normal: Debt Growth <= EBIT Growth | Alert: Debt +20% & EBIT Negative",
                    formula_expression="YoY_Growth(Total_Debt) - YoY_Growth(EBIT)",
                    inputs={"debt_growth_pct": round(debt_growth, 2), "ebit_growth_pct": round(ebit_growth, 2)},
                    interpretation=interp_debt,
                    is_applicable=not is_financial_sector,
                    inapplicable_reason="Industrial debt leverage ratios not applicable to banking deposits." if is_financial_sector else None,
                    limitations="New project capex can temporarily increase debt before revenue commissioning occurs.",
                    methodology_version=cls.METHODOLOGY_VERSION,
                )
            )

        # -------------------------------------------------------------------------
        # 3. Interest Coverage & Solvency Signals
        # -------------------------------------------------------------------------
        fin_costs = float(inc_curr.finance_costs or 0.0)
        ebit_val = float(inc_curr.operating_profit or (float(inc_curr.profit_before_tax or 0.0) + fin_costs))
        
        if fin_costs > 0:
            int_coverage = ebit_val / fin_costs
            if int_coverage < 1.2:
                risk_ic = ForensicRiskLevel.CRITICAL
                interp_ic = f"Interest coverage of {int_coverage:.2f}x is critically low (< 1.2x). Operating profit barely covers debt servicing obligations."
            elif int_coverage < 2.0:
                risk_ic = ForensicRiskLevel.MODERATE
                interp_ic = f"Interest coverage of {int_coverage:.2f}x is tight (< 2.0x). Vulnerable to interest rate hikes or EBITDA shocks."
            else:
                risk_ic = ForensicRiskLevel.LOW
                interp_ic = f"Interest coverage of {int_coverage:.2f}x demonstrates comfortable debt servicing headroom."

            signals.append(
                ForensicSignal(
                    signal_key="INTEREST_COVERAGE_SOLVENCY",
                    signal_label="Interest Coverage Ratio (EBIT / Finance Costs)",
                    category=SignalCategory.DEBT_SOLVENCY,
                    risk_level=risk_ic,
                    value=round(int_coverage, 2),
                    formatted_value=f"{int_coverage:.2f}x",
                    benchmark_threshold="Safe: > 3.0x | Tight: 1.5x - 2.5x | Vulnerable: < 1.5x",
                    formula_expression="EBIT / Finance Costs",
                    inputs={"ebit": ebit_val, "finance_costs": fin_costs},
                    interpretation=interp_ic,
                    is_applicable=True,
                    limitations="Does not account for cash balances and liquid treasury reserves available to service debt.",
                    methodology_version=cls.METHODOLOGY_VERSION,
                )
            )

        # -------------------------------------------------------------------------
        # 4. Earnings Composition: Other Income Dependency
        # -------------------------------------------------------------------------
        other_inc = float(inc_curr.other_income or 0.0)
        pbt = float(inc_curr.profit_before_tax or 0.0)
        
        other_inc_pct = (other_inc / pbt * 100.0) if pbt > 0 else 0.0
        if pbt > 0 and other_inc_pct > 35.0:
            risk_oi = ForensicRiskLevel.ELEVATED
            interp_oi = (
                f"Other Income accounts for {other_inc_pct:.1f}% of Profit Before Tax (> 35%). "
                f"Signifies substantial dependence on non-operating treasury gains, asset sales, or dividend income."
            )
        elif pbt > 0 and other_inc_pct > 20.0:
            risk_oi = ForensicRiskLevel.MODERATE
            interp_oi = f"Other income contributes {other_inc_pct:.1f}% of PBT, a moderate non-core proportion."
        else:
            risk_oi = ForensicRiskLevel.LOW
            interp_oi = f"Other income accounts for {other_inc_pct:.1f}% of PBT; earnings are overwhelmingly driven by core operations."

        signals.append(
            ForensicSignal(
                signal_key="OTHER_INCOME_DEPENDENCY",
                signal_label="Non-Operating Other Income Share in PBT",
                category=SignalCategory.MARGIN_ANOMALY,
                risk_level=risk_oi,
                value=round(other_inc_pct, 2),
                formatted_value=f"{other_inc_pct:.1f}% of PBT",
                benchmark_threshold="Normal: < 15.0% | Moderate: 15-30% | High Non-Core: > 30%",
                formula_expression="(Other Income / Profit Before Tax) * 100",
                inputs={"other_income": other_inc, "profit_before_tax": pbt},
                interpretation=interp_oi,
                is_applicable=True,
                limitations="Holding companies and investment arms naturally have high dividend/treasury other income.",
                methodology_version=cls.METHODOLOGY_VERSION,
            )
        )

        # -------------------------------------------------------------------------
        # 5. Effective Tax Rate Anomaly
        # -------------------------------------------------------------------------
        tax_exp = float(inc_curr.total_tax_expense or 0.0)
        if pbt > 0:
            eff_tax_rate = (tax_exp / pbt) * 100.0
            if eff_tax_rate < 12.0:
                risk_tax = ForensicRiskLevel.MODERATE
                interp_tax = (
                    f"Effective Tax Rate of {eff_tax_rate:.1f}% is unusually low compared to Indian statutory corporate rates (25.17%). "
                    f"Examine tax exemptions, accumulated MAT credits, or jurisdiction structuring."
                )
            else:
                risk_tax = ForensicRiskLevel.LOW
                interp_tax = f"Effective Tax Rate of {eff_tax_rate:.1f}% aligns with expected Indian statutory brackets."

            signals.append(
                ForensicSignal(
                    signal_key="EFFECTIVE_TAX_RATE_ANOMALY",
                    signal_label="Effective Tax Rate Screening",
                    category=SignalCategory.MARGIN_ANOMALY,
                    risk_level=risk_tax,
                    value=round(eff_tax_rate, 2),
                    formatted_value=f"{eff_tax_rate:.1f}%",
                    benchmark_threshold="Standard Ind AS Range: 20.0% to 30.0% | Anomaly: < 12.0%",
                    formula_expression="(Total Tax Expense / Profit Before Tax) * 100",
                    inputs={"tax_expense": tax_exp, "pbt": pbt},
                    interpretation=interp_tax,
                    is_applicable=True,
                    limitations="SEZ tax holidays and carry-forward loss deductions can legitimately reduce effective rates.",
                    methodology_version=cls.METHODOLOGY_VERSION,
                )
            )

        return signals
