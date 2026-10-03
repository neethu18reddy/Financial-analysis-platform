"""Deterministic DuPont Analysis & ROE Decomposition Engine.

Decomposes Return on Equity (ROE) into operational and financial drivers:
1. 3-Step DuPont:
   ROE = Net Profit Margin * Asset Turnover * Equity Multiplier (Financial Leverage)
   ROE = (PAT / Revenue) * (Revenue / Assets) * (Assets / Equity)

2. 5-Step DuPont:
   ROE = Tax Burden * Interest Burden * Operating Margin * Asset Turnover * Financial Leverage
   ROE = (PAT / EBT) * (EBT / EBIT) * (EBIT / Revenue) * (Revenue / Assets) * (Assets / Equity)
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models.financial_statements import IncomeStatement, BalanceSheet


class DuPont3Step(BaseModel):
    """3-Step DuPont Components."""
    net_profit_margin: float       # PAT / Revenue
    asset_turnover: float          # Revenue / Assets
    financial_leverage: float      # Assets / Equity
    roe_calculated: float          # Product of the 3 components * 100
    roe_reported: float
    is_valid: bool = True
    formula_expression: str = "Net Profit Margin * Asset Turnover * Financial Leverage"


class DuPont5Step(BaseModel):
    """5-Step DuPont Components."""
    tax_burden: float              # PAT / EBT
    interest_burden: float         # EBT / EBIT
    operating_margin: float        # EBIT / Revenue
    asset_turnover: float          # Revenue / Assets
    financial_leverage: float      # Assets / Equity
    roe_calculated: float          # Product of the 5 components * 100
    roe_reported: float
    is_valid: bool = True
    formula_expression: str = "Tax Burden * Interest Burden * Operating Margin * Asset Turnover * Financial Leverage"


class DuPontDecompositionResult(BaseModel):
    """Full DuPont analysis container."""
    methodology_version: str = "v1.0.0"
    dupont_3step: Optional[DuPont3Step] = None
    dupont_5step: Optional[DuPont5Step] = None
    inputs: Dict[str, Any] = Field(default_factory=dict)
    key_driver_analysis: str = ""


class DuPontEngine:
    """Calculates deterministic DuPont decomposition trees."""

    METHODOLOGY_VERSION = "v1.0.0"

    @classmethod
    def calculate(
        cls,
        income: Optional[IncomeStatement],
        balance: Optional[BalanceSheet]
    ) -> Optional[DuPontDecompositionResult]:
        """Compute 3-step and 5-step DuPont decomposition."""
        if not income or not balance:
            return None

        rev = income.total_revenue or income.revenue_from_operations or 0.0
        pat = income.net_profit_attributable_to_owners or income.profit_after_tax or 0.0
        pbt = income.profit_before_tax or 0.0
        ebit = pbt + (income.finance_costs or 0.0)
        tot_assets = balance.total_assets or 0.0
        tot_equity = balance.total_equity or 0.0

        if rev <= 0 or tot_assets <= 0 or tot_equity <= 0:
            return None

        # Reported ROE
        roe_rep = round((pat / tot_equity) * 100.0, 2)

        # 1. 3-Step DuPont
        npm = pat / rev
        at = rev / tot_assets
        lev = tot_assets / tot_equity
        roe_3step_calc = round(npm * at * lev * 100.0, 2)

        d3 = DuPont3Step(
            net_profit_margin=round(npm * 100.0, 2),
            asset_turnover=round(at, 4),
            financial_leverage=round(lev, 4),
            roe_calculated=roe_3step_calc,
            roe_reported=roe_rep,
            is_valid=True
        )

        # 2. 5-Step DuPont (requires EBIT and PBT > 0)
        d5 = None
        if ebit > 0 and pbt > 0:
            tax_burden = pat / pbt
            interest_burden = pbt / ebit
            operating_margin = ebit / rev
            roe_5step_calc = round(tax_burden * interest_burden * operating_margin * at * lev * 100.0, 2)

            d5 = DuPont5Step(
                tax_burden=round(tax_burden, 4),
                interest_burden=round(interest_burden, 4),
                operating_margin=round(operating_margin * 100.0, 2),
                asset_turnover=round(at, 4),
                financial_leverage=round(lev, 4),
                roe_calculated=roe_5step_calc,
                roe_reported=roe_rep,
                is_valid=True
            )

        # Key driver text explanation
        driver_notes = []
        if d5:
            if d5.operating_margin > 20.0:
                driver_notes.append("Strong operating margins driving core profitability.")
            if d5.financial_leverage > 2.5:
                driver_notes.append("High financial leverage magnifying returns (and solvency risk).")
            elif d5.financial_leverage <= 1.5:
                driver_notes.append("Low debt leverage; ROE driven primarily by operational efficiency.")
            if d5.asset_turnover > 1.2:
                driver_notes.append("High asset turnover efficiency.")

        return DuPontDecompositionResult(
            methodology_version=cls.METHODOLOGY_VERSION,
            dupont_3step=d3,
            dupont_5step=d5,
            inputs={
                "revenue": rev,
                "ebit": ebit,
                "pbt": pbt,
                "pat": pat,
                "total_assets": tot_assets,
                "total_equity": tot_equity,
            },
            key_driver_analysis=" ".join(driver_notes) or "Balanced operational and capital structure drivers."
        )
