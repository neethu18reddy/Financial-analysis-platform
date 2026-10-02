"""Deterministic validation result models and audit logs."""

import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, Enum, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ValidationStatus(str, enum.Enum):
    """Validation check status."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"


class ValidationCategory(str, enum.Enum):
    """Categories of deterministic validation checks."""
    BALANCE_SHEET_RECONCILIATION = "BALANCE_SHEET_RECONCILIATION"
    CASH_FLOW_RECONCILIATION = "CASH_FLOW_RECONCILIATION"
    INCOME_STATEMENT_MATH = "INCOME_STATEMENT_MATH"
    PERIOD_CONSISTENCY = "PERIOD_CONSISTENCY"
    HISTORICAL_ORDERING = "HISTORICAL_ORDERING"
    DUPLICATE_CHECK = "DUPLICATE_CHECK"
    UNIT_AND_CURRENCY = "UNIT_AND_CURRENCY"
    CONSOLIDATED_STANDALONE_INTEGRITY = "CONSOLIDATED_STANDALONE_INTEGRITY"
    ANOMALY_DETECTION = "ANOMALY_DETECTION"


class ValidationResult(Base, TimestampMixin):
    """Immutable record of deterministic validation run."""
    __tablename__ = "validation_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # "balance_sheets", etc.
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    company_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    period_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    
    rule_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[ValidationCategory] = mapped_column(
        Enum(ValidationCategory, native_enum=False),
        nullable=False,
        index=True
    )
    status: Mapped[ValidationStatus] = mapped_column(
        Enum(ValidationStatus, native_enum=False),
        nullable=False,
        index=True
    )
    
    formula_checked: Mapped[str] = mapped_column(String(255), nullable=False)
    expected_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    discrepancy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tolerance: Mapped[float] = mapped_column(Float, default=0.001, nullable=False)
    
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    validated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
