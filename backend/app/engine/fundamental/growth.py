"""Deterministic Growth & Historical Trajectory Engine.

Calculates YoY Growth and Multi-Period Compound Annual Growth Rate (CAGR):
- Revenue YoY & CAGR
- EBITDA YoY & CAGR
- EBIT YoY & CAGR
- PAT YoY & CAGR
- Cash from Operations (CFO) YoY & CAGR
- Free Cash Flow (FCF) YoY & CAGR

Handles zero/negative base numbers safely without fabricating data.
"""

from typing import List, Dict, Any, Optional, Tuple
from app.models.financial_period import FinancialPeriod
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement
from app.engine.fundamental.profitability import CalculatedMetric


class GrowthEngine:
    """Calculates deterministic YoY growth rates and multi-year CAGRs."""

    METHODOLOGY_VERSION = "v1.0.0"

    @staticmethod
    def calculate_yoy(curr_val: Optional[float], prev_val: Optional[float]) -> Optional[float]:
        """
        Compute standard YoY percentage change.
        Formula: (Current - Previous) / abs(Previous) * 100
        Returns None if previous value is 0, None, or absent.
        """
        if curr_val is None or prev_val is None or prev_val == 0:
            return None
        return round(((curr_val - prev_val) / abs(prev_val)) * 100.0, 2)

    @staticmethod
    def calculate_cagr(latest_val: Optional[float], base_val: Optional[float], num_years: int) -> Optional[float]:
        """
        Compute Compound Annual Growth Rate.
        Formula: (Latest / Base)^(1 / num_years) - 1
        Strict constraints:
        - num_years must be >= 1
        - base_val and latest_val must be strictly positive
        Returns None if base_val <= 0 or latest_val <= 0 or num_years < 1.
        """
        if latest_val is None or base_val is None or num_years < 1:
            return None
        if base_val <= 0 or latest_val <= 0:
            return None
        try:
            cagr = ((latest_val / base_val) ** (1.0 / float(num_years))) - 1.0
            return round(cagr * 100.0, 2)
        except Exception:
            return None

    @classmethod
    def calculate_period_growth(
        cls,
        current_data: Dict[str, Any],
        previous_data: Optional[Dict[str, Any]]
    ) -> Dict[str, CalculatedMetric]:
        """Calculate YoY growth metrics between current and prior fiscal period."""
        metrics: Dict[str, CalculatedMetric] = {}
        if not previous_data:
            return metrics

        # 1. Revenue YoY Growth
        curr_rev = current_data.get("total_revenue")
        prev_rev = previous_data.get("total_revenue")
        rev_growth = cls.calculate_yoy(curr_rev, prev_rev)
        metrics["REVENUE_GROWTH_YOY"] = CalculatedMetric(
            metric_key="REVENUE_GROWTH_YOY",
            metric_label="Revenue Growth (YoY)",
            value=rev_growth,
            formatted_value=f"{rev_growth:.2f}%" if rev_growth is not None else "N/A",
            unit="PERCENT",
            methodology_version=cls.METHODOLOGY_VERSION,
            formula_expression="(Revenue(t) - Revenue(t-1)) / abs(Revenue(t-1)) * 100",
            inputs={"current_revenue": curr_rev, "previous_revenue": prev_rev},
            is_valid=rev_growth is not None,
            notes="Requires prior period revenue." if rev_growth is None else None
        )

        # 2. EBITDA YoY Growth
        curr_ebitda = current_data.get("ebitda")
        prev_ebitda = previous_data.get("ebitda")
        ebitda_growth = cls.calculate_yoy(curr_ebitda, prev_ebitda)
        metrics["EBITDA_GROWTH_YOY"] = CalculatedMetric(
            metric_key="EBITDA_GROWTH_YOY",
            metric_label="EBITDA Growth (YoY)",
            value=ebitda_growth,
            formatted_value=f"{ebitda_growth:.2f}%" if ebitda_growth is not None else "N/A",
            unit="PERCENT",
            methodology_version=cls.METHODOLOGY_VERSION,
            formula_expression="(EBITDA(t) - EBITDA(t-1)) / abs(EBITDA(t-1)) * 100",
            inputs={"current_ebitda": curr_ebitda, "previous_ebitda": prev_ebitda},
            is_valid=ebitda_growth is not None
        )

        # 3. EBIT YoY Growth
        curr_ebit = current_data.get("ebit")
        prev_ebit = previous_data.get("ebit")
        ebit_growth = cls.calculate_yoy(curr_ebit, prev_ebit)
        metrics["EBIT_GROWTH_YOY"] = CalculatedMetric(
            metric_key="EBIT_GROWTH_YOY",
            metric_label="EBIT Growth (YoY)",
            value=ebit_growth,
            formatted_value=f"{ebit_growth:.2f}%" if ebit_growth is not None else "N/A",
            unit="PERCENT",
            methodology_version=cls.METHODOLOGY_VERSION,
            formula_expression="(EBIT(t) - EBIT(t-1)) / abs(EBIT(t-1)) * 100",
            inputs={"current_ebit": curr_ebit, "previous_ebit": prev_ebit},
            is_valid=ebit_growth is not None
        )

        # 4. PAT (Net Profit) YoY Growth
        curr_pat = current_data.get("net_profit")
        prev_pat = previous_data.get("net_profit")
        pat_growth = cls.calculate_yoy(curr_pat, prev_pat)
        metrics["PAT_GROWTH_YOY"] = CalculatedMetric(
            metric_key="PAT_GROWTH_YOY",
            metric_label="Net Profit Growth (PAT YoY)",
            value=pat_growth,
            formatted_value=f"{pat_growth:.2f}%" if pat_growth is not None else "N/A",
            unit="PERCENT",
            methodology_version=cls.METHODOLOGY_VERSION,
            formula_expression="(PAT(t) - PAT(t-1)) / abs(PAT(t-1)) * 100",
            inputs={"current_pat": curr_pat, "previous_pat": prev_pat},
            is_valid=pat_growth is not None
        )

        # 5. CFO YoY Growth
        curr_cfo = current_data.get("cfo")
        prev_cfo = previous_data.get("cfo")
        cfo_growth = cls.calculate_yoy(curr_cfo, prev_cfo)
        metrics["CFO_GROWTH_YOY"] = CalculatedMetric(
            metric_key="CFO_GROWTH_YOY",
            metric_label="Operating Cash Flow Growth (CFO YoY)",
            value=cfo_growth,
            formatted_value=f"{cfo_growth:.2f}%" if cfo_growth is not None else "N/A",
            unit="PERCENT",
            methodology_version=cls.METHODOLOGY_VERSION,
            formula_expression="(CFO(t) - CFO(t-1)) / abs(CFO(t-1)) * 100",
            inputs={"current_cfo": curr_cfo, "previous_cfo": prev_cfo},
            is_valid=cfo_growth is not None
        )

        return metrics
