"""Data classification and source tracking models."""

import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class DataClassification(str, enum.Enum):
    """Explicit labeling for all dataset origins."""
    REAL = "REAL"
    SYNTHETIC = "SYNTHETIC"
    MOCK = "MOCK"
    DERIVED = "DERIVED"


class SourceType(str, enum.Enum):
    """Source provider and document types."""
    NSE_FILING = "NSE_FILING"
    BSE_FILING = "BSE_FILING"
    MCA_XBRL = "MCA_XBRL"
    RBI_DBIE = "RBI_DBIE"
    ANNUAL_REPORT_PDF = "ANNUAL_REPORT_PDF"
    PRESS_RELEASE = "PRESS_RELEASE"
    AUDITED_FINANCIALS_FIXTURE = "AUDITED_FINANCIALS_FIXTURE"
    MOCK_FIXTURE = "MOCK_FIXTURE"


class SourceDocument(Base, TimestampMixin):
    """Source document record preserving provenance origins and licensing constraints."""
    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, native_enum=False),
        nullable=False,
        default=SourceType.NSE_FILING
    )
    data_classification: Mapped[DataClassification] = mapped_column(
        Enum(DataClassification, native_enum=False),
        nullable=False,
        default=DataClassification.REAL
    )
    file_path_or_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    retrieval_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    filing_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    checksum_sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    terms_and_license: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="Direct statutory filings under SEBI LODR Regulations / MCA public access."
    )
    redistribution_allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    attribution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    provenance_records: Mapped[list["DataProvenance"]] = relationship(
        "DataProvenance",
        back_populates="source_document",
        cascade="all, delete-orphan"
    )
