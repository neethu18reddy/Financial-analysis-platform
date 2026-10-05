"""Altman Z-Score & Emerging Market Z''-Score Financial Distress & Solvency Engine.

The Altman Z-Score is a multi-dimensional linear discriminant model designed to assess 
a firm's probability of bankruptcy / financial distress within 2 years.

Models Implemented:
1. Emerging Market 4-Variable Z''-Score (Recommended for Indian Corporates / Ind AS):
   Z'' = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
   - X1 = Working Capital / Total Assets
   - X2 = Retained Earnings / Total Assets
   - X3 = Operating Profit (EBIT) / Total Assets
   - X4 = Book Value of Equity / Total Liabilities

   Thresholds (Z''-Score):
   - Safe Zone: Z'' > 2.60 (Low Default Risk)
   - Grey Zone: 1.10 <= Z'' <= 2.60 (Moderate Financial Risk / Watchlist)
   - Distress Zone: Z'' < 1.10 (High Probability of Solvency Distress)

2. Original 5-Variable Manufacturing Z-Score:
   Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.999*X5
   - Safe Zone: Z > 2.99
   - Grey Zone: 1.81 <= Z <= 2.99
   - Distress Zone: Z < 1.81
"""

from typing import Optional, Dict, Any
from app.models.financial_statements import IncomeStatement, BalanceSheet
from app.models.forensic import AltmanZScoreResult, ForensicRiskLevel


