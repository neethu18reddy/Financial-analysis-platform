"""Corporate actions and share count historical adjustments."""

import enum
from datetime import date
from typing import Optional
from sqlalchemy import String, Float, Integer, Date, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ActionType(str, enum.Enum):
    """Types of corporate capital adjustments."""
    STOCK_SPLIT = "STOCK_SPLIT"
    BONUS_ISSUE = "BONUS_ISSUE"
    DIVIDEND = "DIVIDEND"
    RIGHTS_ISSUE = "RIGHTS_ISSUE"
    BUYBACK = "BUYBACK"
    FACE_VALUE_CHANGE = "FACE_VALUE_CHANGE"


class CorporateAction(Base, TimestampMixin):
    """Historical corporate action events impacting per-share comparability."""
    __tablename__ = "corporate_actions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    action_type: Mapped[ActionType] = mapped_column(
        Enum(ActionType, native_enum=False),
        nullable=False
    )
    ex_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    record_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    ratio_numerator: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # e.g., 2 in 2:1 bonus
    ratio_denominator: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # e.g., 1 in 2:1 bonus
    adjustment_factor: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # Multiplier for historical per-share metrics
    dividend_per_share: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # INR per share
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="corporate_actions")


class ShareCountHistory(Base, TimestampMixin):
    """Historical total outstanding share counts for precise weighted-average and per-share calculations."""
    __tablename__ = "share_count_histories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    total_shares_outstanding: Mapped[float] = mapped_column(Float, nullable=False)  # Raw share count
    face_value_inr: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    paid_up_capital_inr: Mapped[float] = mapped_column(Float, nullable=False)
    treasury_shares: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    promoter_holding_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    public_holding_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
