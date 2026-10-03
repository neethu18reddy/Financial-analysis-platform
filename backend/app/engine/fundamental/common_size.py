"""Deterministic Common-Size Financial Statement Engine.

Converts:
- Income Statement line items into percentage of Total Revenue (100.0%)
- Balance Sheet line items into percentage of Total Assets (100.0%)
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from app.models.financial_statements import IncomeStatement, BalanceSheet


class CommonSizeLineItem(BaseModel):
    line_item_key: str
    line_item_label: str
    raw_value: float
    percentage_of_base: float
    base_label: str  # "Total Revenue" or "Total Assets"


class CommonSizeIncomeStatement(BaseModel):
    base_revenue: float
    items: List[CommonSizeLineItem]


class CommonSizeBalanceSheet(BaseModel):
    base_assets: float
    items: List[CommonSizeLineItem]


class CommonSizeEngine:
    """Calculates deterministic common-size vertical percentage statements."""

    @staticmethod
    def calculate_income_statement(income: Optional[IncomeStatement]) -> Optional[CommonSizeIncomeStatement]:
        """Convert Income Statement items into % of Total Revenue."""
        if not income:
            return None

        base_rev = income.total_revenue or income.revenue_from_operations or 0.0
        if base_rev <= 0:
            return None

        def pct(v: Optional[float]) -> float:
            if v is None:
                return 0.0
            return round((v / base_rev) * 100.0, 2)

        def val(v: Optional[float]) -> float:
            return float(v or 0.0)

        items = [
            CommonSizeLineItem(line_item_key="revenue_from_operations", line_item_label="Revenue from Operations", raw_value=val(income.revenue_from_operations), percentage_of_base=pct(income.revenue_from_operations), base_label="Total Revenue"),
            CommonSizeLineItem(line_item_key="other_income", line_item_label="Other Income", raw_value=val(income.other_income), percentage_of_base=pct(income.other_income), base_label="Total Revenue"),
            CommonSizeLineItem(line_item_key="total_revenue", line_item_label="Total Revenue", raw_value=val(income.total_revenue), percentage_of_base=100.0, base_label="Total Revenue"),
            CommonSizeLineItem(line_item_key="cost_of_materials_consumed", line_item_label="Cost of Materials Consumed", raw_value=val(income.cost_of_materials_consumed), percentage_of_base=pct(income.cost_of_materials_consumed), base_label="Total Revenue"),
            CommonSizeLineItem(line_item_key="purchases_of_stock_in_trade", line_item_label="Purchases of Stock-in-Trade", raw_value=val(income.purchases_of_stock_in_trade), percentage_of_base=pct(income.purchases_of_stock_in_trade), base_label="Total Revenue"),
            CommonSizeLineItem(line_item_key="employee_benefit_expenses", line_item_label="Employee Benefit Expenses", raw_value=val(income.employee_benefit_expenses), percentage_of_base=pct(income.employee_benefit_expenses), base_label="Total Revenue"),
            CommonSizeLineItem(line_item_key="finance_costs", line_item_label="Finance Costs", raw_value=val(income.finance_costs), percentage_of_base=pct(income.finance_costs), base_label="Total Revenue"),
            CommonSizeLineItem(line_item_key="depreciation_and_amortization", line_item_label="Depreciation & Amortization", raw_value=val(income.depreciation_and_amortization), percentage_of_base=pct(income.depreciation_and_amortization), base_label="Total Revenue"),
            CommonSizeLineItem(line_item_key="other_expenses", line_item_label="Other Expenses", raw_value=val(income.other_expenses), percentage_of_base=pct(income.other_expenses), base_label="Total Revenue"),
            CommonSizeLineItem(line_item_key="total_expenses", line_item_label="Total Expenses", raw_value=val(income.total_expenses), percentage_of_base=pct(income.total_expenses), base_label="Total Revenue"),
            CommonSizeLineItem(line_item_key="profit_before_tax", line_item_label="Profit Before Tax (PBT)", raw_value=val(income.profit_before_tax), percentage_of_base=pct(income.profit_before_tax), base_label="Total Revenue"),
            CommonSizeLineItem(line_item_key="total_tax_expense", line_item_label="Total Tax Expense", raw_value=val(income.total_tax_expense), percentage_of_base=pct(income.total_tax_expense), base_label="Total Revenue"),
            CommonSizeLineItem(line_item_key="profit_after_tax", line_item_label="Profit After Tax (PAT)", raw_value=val(income.profit_after_tax), percentage_of_base=pct(income.profit_after_tax), base_label="Total Revenue"),
            CommonSizeLineItem(line_item_key="net_profit_attributable_to_owners", line_item_label="Net Profit Attributable to Owners", raw_value=val(income.net_profit_attributable_to_owners), percentage_of_base=pct(income.net_profit_attributable_to_owners), base_label="Total Revenue"),
        ]
        return CommonSizeIncomeStatement(base_revenue=base_rev, items=items)

    @staticmethod
    def calculate_balance_sheet(balance: Optional[BalanceSheet]) -> Optional[CommonSizeBalanceSheet]:
        """Convert Balance Sheet items into % of Total Assets."""
        if not balance:
            return None

        base_assets = balance.total_assets or 0.0
        if base_assets <= 0:
            return None

        def pct(v: Optional[float]) -> float:
            if v is None:
                return 0.0
            return round((v / base_assets) * 100.0, 2)

        def val(v: Optional[float]) -> float:
            return float(v or 0.0)

        items = [
            CommonSizeLineItem(line_item_key="property_plant_equipment", line_item_label="Property, Plant & Equipment", raw_value=val(balance.property_plant_equipment), percentage_of_base=pct(balance.property_plant_equipment), base_label="Total Assets"),
            CommonSizeLineItem(line_item_key="capital_work_in_progress", line_item_label="Capital Work-in-Progress", raw_value=val(balance.capital_work_in_progress), percentage_of_base=pct(balance.capital_work_in_progress), base_label="Total Assets"),
            CommonSizeLineItem(line_item_key="goodwill_and_intangibles", line_item_label="Goodwill & Intangibles", raw_value=val(balance.goodwill_and_intangibles), percentage_of_base=pct(balance.goodwill_and_intangibles), base_label="Total Assets"),
            CommonSizeLineItem(line_item_key="non_current_investments", line_item_label="Non-Current Investments", raw_value=val(balance.non_current_investments), percentage_of_base=pct(balance.non_current_investments), base_label="Total Assets"),
            CommonSizeLineItem(line_item_key="total_non_current_assets", line_item_label="Total Non-Current Assets", raw_value=val(balance.total_non_current_assets), percentage_of_base=pct(balance.total_non_current_assets), base_label="Total Assets"),
            CommonSizeLineItem(line_item_key="inventories", line_item_label="Inventories", raw_value=val(balance.inventories), percentage_of_base=pct(balance.inventories), base_label="Total Assets"),
            CommonSizeLineItem(line_item_key="trade_receivables", line_item_label="Trade Receivables", raw_value=val(balance.trade_receivables), percentage_of_base=pct(balance.trade_receivables), base_label="Total Assets"),
            CommonSizeLineItem(line_item_key="cash_and_cash_equivalents", line_item_label="Cash & Cash Equivalents", raw_value=val(balance.cash_and_cash_equivalents), percentage_of_base=pct(balance.cash_and_cash_equivalents), base_label="Total Assets"),
            CommonSizeLineItem(line_item_key="total_current_assets", line_item_label="Total Current Assets", raw_value=val(balance.total_current_assets), percentage_of_base=pct(balance.total_current_assets), base_label="Total Assets"),
            CommonSizeLineItem(line_item_key="total_assets", line_item_label="TOTAL ASSETS", raw_value=val(balance.total_assets), percentage_of_base=100.0, base_label="Total Assets"),
            CommonSizeLineItem(line_item_key="total_equity", line_item_label="Total Shareholders' Equity", raw_value=val(balance.total_equity), percentage_of_base=pct(balance.total_equity), base_label="Total Assets"),
            CommonSizeLineItem(line_item_key="total_non_current_liabilities", line_item_label="Total Non-Current Liabilities", raw_value=val(balance.total_non_current_liabilities), percentage_of_base=pct(balance.total_non_current_liabilities), base_label="Total Assets"),
            CommonSizeLineItem(line_item_key="total_current_liabilities", line_item_label="Total Current Liabilities", raw_value=val(balance.total_current_liabilities), percentage_of_base=pct(balance.total_current_liabilities), base_label="Total Assets"),
            CommonSizeLineItem(line_item_key="total_liabilities", line_item_label="Total Liabilities", raw_value=val(balance.total_liabilities), percentage_of_base=pct(balance.total_liabilities), base_label="Total Assets"),
        ]
        return CommonSizeBalanceSheet(base_assets=base_assets, items=items)
