"""Piotroski 9-Point F-Score Fundamental Health & Screening Engine.

The Piotroski F-Score is a discrete score between 0-9 reflecting nine criteria used to 
determine the strength of a firm's financial position across profitability, leverage, and operating efficiency.

Score Classification:
- 8 to 9: Strong Financial Position (Low Risk)
- 5 to 7: Moderate / Stable Financial Position
- 0 to 4: Weak Financial Position / Elevated Distress Risk
"""

from typing import Optional, List, Dict, Any
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement
from app.models.forensic import PiotroskiFScoreResult, PiotroskiSignal, ForensicRiskLevel


class PiotroskiFScoreEngine:
    """Calculates deterministic Piotroski 9-Point F-Score."""

    METHODOLOGY_VERSION = "v1.0.0"

    @classmethod
    def calculate(
        cls,
        inc_curr: Optional[IncomeStatement],
        bal_curr: Optional[BalanceSheet],
        cf_curr: Optional[CashFlowStatement],
        inc_prev: Optional[IncomeStatement],
        bal_prev: Optional[BalanceSheet],
        period_id: int = 0,
        period_label: str = "",
        fiscal_year: int = 0,
    ) -> PiotroskiFScoreResult:
        """Execute deterministic Piotroski F-Score evaluation."""
        if not (inc_curr and bal_curr and inc_prev and bal_prev):
            return PiotroskiFScoreResult(
                period_id=period_id,
                period_label=period_label,
                fiscal_year=fiscal_year,
                f_score=0,
                max_score=9,
                risk_classification=ForensicRiskLevel.INFO,
                financial_health_label="INSUFFICIENT_DATA",
                profitability_score=0,
                leverage_liquidity_score=0,
                operating_efficiency_score=0,
                signals=[],
                is_applicable=False,
                inapplicable_reason="Piotroski F-Score requires 2 consecutive periods of financial statements to evaluate year-over-year momentum.",
                interpretation="Insufficient historical data to evaluate 9-point fundamental test.",
                limitations="Requires audited comparative annual periods.",
                methodology_version=cls.METHODOLOGY_VERSION,
            )

        # Helper values
        net_inc_t = float(inc_curr.profit_after_tax or 0.0)
        net_inc_prev = float(inc_prev.profit_after_tax or 0.0)
        assets_t = float(bal_curr.total_assets or 1.0)
        assets_prev = float(bal_prev.total_assets or 1.0)
        cfo_t = float(cf_curr.cash_from_operating_activities or 0.0) if cf_curr else (net_inc_t - float(inc_curr.depreciation_and_amortization or 0.0))
        
        rev_t = float(inc_curr.revenue_from_operations or inc_curr.total_revenue or 0.0)
        rev_prev = float(inc_prev.revenue_from_operations or inc_prev.total_revenue or 0.0)
        cogs_t = float((inc_curr.cost_of_materials_consumed or 0.0) + (inc_curr.purchases_of_stock_in_trade or 0.0) + (inc_curr.changes_in_inventories or 0.0))
        cogs_prev = float((inc_prev.cost_of_materials_consumed or 0.0) + (inc_prev.purchases_of_stock_in_trade or 0.0) + (inc_prev.changes_in_inventories or 0.0))
        
        gm_t = ((rev_t - cogs_t) / rev_t) if rev_t > 0 else 0.0
        gm_prev = ((rev_prev - cogs_prev) / rev_prev) if rev_prev > 0 else 0.0
        
        turnover_t = (rev_t / assets_t) if assets_t > 0 else 0.0
        turnover_prev = (rev_prev / assets_prev) if assets_prev > 0 else 0.0

        ltd_t = float(bal_curr.non_current_borrowings or 0.0)
        ltd_prev = float(bal_prev.non_current_borrowings or 0.0)
        lev_t = (ltd_t / assets_t) if assets_t > 0 else 0.0
        lev_prev = (ltd_prev / assets_prev) if assets_prev > 0 else 0.0

        ca_t = float(bal_curr.total_current_assets or 0.0)
        cl_t = float(bal_curr.total_current_liabilities or 1.0)
        cr_t = (ca_t / cl_t) if cl_t > 0 else 0.0

        ca_prev = float(bal_prev.total_current_assets or 0.0)
        cl_prev = float(bal_prev.total_current_liabilities or 1.0)
        cr_prev = (ca_prev / cl_prev) if cl_prev > 0 else 0.0

        equity_t = float(bal_curr.equity_share_capital or 0.0)
        equity_prev = float(bal_prev.equity_share_capital or 0.0)

        roa_t = (net_inc_t / assets_t) if assets_t > 0 else 0.0
        roa_prev = (net_inc_prev / assets_prev) if assets_prev > 0 else 0.0

        # -------------------------------------------------------------
        # 1. Profitability Signals (4 Points)
        # -------------------------------------------------------------
        p1 = net_inc_t > 0
        p2 = cfo_t > 0
        p3 = roa_t > roa_prev
        p4 = cfo_t > net_inc_t  # Accrual quality: cash flow exceeds accounting profit

        # -------------------------------------------------------------
        # 2. Leverage, Liquidity & Solvency (3 Points)
        # -------------------------------------------------------------
        l1 = lev_t <= lev_prev  # Lower long-term debt ratio
        l2 = cr_t > cr_prev     # Higher current ratio
        l3 = equity_t <= (equity_prev * 1.005)  # No equity dilution (allowing tiny rounding tolerance)

        # -------------------------------------------------------------
        # 3. Operating Efficiency (2 Points)
        # -------------------------------------------------------------
        e1 = gm_t > gm_prev           # Gross margin expansion
        e2 = turnover_t > turnover_prev # Asset turnover improvement

        signals: List[PiotroskiSignal] = [
            # Profitability
            PiotroskiSignal(
                key="POSITIVE_ROA",
                category="Profitability",
                name="Positive Return on Assets (ROA > 0)",
                passed=p1,
                score=1 if p1 else 0,
                description="Firm generated positive net profit in the current period.",
                formula="Net Income_t > 0",
                inputs={"net_income": net_inc_t, "total_assets": assets_t, "roa": round(roa_t, 4)},
            ),
            PiotroskiSignal(
                key="POSITIVE_CFO",
                category="Profitability",
                name="Positive Cash Flow from Operations (CFO > 0)",
                passed=p2,
                score=1 if p2 else 0,
                description="Firm generated positive operating cash flow from core operations.",
                formula="Cash Flow from Operations_t > 0",
                inputs={"cfo": cfo_t},
            ),
            PiotroskiSignal(
                key="ROA_EXPANSION",
                category="Profitability",
                name="ROA Expansion (ROA_t > ROA_{t-1})",
                passed=p3,
                score=1 if p3 else 0,
                description="Return on assets improved compared to prior fiscal year.",
                formula="ROA_t > ROA_{t-1}",
                inputs={"roa_current": round(roa_t, 4), "roa_prev": round(roa_prev, 4)},
            ),
            PiotroskiSignal(
                key="CFO_EXCEEDS_NET_INCOME",
                category="Profitability",
                name="Cash Quality (CFO > Net Income)",
                passed=p4,
                score=1 if p4 else 0,
                description="Operating cash flow exceeds accounting net profit, indicating genuine cash backing with low accruals.",
                formula="CFO_t > Net Income_t",
                inputs={"cfo": cfo_t, "net_income": net_inc_t},
            ),
            # Leverage & Liquidity
            PiotroskiSignal(
                key="DECREASING_LEVERAGE",
                category="Leverage & Liquidity",
                name="Deleveraging (Long-Term Debt Ratio <= Prior Year)",
                passed=l1,
                score=1 if l1 else 0,
                description="Long term debt to total assets did not increase, preserving solvency margin.",
                formula="(Long-Term Debt / Assets)_t <= (Long-Term Debt / Assets)_{t-1}",
                inputs={"leverage_current": round(lev_t, 4), "leverage_prev": round(lev_prev, 4)},
            ),
            PiotroskiSignal(
                key="IMPROVING_CURRENT_RATIO",
                category="Leverage & Liquidity",
                name="Current Ratio Improvement (CR_t > CR_{t-1})",
                passed=l2,
                score=1 if l2 else 0,
                description="Short term liquidity coverage improved relative to prior period.",
                formula="Current Ratio_t > Current Ratio_{t-1}",
                inputs={"cr_current": round(cr_t, 2), "cr_prev": round(cr_prev, 2)},
            ),
            PiotroskiSignal(
                key="NO_EQUITY_DILUTION",
                category="Leverage & Liquidity",
                name="No Equity Dilution (Share Capital <= Prior Year)",
                passed=l3,
                score=1 if l3 else 0,
                description="Firm did not issue new equity shares to fund operations or bridge cash deficits.",
                formula="Equity Share Capital_t <= Equity Share Capital_{t-1}",
                inputs={"share_capital_current": equity_t, "share_capital_prev": equity_prev},
            ),
            # Operating Efficiency
            PiotroskiSignal(
                key="GROSS_MARGIN_EXPANSION",
                category="Operating Efficiency",
                name="Gross Margin Expansion (GM_t > GM_{t-1})",
                passed=e1,
                score=1 if e1 else 0,
                description="Gross profit margin improved, demonstrating pricing power or cost discipline.",
                formula="Gross Margin_t > Gross Margin_{t-1}",
                inputs={"gross_margin_current": round(gm_t * 100, 2), "gross_margin_prev": round(gm_prev * 100, 2)},
            ),
            PiotroskiSignal(
                key="ASSET_TURNOVER_IMPROVEMENT",
                category="Operating Efficiency",
                name="Asset Turnover Improvement (Turnover_t > Turnover_{t-1})",
                passed=e2,
                score=1 if e2 else 0,
                description="Total asset productivity improved, generating higher revenue per rupee of asset base.",
                formula="Asset Turnover_t > Asset Turnover_{t-1}",
                inputs={"turnover_current": round(turnover_t, 2), "turnover_prev": round(turnover_prev, 2)},
            ),
        ]

        prof_score = sum(1 for s in signals[:4] if s.passed)
        lev_score = sum(1 for s in signals[4:7] if s.passed)
        eff_score = sum(1 for s in signals[7:] if s.passed)
        f_score = prof_score + lev_score + eff_score

        if f_score >= 8:
            risk_class = ForensicRiskLevel.LOW
            health_label = "Strong Financial Health"
            interpretation = (
                f"Piotroski F-Score of {f_score}/9 indicates high fundamental momentum and robust operational health across "
                f"profitability, balance sheet deleveraging, and operational asset productivity."
            )
        elif f_score >= 5:
            risk_class = ForensicRiskLevel.MODERATE
            health_label = "Moderate / Stable Financial Health"
            interpretation = (
                f"Piotroski F-Score of {f_score}/9 reflects stable fundamentals with selected operational or liquidity headwinds "
                f"warranting monitoring."
            )
        else:
            risk_class = ForensicRiskLevel.HIGH
            health_label = "Weak Financial Health (Elevated Screening Risk)"
            interpretation = (
                f"Piotroski F-Score of {f_score}/9 indicates fundamental weakness, deteriorating cash generation, or balance sheet stress. "
                f"This screening signal suggests heightened scrutiny is needed."
            )

        limitations = (
            "Binary scoring methodology does not weight the magnitude of changes (e.g. 0.1% vs 20% margin change count equally). "
            "Best used in combination with continuous fundamental ratio and forensic accrual models."
        )

        return PiotroskiFScoreResult(
            period_id=period_id,
            period_label=period_label,
            fiscal_year=fiscal_year,
            f_score=f_score,
            max_score=9,
            risk_classification=risk_class,
            financial_health_label=health_label,
            profitability_score=prof_score,
            leverage_liquidity_score=lev_score,
            operating_efficiency_score=eff_score,
            signals=signals,
            is_applicable=True,
            interpretation=interpretation,
            limitations=limitations,
            methodology_version=cls.METHODOLOGY_VERSION,
        )
