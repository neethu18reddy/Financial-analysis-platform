"""Normalized Financial Statements: Income Statement, Balance Sheet, Cash Flow Statement."""

import enum
from typing import Optional, List
from sqlalchemy import Float, Enum, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class StatementType(str, enum.Enum):
    """Consolidated vs Standalone separation."""
    CONSOLIDATED = "CONSOLIDATED"
    STANDALONE = "STANDALONE"


class IncomeStatement(Base, TimestampMixin):
    """Normalized Income Statement (Statement of Profit and Loss) under Ind AS."""
    __tablename__ = "income_statements"
    __table_args__ = (
        UniqueConstraint("period_id", "statement_type", name="uq_income_statement_period_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period_id: Mapped[int] = mapped_column(
        ForeignKey("financial_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    statement_type: Mapped[StatementType] = mapped_column(
        Enum(StatementType, native_enum=False),
        nullable=False,
        default=StatementType.CONSOLIDATED
    )

    # Revenue
    revenue_from_operations: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    other_income: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_revenue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Expenses
    cost_of_materials_consumed: Mapped[float] = mapped_column(Float, default=0.0)
    purchases_of_stock_in_trade: Mapped[float] = mapped_column(Float, default=0.0)
    changes_in_inventories: Mapped[float] = mapped_column(Float, default=0.0)
    employee_benefit_expenses: Mapped[float] = mapped_column(Float, default=0.0)
    finance_costs: Mapped[float] = mapped_column(Float, default=0.0)
    depreciation_and_amortization: Mapped[float] = mapped_column(Float, default=0.0)
    other_expenses: Mapped[float] = mapped_column(Float, default=0.0)
    total_expenses: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Profit / Loss
    operating_profit: Mapped[float] = mapped_column(Float, default=0.0)  # Total Revenue - Total Expenses + Finance Costs
    profit_before_exceptional_items_and_tax: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    exceptional_items: Mapped[float] = mapped_column(Float, default=0.0)
    profit_before_tax: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Tax & Net Profit
    current_tax: Mapped[float] = mapped_column(Float, default=0.0)
    deferred_tax: Mapped[float] = mapped_column(Float, default=0.0)
    total_tax_expense: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    profit_after_tax: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Minority & Comprehensive
    minority_interest: Mapped[float] = mapped_column(Float, default=0.0)
    share_of_profit_associates: Mapped[float] = mapped_column(Float, default=0.0)
    net_profit_attributable_to_owners: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Per Share Metrics
    basic_eps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    diluted_eps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    raw_payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    period: Mapped["FinancialPeriod"] = relationship("FinancialPeriod", back_populates="income_statements")


class BalanceSheet(Base, TimestampMixin):
    """Normalized Balance Sheet under Ind AS (Schedule III format)."""
    __tablename__ = "balance_sheets"
    __table_args__ = (
        UniqueConstraint("period_id", "statement_type", name="uq_balance_sheet_period_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period_id: Mapped[int] = mapped_column(
        ForeignKey("financial_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    statement_type: Mapped[StatementType] = mapped_column(
        Enum(StatementType, native_enum=False),
        nullable=False,
        default=StatementType.CONSOLIDATED
    )

    # Non-Current Assets
    property_plant_equipment: Mapped[float] = mapped_column(Float, default=0.0)
    capital_work_in_progress: Mapped[float] = mapped_column(Float, default=0.0)
    goodwill_and_intangibles: Mapped[float] = mapped_column(Float, default=0.0)
    non_current_investments: Mapped[float] = mapped_column(Float, default=0.0)
    deferred_tax_assets: Mapped[float] = mapped_column(Float, default=0.0)
    other_non_current_assets: Mapped[float] = mapped_column(Float, default=0.0)
    total_non_current_assets: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Current Assets
    inventories: Mapped[float] = mapped_column(Float, default=0.0)
    trade_receivables: Mapped[float] = mapped_column(Float, default=0.0)
    cash_and_cash_equivalents: Mapped[float] = mapped_column(Float, default=0.0)
    bank_balances_other: Mapped[float] = mapped_column(Float, default=0.0)
    short_term_loans_and_advances: Mapped[float] = mapped_column(Float, default=0.0)
    other_current_assets: Mapped[float] = mapped_column(Float, default=0.0)
    total_current_assets: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Total Assets
    total_assets: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Equity
    equity_share_capital: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    other_equity_and_reserves: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    non_controlling_interests: Mapped[float] = mapped_column(Float, default=0.0)
    total_equity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Non-Current Liabilities
    non_current_borrowings: Mapped[float] = mapped_column(Float, default=0.0)
    deferred_tax_liabilities: Mapped[float] = mapped_column(Float, default=0.0)
    other_non_current_liabilities: Mapped[float] = mapped_column(Float, default=0.0)
    total_non_current_liabilities: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Current Liabilities
    current_borrowings: Mapped[float] = mapped_column(Float, default=0.0)
    trade_payables: Mapped[float] = mapped_column(Float, default=0.0)
    other_current_liabilities: Mapped[float] = mapped_column(Float, default=0.0)
    short_term_provisions: Mapped[float] = mapped_column(Float, default=0.0)
    total_current_liabilities: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Total Liabilities & Equity
    total_liabilities: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_equity_and_liabilities: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    raw_payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    period: Mapped["FinancialPeriod"] = relationship("FinancialPeriod", back_populates="balance_sheets")


class CashFlowStatement(Base, TimestampMixin):
    """Normalized Cash Flow Statement (Direct/Indirect Ind AS format)."""
    __tablename__ = "cash_flow_statements"
    __table_args__ = (
        UniqueConstraint("period_id", "statement_type", name="uq_cash_flow_period_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period_id: Mapped[int] = mapped_column(
        ForeignKey("financial_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    statement_type: Mapped[StatementType] = mapped_column(
        Enum(StatementType, native_enum=False),
        nullable=False,
        default=StatementType.CONSOLIDATED
    )

    # Activities
    cash_from_operating_activities: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cash_from_investing_activities: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cash_from_financing_activities: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Net movement
    net_increase_in_cash: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    foreign_exchange_effect: Mapped[float] = mapped_column(Float, default=0.0)
    cash_beginning_of_period: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cash_end_of_period: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Key Sub-items for fundamental analysis
    capital_expenditure: Mapped[float] = mapped_column(Float, default=0.0)
    free_cash_flow: Mapped[float] = mapped_column(Float, default=0.0)
    dividend_paid: Mapped[float] = mapped_column(Float, default=0.0)

    raw_payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    period: Mapped["FinancialPeriod"] = relationship("FinancialPeriod", back_populates="cash_flow_statements")
