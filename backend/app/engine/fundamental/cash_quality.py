"""Deterministic Cash Quality & Earnings Integrity Engine.

Calculates:
- CFO to PAT Ratio (Operating Cash Conversion)
- Free Cash Flow to PAT Ratio
- Sloan Accruals Ratio = (PAT - CFO) / Total Assets
- FCF Yield / FCF Margin
- Cash Flow to Debt Coverage
"""

from typing import Dict, Any, Optional
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement
from app.engine.fundamental.profitability import CalculatedMetric


class CashQualityEngine:
    """Calculates cash conversion and accruals quality indicators."""

    METHODOLOGY_VERSION = "v1.0.0"

    @classmethod
    def calculate_all(
        cls,
        income: Optional[IncomeStatement],
        balance: Optional[BalanceSheet],
        cash_flow: Optional[CashFlowStatement]
    ) -> Dict[str, CalculatedMetric]:
        """Calculate cash quality and accrual integrity metrics."""
        metrics: Dict[str, CalculatedMetric] = {}

        if not income or not cash_flow:
            return metrics

        pat = income.net_profit_attributable_to_owners or income.profit_after_tax or 0.0
        cfo = cash_flow.cash_from_operating_activities or 0.0
        fcf = cash_flow.free_cash_flow or (cfo - (cash_flow.capital_expenditure or 0.0))
        tot_rev = income.total_revenue or income.revenue_from_operations or 0.0
        tot_assets = balance.total_assets if balance else 0.0
        tot_debt = ((balance.non_current_borrowings or 0.0) + (balance.current_borrowings or 0.0)) if balance else 0.0

        # 1. CFO to PAT Ratio = Cash from Operations / Net Profit
        if pat > 0:
            cfo_to_pat = round(cfo / pat, 2)
            metrics["CFO_TO_PAT"] = CalculatedMetric(
                metric_key="CFO_TO_PAT",
                metric_label="CFO to Net Profit Ratio (Cash Conversion)",
                value=cfo_to_pat,
                formatted_value=f"{cfo_to_pat:.2f}x",
                unit="MULTIPLIER",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="Cash from Operations / Net Profit",
                inputs={"cfo": cfo, "net_profit": pat},
                is_valid=True,
                notes="Target >= 1.0x. Values < 0.8x indicate aggressive accrual accounting or working capital drag."
            )
        else:
            metrics["CFO_TO_PAT"] = CalculatedMetric(
                metric_key="CFO_TO_PAT",
                metric_label="CFO to Net Profit Ratio",
                value=None,
                formatted_value="N/A",
                unit="MULTIPLIER",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="Cash from Operations / Net Profit",
                inputs={"cfo": cfo, "net_profit": pat},
                is_valid=False,
                notes="Net profit is zero or negative."
            )

        # 2. FCF to PAT Ratio = Free Cash Flow / Net Profit
        if pat > 0:
            fcf_to_pat = round(fcf / pat, 2)
            metrics["FCF_TO_PAT"] = CalculatedMetric(
                metric_key="FCF_TO_PAT",
                metric_label="FCF to Net Profit Ratio",
                value=fcf_to_pat,
                formatted_value=f"{fcf_to_pat:.2f}x",
                unit="MULTIPLIER",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="Free Cash Flow / Net Profit",
                inputs={"fcf": fcf, "net_profit": pat},
                is_valid=True
            )
        else:
            metrics["FCF_TO_PAT"] = CalculatedMetric(
                metric_key="FCF_TO_PAT",
                metric_label="FCF to Net Profit Ratio",
                value=None,
                formatted_value="N/A",
                unit="MULTIPLIER",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="Free Cash Flow / Net Profit",
                inputs={"fcf": fcf, "net_profit": pat},
                is_valid=False
            )

        # 3. Sloan Accruals Ratio = (PAT - CFO) / Total Assets
        if tot_assets > 0:
            accruals_amt = round(pat - cfo, 4)
            sloan_ratio = round((accruals_amt / tot_assets) * 100.0, 2)
            metrics["SLOAN_ACCRUALS_RATIO"] = CalculatedMetric(
                metric_key="SLOAN_ACCRUALS_RATIO",
                metric_label="Sloan Accruals Ratio (Earnings Quality)",
                value=sloan_ratio,
                formatted_value=f"{sloan_ratio:.2f}%",
                unit="PERCENT",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="(Net Profit - Cash from Operations) / Total Assets * 100",
                inputs={"net_profit": pat, "cfo": cfo, "accruals_amount": accruals_amt, "total_assets": tot_assets},
                is_valid=True,
                notes="Values between -10% and +10% represent clean accruals. Values > +10% indicate low cash realization."
            )

        # 4. FCF Margin = Free Cash Flow / Total Revenue
        if tot_rev > 0:
            fcf_margin = round((fcf / tot_rev) * 100.0, 2)
            metrics["FCF_MARGIN"] = CalculatedMetric(
                metric_key="FCF_MARGIN",
                metric_label="Free Cash Flow Margin",
                value=fcf_margin,
                formatted_value=f"{fcf_margin:.2f}%",
                unit="PERCENT",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="Free Cash Flow / Total Revenue * 100",
                inputs={"fcf": fcf, "total_revenue": tot_rev},
                is_valid=True
            )

        # 5. Operating Cash Flow to Total Debt (Cash Coverage)
        if tot_debt > 0:
            cfo_to_debt = round(cfo / tot_debt, 2)
            metrics["CFO_TO_DEBT"] = CalculatedMetric(
                metric_key="CFO_TO_DEBT",
                metric_label="CFO to Total Debt Coverage",
                value=cfo_to_debt,
                formatted_value=f"{cfo_to_debt:.2f}x",
                unit="MULTIPLIER",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="Cash from Operations / Total Debt",
                inputs={"cfo": cfo, "total_debt": tot_debt},
                is_valid=True
            )
        else:
            metrics["CFO_TO_DEBT"] = CalculatedMetric(
                metric_key="CFO_TO_DEBT",
                metric_label="CFO to Total Debt Coverage",
                value=None,
                formatted_value="Debt Free",
                unit="MULTIPLIER",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="Cash from Operations / Total Debt",
                inputs={"cfo": cfo, "total_debt": tot_debt},
                is_valid=True,
                notes="Company has zero debt borrowings."
            )

        return metrics
