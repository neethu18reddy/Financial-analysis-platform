"""Company and Security models for Indian listed equities."""

from typing import Optional, List
from sqlalchemy import String, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Company(Base, TimestampMixin):
    """Normalized Indian company entity."""
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cin: Mapped[str] = mapped_column(String(21), unique=True, index=True, nullable=False)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    trade_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sector: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    industry: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    isin: Mapped[str] = mapped_column(String(12), unique=True, index=True, nullable=False)
    primary_exchange: Mapped[str] = mapped_column(String(10), default="NSE", nullable=False)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    registered_state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    securities: Mapped[List["Security"]] = relationship(
        "Security",
        back_populates="company",
        cascade="all, delete-orphan"
    )
    financial_periods: Mapped[List["FinancialPeriod"]] = relationship(
        "FinancialPeriod",
        back_populates="company",
        cascade="all, delete-orphan",
        order_by="FinancialPeriod.end_date.desc()"
    )
    corporate_actions: Mapped[List["CorporateAction"]] = relationship(
        "CorporateAction",
        back_populates="company",
        cascade="all, delete-orphan",
        order_by="CorporateAction.ex_date.desc()"
    )


class Security(Base, TimestampMixin):
    """Traded security details mapped to an exchange listing."""
    __tablename__ = "securities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    series: Mapped[str] = mapped_column(String(10), default="EQ", nullable=False)
    isin: Mapped[str] = mapped_column(String(12), nullable=False)
    exchange: Mapped[str] = mapped_column(String(10), default="NSE", nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    lot_size: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="securities")
