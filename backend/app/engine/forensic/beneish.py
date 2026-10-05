"""Beneish M-Score 8-Variable Earnings Manipulation Detection Engine.

The Beneish M-Score is a probabilistic mathematical model created by Messod Beneish 
to detect whether a company has manipulated its earnings.

Standard 8-Variable Formula:
M-Score = -4.84 + 0.920*DSRI + 0.528*GMI + 0.404*AQI + 0.892*SGI + 0.115*DEPI - 0.172*SGAI + 4.037*TATA + 0.0327*LVGI

Benchmark Threshold:
- M-Score > -1.78: Elevated probability of earnings manipulation (High Risk / Screening Flag)
- M-Score <= -1.78: Low probability of earnings manipulation (Normal / Low Risk)
"""

from typing import Optional, Dict, Any
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement
from app.models.forensic import BeneishMScoreResult, BeneishVariable, ForensicRiskLevel


class BeneishMScoreEngine:
    """Calculates deterministic Beneish M-Score across two consecutive financial periods."""

    METHODOLOGY_VERSION = "v1.0.0"
    THRESHOLD = -1.78

    COEFFICIENTS = {
        "INTERCEPT": -4.84,
        "DSRI": 0.920,
        "GMI": 0.528,
        "AQI": 0.404,
        "SGI": 0.892,
        "DEPI": 0.115,
        "SGAI": -0.172,
        "TATA": 4.037,
        "LVGI": 0.0327,
    }

    @classmethod
    def calculate(
        cls,
        inc_curr: Optional[IncomeStatement],
        bal_curr: Optional[BalanceSheet],
        cf_curr: Optional[CashFlowStatement],
        inc_prev: Optional[IncomeStatement],
        bal_prev: Optional[BalanceSheet],
        is_financial_sector: bool = False,
        period_id: int = 0,
        period_label: str = "",
        fiscal_year: int = 0,
    ) -> BeneishMScoreResult:
        """Execute deterministic Beneish M-Score calculation with sector guardrails."""
        # 1. Sector Applicability Guardrail
        if is_financial_sector:
            return BeneishMScoreResult(
                period_id=period_id,
                period_label=period_label,
                fiscal_year=fiscal_year,
                m_score=None,
                risk_classification=ForensicRiskLevel.NOT_APPLICABLE,
                is_applicable=False,
                inapplicable_reason="Beneish M-Score is not applicable to Banking, Insurance, and NBFC financial entities due to distinct balance sheet structures and statutory reserve mechanics.",
                probability_of_manipulation_flag="NOT_APPLICABLE",
                variables={},
                interpretation="Model not applicable for BFSI sector. Use asset quality and NPA provisioning metrics instead.",
                limitations="Standard manufacturing and commercial accrual ratios cannot be meaningfully evaluated on banking balance sheets.",
                methodology_version=cls.METHODOLOGY_VERSION,
            )

        # 2. Historical Data Availability Check
        if not (inc_curr and bal_curr and inc_prev and bal_prev):
            return BeneishMScoreResult(
                period_id=period_id,
                period_label=period_label,
                fiscal_year=fiscal_year,
                m_score=None,
                risk_classification=ForensicRiskLevel.INFO,
                is_applicable=False,
                inapplicable_reason="Beneish M-Score requires two consecutive audited financial periods (current and prior year). Prior year statements missing.",
                probability_of_manipulation_flag="INSUFFICIENT_DATA",
                variables={},
                interpretation="Insufficient historical data to compute multi-period comparative indices.",
                limitations="Requires at least 2 consecutive annual filings to compute ratios.",
                methodology_version=cls.METHODOLOGY_VERSION,
            )

        # Safe helper getters
        def get_rev(inc: IncomeStatement) -> float:
            return float(inc.revenue_from_operations or inc.total_revenue or 0.0)

        def get_cogs(inc: IncomeStatement) -> float:
            return float((inc.cost_of_materials_consumed or 0.0) + (inc.purchases_of_stock_in_trade or 0.0) + (inc.changes_in_inventories or 0.0))

        def get_sga(inc: IncomeStatement) -> float:
            return float((inc.employee_benefit_expenses or 0.0) + (inc.other_expenses or 0.0))

        # Inputs extraction
        rev_t = get_rev(inc_curr)
        rev_prev = get_rev(inc_prev)
        rec_t = float(bal_curr.trade_receivables or 0.0)
        rec_prev = float(bal_prev.trade_receivables or 0.0)
        cogs_t = get_cogs(inc_curr)
        cogs_prev = get_cogs(inc_prev)
        assets_t = float(bal_curr.total_assets or 1.0)
        assets_prev = float(bal_prev.total_assets or 1.0)
        ca_t = float(bal_curr.total_current_assets or 0.0)
        ca_prev = float(bal_prev.total_current_assets or 0.0)
        ppe_t = float(bal_curr.property_plant_equipment or 0.0)
        ppe_prev = float(bal_prev.property_plant_equipment or 0.0)
        inv_t = float(bal_curr.non_current_investments or 0.0)
        inv_prev = float(bal_prev.non_current_investments or 0.0)
        dep_t = float(inc_curr.depreciation_and_amortization or 0.0)
        dep_prev = float(inc_prev.depreciation_and_amortization or 0.0)
        sga_t = get_sga(inc_curr)
        sga_prev = get_sga(inc_prev)
        ltd_t = float(bal_curr.non_current_borrowings or 0.0) + float(bal_curr.current_borrowings or 0.0)
        ltd_prev = float(bal_prev.non_current_borrowings or 0.0) + float(bal_prev.current_borrowings or 0.0)
        net_inc_t = float(inc_curr.profit_after_tax or 0.0)
        cfo_t = float(cf_curr.cash_from_operating_activities or 0.0) if cf_curr else (net_inc_t - dep_t)

        # 1. DSRI (Days Sales in Receivables Index)
        dsr_t = (rec_t / rev_t) if rev_t > 0 else 1.0
        dsr_prev = (rec_prev / rev_prev) if rev_prev > 0 else 1.0
        dsri = round(dsr_t / dsr_prev, 4) if dsr_prev > 0 else 1.0

        # 2. GMI (Gross Margin Index)
        gm_prev = ((rev_prev - cogs_prev) / rev_prev) if rev_prev > 0 else 0.0
        gm_t = ((rev_t - cogs_t) / rev_t) if rev_t > 0 else 0.0
        gmi = round(gm_prev / gm_t, 4) if gm_t > 0 else 1.0

        # 3. AQI (Asset Quality Index)
        nca_t = (assets_t - (ca_t + ppe_t + inv_t)) / assets_t if assets_t > 0 else 0.0
        nca_prev = (assets_prev - (ca_prev + ppe_prev + inv_prev)) / assets_prev if assets_prev > 0 else 0.0
        aq_t = max(0.0, 1.0 - ((ca_t + ppe_t + inv_t) / assets_t)) if assets_t > 0 else 0.0
        aq_prev = max(0.0, 1.0 - ((ca_prev + ppe_prev + inv_prev) / assets_prev)) if assets_prev > 0 else 0.0
        aqi = round((1.0 - ((ca_t + ppe_t) / assets_t)) / max(0.01, (1.0 - ((ca_prev + ppe_prev) / assets_prev))), 4) if assets_t > 0 and assets_prev > 0 else 1.0
        # Bound extreme AQI anomalies safely
        aqi = max(0.1, min(10.0, aqi))

        # 4. SGI (Sales Growth Index)
        sgi = round(rev_t / rev_prev, 4) if rev_prev > 0 else 1.0

        # 5. DEPI (Depreciation Index)
        dep_rate_prev = (dep_prev / (ppe_prev + dep_prev)) if (ppe_prev + dep_prev) > 0 else 0.0
        dep_rate_t = (dep_t / (ppe_t + dep_t)) if (ppe_t + dep_t) > 0 else 0.0
        depi = round(dep_rate_prev / dep_rate_t, 4) if dep_rate_t > 0 else 1.0

        # 6. SGAI (Sales, General and Administrative expenses Index)
        sga_rate_t = (sga_t / rev_t) if rev_t > 0 else 0.0
        sga_rate_prev = (sga_prev / rev_prev) if rev_prev > 0 else 0.0
        sgai = round(sga_rate_t / sga_rate_prev, 4) if sga_rate_prev > 0 else 1.0

        # 7. LVGI (Leverage Index)
        lev_t = (ltd_t / assets_t) if assets_t > 0 else 0.0
        lev_prev = (ltd_prev / assets_prev) if assets_prev > 0 else 0.0
        lvgi = round(lev_t / lev_prev, 4) if lev_prev > 0 else 1.0

        # 8. TATA (Total Accruals to Total Assets)
        tata = round((net_inc_t - cfo_t) / assets_t, 4) if assets_t > 0 else 0.0

        # Variable contributions
        variables: Dict[str, BeneishVariable] = {
            "DSRI": BeneishVariable(
                key="DSRI",
                name="Days Sales in Receivables Index",
                value=dsri,
                coefficient=cls.COEFFICIENTS["DSRI"],
                contribution=round(cls.COEFFICIENTS["DSRI"] * dsri, 4),
                formula="(Receivables_t / Revenue_t) / (Receivables_{t-1} / Revenue_{t-1})",
                interpretation="> 1.0 indicates receivables growing faster than revenue, potential revenue acceleration or collection delays." if dsri > 1.05 else "Normal receivables to revenue trajectory."
            ),
            "GMI": BeneishVariable(
                key="GMI",
                name="Gross Margin Index",
                value=gmi,
                coefficient=cls.COEFFICIENTS["GMI"],
                contribution=round(cls.COEFFICIENTS["GMI"] * gmi, 4),
                formula="Gross_Margin_{t-1} / Gross_Margin_t",
                interpretation="> 1.0 indicates deteriorating gross margins, creating incentives for earnings management." if gmi > 1.05 else "Gross margins stable or expanding."
            ),
            "AQI": BeneishVariable(
                key="AQI",
                name="Asset Quality Index",
                value=aqi,
                coefficient=cls.COEFFICIENTS["AQI"],
                contribution=round(cls.COEFFICIENTS["AQI"] * aqi, 4),
                formula="[1 - (Current Assets_t + PPE_t) / Assets_t] / [1 - (Current Assets_{t-1} + PPE_{t-1}) / Assets_{t-1}]",
                interpretation="> 1.0 indicates increased capitalization of non-current intangible / deferred costs." if aqi > 1.05 else "Asset quality structure stable."
            ),
            "SGI": BeneishVariable(
                key="SGI",
                name="Sales Growth Index",
                value=sgi,
                coefficient=cls.COEFFICIENTS["SGI"],
                contribution=round(cls.COEFFICIENTS["SGI"] * sgi, 4),
                formula="Revenue_t / Revenue_{t-1}",
                interpretation="High sales growth companies face market pressure to sustain revenue momentum." if sgi > 1.20 else "Moderate / normal revenue trajectory."
            ),
            "DEPI": BeneishVariable(
                key="DEPI",
                name="Depreciation Index",
                value=depi,
                coefficient=cls.COEFFICIENTS["DEPI"],
                contribution=round(cls.COEFFICIENTS["DEPI"] * depi, 4),
                formula="Depreciation_Rate_{t-1} / Depreciation_Rate_t",
                interpretation="> 1.0 indicates slowing depreciation rate, potential useful life extension to boost net profit." if depi > 1.05 else "Depreciation rate consistent."
            ),
            "SGAI": BeneishVariable(
                key="SGAI",
                name="SG&A Expenses Index",
                value=sgai,
                coefficient=cls.COEFFICIENTS["SGAI"],
                contribution=round(cls.COEFFICIENTS["SGAI"] * sgai, 4),
                formula="(SGA_t / Revenue_t) / (SGA_{t-1} / Revenue_{t-1})",
                interpretation="> 1.0 indicates operational overhead increasing relative to revenue." if sgai > 1.05 else "Overhead costs controlled relative to revenue."
            ),
            "LVGI": BeneishVariable(
                key="LVGI",
                name="Leverage Index",
                value=lvgi,
                coefficient=cls.COEFFICIENTS["LVGI"],
                contribution=round(cls.COEFFICIENTS["LVGI"] * lvgi, 4),
                formula="(Total_Debt_t / Assets_t) / (Total_Debt_{t-1} / Assets_{t-1})",
                interpretation="> 1.0 indicates increased financial leverage, increasing debt covenant pressure." if lvgi > 1.05 else "Financial leverage stable or deleveraging."
            ),
            "TATA": BeneishVariable(
                key="TATA",
                name="Total Accruals to Total Assets",
                value=tata,
                coefficient=cls.COEFFICIENTS["TATA"],
                contribution=round(cls.COEFFICIENTS["TATA"] * tata, 4),
                formula="(Net_Income_t - Cash_from_Operations_t) / Total_Assets_t",
                interpretation="High positive accruals indicate net income significantly exceeds cash realization (accrual anomaly)." if tata > 0.05 else "Net income well supported by operating cash flow."
            ),
        }

        # Compute M-Score sum
        m_score = (
            cls.COEFFICIENTS["INTERCEPT"]
            + variables["DSRI"].contribution
            + variables["GMI"].contribution
            + variables["AQI"].contribution
            + variables["SGI"].contribution
            + variables["DEPI"].contribution
            + variables["SGAI"].contribution
            + variables["TATA"].contribution
            + variables["LVGI"].contribution
        )
        m_score = round(m_score, 3)

        is_elevated = m_score > cls.THRESHOLD
        risk_class = ForensicRiskLevel.ELEVATED if is_elevated else ForensicRiskLevel.LOW
        flag = "ELEVATED_MANIPULATION_RISK" if is_elevated else "LOW_MANIPULATION_RISK"

        interpretation = (
            f"Beneish M-Score of {m_score:.2f} is above threshold ({cls.THRESHOLD}), indicating statistical characteristics "
            f"consistent with earnings management or aggressive accounting anomalies. This is a screening signal requiring "
            f"audit examination and does NOT constitute proof of financial fraud."
            if is_elevated
            else f"Beneish M-Score of {m_score:.2f} is below threshold ({cls.THRESHOLD}), indicating normal accounting profile."
        )

        limitations = (
            "Empirical statistical model calibrated on historical US/global corporate restatements. "
            "High growth or capital-intensive infrastructure firms may trigger elevated scores due to legitimate capex cycles."
        )

        return BeneishMScoreResult(
            period_id=period_id,
            period_label=period_label,
            fiscal_year=fiscal_year,
            m_score=m_score,
            risk_classification=risk_class,
            is_applicable=True,
            threshold=cls.THRESHOLD,
            probability_of_manipulation_flag=flag,
            variables=variables,
            interpretation=interpretation,
            limitations=limitations,
            methodology_version=cls.METHODOLOGY_VERSION,
        )
