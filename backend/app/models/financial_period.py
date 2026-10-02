"""Financial reporting period model with explicit chronology and standard attributes."""

import enum
from datetime import date
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, Date, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class PeriodType(str, enum.Enum):
    """Reporting period frequency."""
    ANNUAL = "ANNUAL"
    QUARTERLY = "QUARTERLY"
    HALF_YEARLY = "HALF_YEARLY"
    TTM = "TTM"


class ReportingStandard(str, enum.Enum):
    """Accounting standards applied to filings."""
    IND_AS = "IND_AS"
    IGAAP = "IGAAP"
    IFRS = "IFRS"
    US_GAAP = "US_GAAP"


class FinancialUnit(str, enum.Enum):
    """Canonical reporting scale units."""
    CRORES = "CRORES"
    LAKHS = "LAKHS"
    MILLIONS = "MILLIONS"
    BILLIONS = "BILLIONS"
    UNITS = "UNITS"


class FinancialPeriod(Base, TimestampMixin):
    """Explicitly scoped financial reporting window."""
    __tablename__ = "financial_periods"
    __table_args__ = (
        UniqueConstraint("company_id", "period_type", "fiscal_year", "fiscal_quarter", name="uq_company_period"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    period_type: Mapped[PeriodType] = mapped_column(
        Enum(PeriodType, native_enum=False),
        nullable=False,
        default=PeriodType.ANNUAL
    )
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # e.g. 2024 for FY2023-24
    fiscal_quarter: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1, 2, 3, 4
    period_label: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "FY 2023-24" or "Q3 FY24"
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    filing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    reporting_standard: Mapped[ReportingStandard] = mapped_column(
        Enum(ReportingStandard, native_enum=False),
        nullable=False,
        default=ReportingStandard.IND_AS
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    canonical_unit: Mapped[FinancialUnit] = mapped_column(
        Enum(FinancialUnit, native_enum=False),
        default=FinancialUnit.CRORES,
        nullable=False
    )
    is_audited: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="financial_periods")
    income_statements: Mapped[List["IncomeStatement"]] = relationship(
        "IncomeStatement",
        back_populates="period",
        cascade="all, delete-orphan"
    )
    balance_sheets: Mapped[List["BalanceSheet"]] = relationship(
        "BalanceSheet",
        back_populates="period",
        cascade="all, delete-orphan"
    )
    cash_flow_statements: Mapped[List["CashFlowStatement"]] = relationship(
        "CashFlowStatement",
        back_populates="period",
        cascade="all, delete-orphan"
    )
