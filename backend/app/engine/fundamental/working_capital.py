"""Deterministic Working Capital & Efficiency Engine.

Calculates:
- Days Sales Outstanding (DSO) / Receivables Days
- Days Inventory Outstanding (DIO) / Inventory Days
- Days Payables Outstanding (DPO) / Payables Days
- Cash Conversion Cycle (CCC = DIO + DSO - DPO)
- Total Asset Turnover
- Working Capital Turnover
- Current Ratio & Quick Ratio
"""

from typing import Dict, Any, Optional
from app.models.financial_statements import IncomeStatement, BalanceSheet
from app.engine.fundamental.profitability import CalculatedMetric


class WorkingCapitalEngine:
    """Calculates efficiency metrics and working capital duration cycles in days."""

    METHODOLOGY_VERSION = "v1.0.0"

    @classmethod
    def calculate_all(
        cls,
        income: Optional[IncomeStatement],
        balance: Optional[BalanceSheet]
    ) -> Dict[str, CalculatedMetric]:
        """Calculate working capital and efficiency cycles."""
        metrics: Dict[str, CalculatedMetric] = {}

        if not income or not balance:
            return metrics

        rev = income.total_revenue or income.revenue_from_operations or 0.0
        cogs = (
            (income.cost_of_materials_consumed or 0.0)
            + (income.purchases_of_stock_in_trade or 0.0)
            + (income.changes_in_inventories or 0.0)
        )
        # For software/service companies, COGS might be 0; use Total Revenue for base turnover if COGS is 0
        cogs_base = cogs if cogs > 0 else (income.total_expenses or rev)

        receivables = balance.trade_receivables or 0.0
        inventory = balance.inventories or 0.0
        payables = balance.trade_payables or 0.0
        tot_assets = balance.total_assets or 0.0
        curr_assets = balance.total_current_assets or 0.0
        curr_liab = balance.total_current_liabilities or 0.0

        # 1. Days Sales Outstanding (DSO) = (Trade Receivables / Revenue) * 365
        if rev > 0:
            dso = round((receivables / rev) * 365.0, 1)
            metrics["DSO"] = CalculatedMetric(
                metric_key="DSO",
                metric_label="Days Sales Outstanding (DSO)",
                value=dso,
                formatted_value=f"{dso:.1f} days",
                unit="DAYS",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="(Trade Receivables / Total Revenue) * 365",
                inputs={"trade_receivables": receivables, "total_revenue": rev},
                is_valid=True
            )
        else:
            metrics["DSO"] = CalculatedMetric(
                metric_key="DSO",
                metric_label="Days Sales Outstanding (DSO)",
                value=None,
                formatted_value="N/A",
                unit="DAYS",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="(Trade Receivables / Total Revenue) * 365",
                inputs={"trade_receivables": receivables, "total_revenue": rev},
                is_valid=False
            )

        # 2. Days Inventory Outstanding (DIO) = (Inventories / COGS) * 365
        if cogs_base > 0 and inventory > 0:
            dio = round((inventory / cogs_base) * 365.0, 1)
            metrics["DIO"] = CalculatedMetric(
                metric_key="DIO",
                metric_label="Days Inventory Outstanding (DIO)",
                value=dio,
                formatted_value=f"{dio:.1f} days",
                unit="DAYS",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="(Inventories / Cost of Goods Sold) * 365",
                inputs={"inventories": inventory, "cogs": cogs_base},
                is_valid=True
            )
        else:
            # Service company with 0 inventory
            metrics["DIO"] = CalculatedMetric(
                metric_key="DIO",
                metric_label="Days Inventory Outstanding (DIO)",
                value=0.0 if inventory == 0 else None,
                formatted_value="0.0 days" if inventory == 0 else "N/A",
                unit="DAYS",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="(Inventories / COGS) * 365",
                inputs={"inventories": inventory, "cogs": cogs_base},
                is_valid=True if inventory == 0 else False,
                notes="Zero inventory (typical for IT services / asset-light firms)." if inventory == 0 else "No COGS base available."
            )

        # 3. Days Payables Outstanding (DPO) = (Trade Payables / COGS) * 365
        if cogs_base > 0 and payables > 0:
            dpo = round((payables / cogs_base) * 365.0, 1)
            metrics["DPO"] = CalculatedMetric(
                metric_key="DPO",
                metric_label="Days Payables Outstanding (DPO)",
                value=dpo,
                formatted_value=f"{dpo:.1f} days",
                unit="DAYS",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="(Trade Payables / Cost of Goods Sold) * 365",
                inputs={"trade_payables": payables, "cogs": cogs_base},
                is_valid=True
            )
        else:
            metrics["DPO"] = CalculatedMetric(
                metric_key="DPO",
                metric_label="Days Payables Outstanding (DPO)",
                value=0.0 if payables == 0 else None,
                formatted_value="0.0 days" if payables == 0 else "N/A",
                unit="DAYS",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="(Trade Payables / COGS) * 365",
                inputs={"trade_payables": payables, "cogs": cogs_base},
                is_valid=True if payables == 0 else False
            )

        # 4. Cash Conversion Cycle (CCC) = DIO + DSO - DPO
        dso_v = metrics["DSO"].value if "DSO" in metrics else None
        dio_v = metrics["DIO"].value if "DIO" in metrics else None
        dpo_v = metrics["DPO"].value if "DPO" in metrics else None

        if dso_v is not None and dio_v is not None and dpo_v is not None:
            ccc = round(dio_v + dso_v - dpo_v, 1)
            metrics["CASH_CONVERSION_CYCLE"] = CalculatedMetric(
                metric_key="CASH_CONVERSION_CYCLE",
                metric_label="Cash Conversion Cycle (CCC)",
                value=ccc,
                formatted_value=f"{ccc:.1f} days",
                unit="DAYS",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="DIO + DSO - DPO",
                inputs={"dio": dio_v, "dso": dso_v, "dpo": dpo_v},
                is_valid=True,
                notes="Negative CCC indicates high supplier financing power (working capital provided by vendors)." if ccc < 0 else None
            )
        else:
            metrics["CASH_CONVERSION_CYCLE"] = CalculatedMetric(
                metric_key="CASH_CONVERSION_CYCLE",
                metric_label="Cash Conversion Cycle (CCC)",
                value=None,
                formatted_value="N/A",
                unit="DAYS",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="DIO + DSO - DPO",
                inputs={"dio": dio_v, "dso": dso_v, "dpo": dpo_v},
                is_valid=False
            )

        # 5. Asset Turnover = Total Revenue / Total Assets
        if tot_assets > 0:
            asset_turnover = round(rev / tot_assets, 2)
            metrics["ASSET_TURNOVER"] = CalculatedMetric(
                metric_key="ASSET_TURNOVER",
                metric_label="Total Asset Turnover",
                value=asset_turnover,
                formatted_value=f"{asset_turnover:.2f}x",
                unit="MULTIPLIER",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="Total Revenue / Total Assets",
                inputs={"total_revenue": rev, "total_assets": tot_assets},
                is_valid=True
            )

        # 6. Current Ratio = Current Assets / Current Liabilities
        if curr_liab > 0:
            current_ratio = round(curr_assets / curr_liab, 2)
            metrics["CURRENT_RATIO"] = CalculatedMetric(
                metric_key="CURRENT_RATIO",
                metric_label="Current Ratio (Liquidity)",
                value=current_ratio,
                formatted_value=f"{current_ratio:.2f}x",
                unit="RATIO",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="Total Current Assets / Total Current Liabilities",
                inputs={"current_assets": curr_assets, "current_liabilities": curr_liab},
                is_valid=True
            )

        # 7. Quick Ratio = (Current Assets - Inventories) / Current Liabilities
        if curr_liab > 0:
            quick_assets = curr_assets - inventory
            quick_ratio = round(quick_assets / curr_liab, 2)
            metrics["QUICK_RATIO"] = CalculatedMetric(
                metric_key="QUICK_RATIO",
                metric_label="Quick Ratio (Acid Test)",
                value=quick_ratio,
                formatted_value=f"{quick_ratio:.2f}x",
                unit="RATIO",
                methodology_version=cls.METHODOLOGY_VERSION,
                formula_expression="(Total Current Assets - Inventories) / Total Current Liabilities",
                inputs={"quick_assets": quick_assets, "current_liabilities": curr_liab},
                is_valid=True
            )

        return metrics
