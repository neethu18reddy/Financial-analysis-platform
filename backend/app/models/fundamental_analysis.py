"""Fundamental Analysis database models storing analytical metrics, DuPont decomposition, and methodology lineage."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, ForeignKey, Text, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class FundamentalMetricRecord(Base, TimestampMixin):
    """Immutable or computed analytical metric record with methodology version and input lineage."""
    __tablename__ = "fundamental_metric_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    period_id: Mapped[int] = mapped_column(
        ForeignKey("financial_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    statement_type: Mapped[str] = mapped_column(String(20), default="CONSOLIDATED", nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # PROFITABILITY, GROWTH, EFFICIENCY, CASH_QUALITY, DUPONT
    metric_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g., "ROCE", "ROE_5STEP", "DSO"
    metric_label: Mapped[str] = mapped_column(String(255), nullable=False)
    
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(20), default="PERCENT", nullable=False)  # PERCENT, RATIO, DAYS, MULTIPLIER, CRORES
    
    methodology_version: Mapped[str] = mapped_column(String(20), default="v1.0.0", nullable=False)
    formula_expression: Mapped[str] = mapped_column(String(500), nullable=False)
    inputs_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