class AltmanZScoreEngine:
    """Calculates deterministic Altman Z-Score & Emerging Market Z''-Score."""

    METHODOLOGY_VERSION = "v1.0.0"

    @classmethod
    def calculate(
        cls,
        inc: Optional[IncomeStatement],
        bal: Optional[BalanceSheet],
        is_financial_sector: bool = False,
        period_id: int = 0,
        period_label: str = "",
        fiscal_year: int = 0,
        prefer_emerging_market: bool = True,
    ) -> AltmanZScoreResult:
        """Execute deterministic Altman Z-Score evaluation."""
        # 1. Sector Applicability Guardrail
        if is_financial_sector:
            return AltmanZScoreResult(
                period_id=period_id,
                period_label=period_label,
                fiscal_year=fiscal_year,
                model_type="Emerging_Market_Z_Double_Prime",
                z_score=None,
                zone="Not Applicable",
                risk_classification=ForensicRiskLevel.NOT_APPLICABLE,
                safe_threshold=2.60,
                distress_threshold=1.10,
                components={},
                formula_expression="Z'' = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4",
                is_applicable=False,
                inapplicable_reason="Altman Z-Score models are explicitly not applicable to Banking, NBFC, or Financial entities due to regulatory capital requirements and distinct balance sheet leverage mechanics.",
                interpretation="Financial sector entities are evaluated using Capital Adequacy (CRAR), Net NPA, and Liquidity Coverage Ratios rather than industrial distress models.",
                limitations="Asset-to-debt distress multipliers are invalid for deposit-taking financial institutions.",
                methodology_version=cls.METHODOLOGY_VERSION,
            )

        if not (inc and bal):
            return AltmanZScoreResult(
                period_id=period_id,
                period_label=period_label,
                fiscal_year=fiscal_year,
                model_type="Emerging_Market_Z_Double_Prime",
                z_score=None,
                zone="Insufficient Data",
                risk_classification=ForensicRiskLevel.INFO,
                safe_threshold=2.60,
                distress_threshold=1.10,
                components={},
                formula_expression="Z'' = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4",
                is_applicable=False,
                inapplicable_reason="Financial statements missing for selected period.",
                interpretation="Cannot compute distress model without audited income statement and balance sheet.",
                limitations="Requires complete balance sheet and income statement.",
                methodology_version=cls.METHODOLOGY_VERSION,
            )

        # Extraction
        tot_assets = float(bal.total_assets or 1.0)
        tot_liab = float(bal.total_liabilities or (tot_assets - float(bal.total_equity or 0.0)))
        if tot_liab <= 0:
            tot_liab = max(1.0, float(bal.total_current_liabilities or 0.0) + float(bal.total_non_current_liabilities or 0.0))

        ca = float(bal.total_current_assets or 0.0)
        cl = float(bal.total_current_liabilities or 0.0)
        wc = ca - cl

        retained_earnings = float(bal.other_equity_and_reserves or 0.0)
        ebit = float(inc.operating_profit or (float(inc.profit_before_tax or 0.0) + float(inc.finance_costs or 0.0)))
        equity_bv = float(bal.total_equity or (float(bal.equity_share_capital or 0.0) + retained_earnings))
        revenue = float(inc.revenue_from_operations or inc.total_revenue or 0.0)

        # Components
        x1 = wc / tot_assets if tot_assets > 0 else 0.0
        x2 = retained_earnings / tot_assets if tot_assets > 0 else 0.0
        x3 = ebit / tot_assets if tot_assets > 0 else 0.0
        x4 = equity_bv / tot_liab if tot_liab > 0 else 1.0
        x5 = revenue / tot_assets if tot_assets > 0 else 0.0

        if prefer_emerging_market:
            # Emerging Market Z''-Score
            # Z'' = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
            z_score = round(6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4, 3)
            safe_th = 2.60
            distress_th = 1.10
            model_type = "Emerging_Market_Z_Double_Prime"
            formula = "Z'' = 6.56*(WC/Assets) + 3.26*(Reserves/Assets) + 6.72*(EBIT/Assets) + 1.05*(Equity/Liabilities)"
        else:
            # Original 5-Variable Manufacturing Z-Score
            # Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.999*X5
            z_score = round(1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.999 * x5, 3)
            safe_th = 2.99
            distress_th = 1.81
            model_type = "Original_5_Variable_Z_Score"
            formula = "Z = 1.2*(WC/Assets) + 1.4*(Reserves/Assets) + 3.3*(EBIT/Assets) + 0.6*(Equity/Liabilities) + 0.999*(Rev/Assets)"

        # Zone Classification
        if z_score > safe_th:
            zone = "Safe Zone"
            risk_class = ForensicRiskLevel.LOW
            interpretation = (
                f"{model_type} of {z_score:.2f} places the firm comfortably in the Safe Zone (threshold > {safe_th:.2f}). "
                f"Low probability of short-to-medium term solvency or liquidity distress."
            )
        elif z_score >= distress_th:
            zone = "Grey Zone"
            risk_class = ForensicRiskLevel.MODERATE
            interpretation = (
                f"{model_type} of {z_score:.2f} falls into the Grey / Watchlist Zone ({distress_th:.2f} to {safe_th:.2f}). "
                f"Reflects moderate financial leverage or tighter working capital buffers warranting active balance sheet monitoring."
            )
        else:
            zone = "Distress Zone"
            risk_class = ForensicRiskLevel.HIGH
            interpretation = (
                f"{model_type} of {z_score:.2f} falls into the Distress Zone (< {distress_th:.2f}). "
                f"Statistical indicator highlighting working capital compression, high liability burden, or insufficient operating earnings coverage."
            )

        components = {
            "X1_Working_Capital_to_Assets": round(x1, 4),
            "X2_Retained_Earnings_to_Assets": round(x2, 4),
            "X3_EBIT_to_Assets": round(x3, 4),
            "X4_Equity_to_Liabilities": round(x4, 4),
            "X5_Asset_Turnover": round(x5, 4),
        }

        limitations = (
            "Empirical insolvency scoring model. Does not factor in parent company guarantees, "
            "unencumbered asset liquidations, or sovereign backstops."
        )

        return AltmanZScoreResult(
            period_id=period_id,
            period_label=period_label,
            fiscal_year=fiscal_year,
            model_type=model_type,
            z_score=z_score,
            zone=zone,
            risk_classification=risk_class,
            safe_threshold=safe_th,
            distress_threshold=distress_th,
            components=components,
            formula_expression=formula,
            is_applicable=True,
            interpretation=interpretation,
            limitations=limitations,
            methodology_version=cls.METHODOLOGY_VERSION,
        )
