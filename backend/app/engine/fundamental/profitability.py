"""Deterministic Profitability Engine.

Calculates margins and capital return metrics:
- Gross Margin
- EBITDA Margin
- EBIT Margin
- PAT (Net) Margin
- Return on Assets (ROA)
- Return on Equity (ROE)
- Return on Capital Employed (ROCE)
- Return on Invested Capital (ROIC)
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement


class CalculatedMetric(BaseModel):
    """Standardized analytical metric payload with methodology version and formula inputs."""
    metric_key: str
    metric_label: str
    value: Optional[float] = None
    formatted_value: str
    unit: str = "PERCENT"  # PERCENT, RATIO, DAYS, MULTIPLIER
    methodology_version: str = "v1.0.0"
    formula_expression: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    is_valid: bool = True
    notes: Optional[str] = None


class ProfitabilityEngine:
    """Pure mathematical routines for corporate profitability and returns analysis."""

    METHODOLOGY_VERSION = "v1.0.0"

    @classmethod
    def calculate_all(
        cls,
        income: Optional[IncomeStatement],
        balance: Optional[BalanceSheet],
        cash_flow: Optional[CashFlowStatement] = None
    ) -> Dict[str, CalculatedMetric]:
        """Compute all profitability metrics for a given financial period."""
        metrics: Dict[str, CalculatedMetric] = {}

        if not income:
            return metrics

        rev = income.total_revenue
        rev_ops = income.revenue_from_operations

        # 1. Gross Profit & Gross Margin
        cogs = (
            (income.cost_of_materials_consumed or 0.0)
            + (income.purchases_of_stock_in_trade or 0.0)
            + (income.changes_in_inventories or 0.0)
        )
        gross_profit = round(rev_ops - cogs, 4)
        if rev_ops > 0:
            gm_val = round((gross_profit / rev_ops) * 100.0, 2)
            metrics["GROSS_MARGIN"] = CalculatedMetric(
                metric_key="GROSS_MARGIN",
                metric_label="Gross Profit Margin",
                value=gm_val,
                formatted_value=f"{gm_val:.2f}%",
                unit="PERCENT",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="(Revenue from Operations - COGS) / Revenue from Operations * 100",
                inputs={"revenue_from_operations": rev_ops, "cogs": cogs, "gross_profit": gross_profit},
                is_valid=True
            )
        else:
            metrics["GROSS_MARGIN"] = CalculatedMetric(
                metric_key="GROSS_MARGIN",
                metric_label="Gross Profit Margin",
                value=None,
                formatted_value="N/A",
                unit="PERCENT",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="(Revenue from Operations - COGS) / Revenue from Operations * 100",
                inputs={"revenue_from_operations": rev_ops, "cogs": cogs},
                is_valid=False,
                notes="Revenue from operations is zero or negative."
            )

        # 2. EBITDA & EBITDA Margin
        ebitda = round(
            (income.profit_before_tax or 0.0)
            + (income.finance_costs or 0.0)
            + (income.depreciation_and_amortization or 0.0)
            - (income.exceptional_items or 0.0),
            4
        )
        if rev > 0:
            ebitda_margin = round((ebitda / rev) * 100.0, 2)
            metrics["EBITDA_MARGIN"] = CalculatedMetric(
                metric_key="EBITDA_MARGIN",
                metric_label="EBITDA Margin",
                value=ebitda_margin,
                formatted_value=f"{ebitda_margin:.2f}%",
                unit="PERCENT",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="(PBT + Finance Costs + D&A - Exceptional Items) / Total Revenue * 100",
                inputs={"pbt": income.profit_before_tax, "finance_costs": income.finance_costs, "depreciation": income.depreciation_and_amortization, "ebitda": ebitda, "total_revenue": rev},
                is_valid=True
            )
        else:
            metrics["EBITDA_MARGIN"] = CalculatedMetric(
                metric_key="EBITDA_MARGIN",
                metric_label="EBITDA Margin",
                value=None,
                formatted_value="N/A",
                unit="PERCENT",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="EBITDA / Total Revenue * 100",
                inputs={"total_revenue": rev},
                is_valid=False
            )

        # 3. EBIT (Operating Profit) & EBIT Margin
        ebit = round((income.profit_before_tax or 0.0) + (income.finance_costs or 0.0), 4)
        if rev > 0:
            ebit_margin = round((ebit / rev) * 100.0, 2)
            metrics["EBIT_MARGIN"] = CalculatedMetric(
                metric_key="EBIT_MARGIN",
                metric_label="EBIT Margin (Operating Margin)",
                value=ebit_margin,
                formatted_value=f"{ebit_margin:.2f}%",
                unit="PERCENT",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="(Profit Before Tax + Finance Costs) / Total Revenue * 100",
                inputs={"pbt": income.profit_before_tax, "finance_costs": income.finance_costs, "ebit": ebit, "total_revenue": rev},
                is_valid=True
            )
        else:
            metrics["EBIT_MARGIN"] = CalculatedMetric(
                metric_key="EBIT_MARGIN",
                metric_label="EBIT Margin",
                value=None,
                formatted_value="N/A",
                unit="PERCENT",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="EBIT / Total Revenue * 100",
                inputs={"total_revenue": rev},
                is_valid=False
            )

        # 4. PAT (Net Profit) Margin
        pat = income.net_profit_attributable_to_owners or income.profit_after_tax or 0.0
        if rev > 0:
            pat_margin = round((pat / rev) * 100.0, 2)
            metrics["PAT_MARGIN"] = CalculatedMetric(
                metric_key="PAT_MARGIN",
                metric_label="Net Profit Margin (PAT Margin)",
                value=pat_margin,
                formatted_value=f"{pat_margin:.2f}%",
                unit="PERCENT",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="Net Profit Attributable to Owners / Total Revenue * 100",
                inputs={"net_profit": pat, "total_revenue": rev},
                is_valid=True
            )
        else:
            metrics["PAT_MARGIN"] = CalculatedMetric(
                metric_key="PAT_MARGIN",
                metric_label="Net Profit Margin",
                value=None,
                formatted_value="N/A",
                unit="PERCENT",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="Net Profit / Total Revenue * 100",
                inputs={"total_revenue": rev},
                is_valid=False
            )

        # Capital Returns (require BalanceSheet)
        if balance:
            tot_assets = balance.total_assets
            tot_equity = balance.total_equity
            curr_liab = balance.total_current_liabilities
            non_curr_liab = balance.total_non_current_liabilities

            # 5. Return on Assets (ROA)
            if tot_assets > 0:
                roa = round((pat / tot_assets) * 100.0, 2)
                metrics["ROA"] = CalculatedMetric(
                    metric_key="ROA",
                    metric_label="Return on Assets (ROA)",
                    value=roa,
                    formatted_value=f"{roa:.2f}%",
                    unit="PERCENT",
                    methodology_version=cls.METHODOLOGY_VERSION,
                    formula_expression="Net Profit / Total Assets * 100",
                    inputs={"net_profit": pat, "total_assets": tot_assets},
                    is_valid=True
                )
            else:
                metrics["ROA"] = CalculatedMetric(
                    metric_key="ROA",
                    metric_label="Return on Assets (ROA)",
                    value=None,
                    formatted_value="N/A",
                    unit="PERCENT",
                    methodology_version=cls.METHODOLOGY_VERSION,
                    formula_expression="Net Profit / Total Assets * 100",
                    inputs={"total_assets": tot_assets},
                    is_valid=False
                )

            # 6. Return on Equity (ROE)
            if tot_equity > 0:
                roe = round((pat / tot_equity) * 100.0, 2)
                metrics["ROE"] = CalculatedMetric(
                    metric_key="ROE",
                    metric_label="Return on Equity (ROE)",
                    value=roe,
                    formatted_value=f"{roe:.2f}%",
                    unit="PERCENT",
                    methodology_version=cls.METHODOLOGY_VERSION,
                    formula_expression="Net Profit Attributable to Owners / Total Shareholders' Equity * 100",
                    inputs={"net_profit": pat, "total_equity": tot_equity},
                    is_valid=True
                )
            else:
                metrics["ROE"] = CalculatedMetric(
                    metric_key="ROE",
                    metric_label="Return on Equity (ROE)",
                    value=None,
                    formatted_value="N/A",
                    unit="PERCENT",
                    methodology_version=cls.METHODOLOGY_VERSION,
                    formula_expression="Net Profit / Total Equity * 100",
                    inputs={"total_equity": tot_equity},
                    is_valid=False,
                    notes="Shareholders' equity is zero or negative."
                )

            # 7. Return on Capital Employed (ROCE)
            capital_employed = round(tot_assets - curr_liab, 4)
            if capital_employed > 0:
                roce = round((ebit / capital_employed) * 100.0, 2)
                metrics["ROCE"] = CalculatedMetric(
                    metric_key="ROCE",
                    metric_label="Return on Capital Employed (ROCE)",
                    value=roce,
                    formatted_value=f"{roce:.2f}%",
                    unit="PERCENT",
                    methodology_version=cls.METHODOLOGY_VERSION,
                    formula_expression="EBIT / (Total Assets - Current Liabilities) * 100",
                    inputs={"ebit": ebit, "total_assets": tot_assets, "current_liabilities": curr_liab, "capital_employed": capital_employed},
                    is_valid=True
                )
            else:
                metrics["ROCE"] = CalculatedMetric(
                    metric_key="ROCE",
                    metric_label="Return on Capital Employed (ROCE)",
                    value=None,
                    formatted_value="N/A",
                    unit="PERCENT",
                    methodology_version=cls.METHODOLOGY_VERSION,
                    formula_expression="EBIT / (Total Assets - Current Liabilities) * 100",
                    inputs={"capital_employed": capital_employed},
                    is_valid=False
                )

            # 8. Return on Invested Capital (ROIC)
            # Effective Tax Rate
            pbt = income.profit_before_tax or 0.0
            tax_exp = income.total_tax_expense or 0.0
            eff_tax_rate = max(0.0, min(0.40, (tax_exp / pbt))) if pbt > 0 else 0.25
            nopat = round(ebit * (1.0 - eff_tax_rate), 4)

            total_debt = (balance.non_current_borrowings or 0.0) + (balance.current_borrowings or 0.0)
            cash_eq = (balance.cash_and_cash_equivalents or 0.0) + (balance.bank_balances_other or 0.0)
            invested_capital = round(tot_equity + total_debt - cash_eq, 4)

            if invested_capital > 0:
                roic = round((nopat / invested_capital) * 100.0, 2)
                metrics["ROIC"] = CalculatedMetric(
                    metric_key="ROIC",
                    metric_label="Return on Invested Capital (ROIC)",
                    value=roic,
                    formatted_value=f"{roic:.2f}%",
                    unit="PERCENT",
                    methodology_version=cls.METHODOLOGY_VERSION,
                    formula_expression="NOPAT / (Equity + Total Debt - Cash & Bank) * 100",
                    inputs={
                        "ebit": ebit,
                        "effective_tax_rate": round(eff_tax_rate * 100, 2),
                        "nopat": nopat,
                        "total_equity": tot_equity,
                        "total_debt": total_debt,
                        "cash_and_equivalents": cash_eq,
                        "invested_capital": invested_capital
                    },
                    is_valid=True
                )
            else:
                metrics["ROIC"] = CalculatedMetric(
                    metric_key="ROIC",
                    metric_label="Return on Invested Capital (ROIC)",
                    value=None,
                    formatted_value="N/A",
                    unit="PERCENT",
                    methodology_version=cls.METHODOLOGY_VERSION,
                    formula_expression="NOPAT / Invested Capital * 100",
                    inputs={"invested_capital": invested_capital},
                    is_valid=False,
                    notes="Invested capital is zero or negative (high net cash position)."
                )

        return metrics
