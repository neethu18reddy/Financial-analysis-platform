"""Data provenance tracking models for deep auditable lineage."""

from typing import Optional
from sqlalchemy import String, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class DataProvenance(Base, TimestampMixin):
    """Field-level provenance mapping every financial metric to its original filing source."""
    __tablename__ = "data_provenance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_document_id: Mapped[int] = mapped_column(
        ForeignKey("source_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # "income_statements", "balance_sheets", etc.
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g., "revenue_from_operations"
    
    # Original reported characteristics
    reported_label: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., "Revenue from Sale of Products & Services"
    reported_value_raw: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "89,922"
    reported_unit: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "Crores"
    reported_currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    
    # Normalized characteristics stored in target database
    normalized_value: Mapped[float] = mapped_column(Float, nullable=False)
    normalized_unit: Mapped[str] = mapped_column(String(50), default="CRORES", nullable=False)
    
    # Page and reference pointers
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    table_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    note_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g. "Note 24: Revenue from operations"
    extraction_method: Mapped[str] = mapped_column(String(100), default="STATUTORY_AUDITED_FIXTURE", nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    transformation_applied: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    source_document: Mapped["SourceDocument"] = relationship("SourceDocument", back_populates="provenance_records")
