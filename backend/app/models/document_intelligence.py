"""Document Intelligence and Annual Report RAG Data Models.

Defines SQLAlchemy ORM tables and Pydantic validation contracts for:
- Document Metadata & Ingestion Identity (SHA-256, page counts, filing metadata)
- Document Pages (Raw extracted text, page numbers, section headers)
- Financial Semantic Chunks (Token counts, section context, embeddings, character offsets)
- Verifiable Evidence Citations (Exact quote, page, section, source URL, relevance score)
- Retrieval Queries and Responses
"""

import enum
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import String, Integer, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, Field

from app.db.base import Base, TimestampMixin


class DocumentType(str, enum.Enum):
    """Statutory and investor corporate document types."""
    ANNUAL_REPORT = "ANNUAL_REPORT"
    EARNINGS_CALL_TRANSCRIPT = "EARNINGS_CALL_TRANSCRIPT"
    INVESTOR_PRESENTATION = "INVESTOR_PRESENTATION"
    AUDITOR_REPORT = "AUDITOR_REPORT"
    REGULATORY_FILING = "REGULATORY_FILING"


class DocumentProcessingStatus(str, enum.Enum):
    """Document ingestion pipeline processing states."""
    PENDING = "PENDING"
    PARSING = "PARSING"
    CHUNKING = "CHUNKING"
    INDEXING = "INDEXING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ---------------------------------------------------------------------------
# SQLAlchemy ORM Models
# ---------------------------------------------------------------------------

class DocumentRecord(Base, TimestampMixin):
    """Primary registry table for uploaded or ingested financial documents."""
    __tablename__ = "document_records"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    fiscal_year: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(SQLEnum(DocumentType, native_enum=False), default=DocumentType.ANNUAL_REPORT, nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_hash_sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    
    page_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    extraction_method: Mapped[str] = mapped_column(String(50), default="PYPDF_STRUCTURED", nullable=False)
    processing_status: Mapped[DocumentProcessingStatus] = mapped_column(SQLEnum(DocumentProcessingStatus, native_enum=False), default=DocumentProcessingStatus.PENDING, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    retrieval_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    pages: Mapped[List["DocumentPageRecord"]] = relationship("DocumentPageRecord", back_populates="document", cascade="all, delete-orphan", order_by="DocumentPageRecord.page_number.asc()")
    chunks: Mapped[List["DocumentChunkRecord"]] = relationship("DocumentChunkRecord", back_populates="document", cascade="all, delete-orphan", order_by="DocumentChunkRecord.chunk_index.asc()")


class DocumentPageRecord(Base, TimestampMixin):
    """Extracted text per physical page of a document."""
    __tablename__ = "document_page_records"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("document_records.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # 1-indexed
    
    detected_section: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    cleaned_text: Mapped[str] = mapped_column(Text, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    has_tables: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    document: Mapped["DocumentRecord"] = relationship("DocumentRecord", back_populates="pages")
    chunks: Mapped[List["DocumentChunkRecord"]] = relationship("DocumentChunkRecord", back_populates="page", cascade="all, delete-orphan")


class DocumentChunkRecord(Base, TimestampMixin):
    """Semantic chunk prepared for embedding and vector similarity retrieval."""
    __tablename__ = "document_chunk_records"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("document_records.id", ondelete="CASCADE"), nullable=False, index=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("document_page_records.id", ondelete="CASCADE"), nullable=False, index=True)
    
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    section_title: Mapped[str] = mapped_column(String(100), default="GENERAL_DISCLOSURE", nullable=False, index=True)
    
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON serialization of vector
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    document: Mapped["DocumentRecord"] = relationship("DocumentRecord", back_populates="chunks")
    page: Mapped["DocumentPageRecord"] = relationship("DocumentPageRecord", back_populates="chunks")


# ---------------------------------------------------------------------------
# Pydantic Schemas & Contracts
# ---------------------------------------------------------------------------

class DocumentPageDTO(BaseModel):
    """DTO for viewing a single page."""
    page_number: int
    detected_section: Optional[str] = None
    char_count: int
    has_tables: bool
    text: str


class DocumentMetadataDTO(BaseModel):
    """DTO for document library listing."""
    id: int
    ticker: str
    fiscal_year: int
    document_type: DocumentType
    title: str
    file_name: str
    source_url: Optional[str] = None
    file_hash_sha256: str
    page_count: int
    file_size_bytes: int
    extraction_method: str
    processing_status: DocumentProcessingStatus
    error_message: Optional[str] = None
    retrieval_date: str
    total_chunks: int = 0


class DocumentDetailDTO(DocumentMetadataDTO):
    """Detailed document DTO including available sections and pages."""
    sections_detected: List[str] = Field(default_factory=list)
    pages: List[DocumentPageDTO] = Field(default_factory=list)


class EvidenceCitation(BaseModel):
    """Verifiable page-level citation for an analytical statement."""
    document_id: int
    document_title: str
    ticker: str
    fiscal_year: int
    page_number: int
    section_title: str
    exact_quote: str
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    relevance_score: float = Field(ge=0.0, le=1.0)
    source_url: Optional[str] = None
    provenance_hash: str


class DocumentRetrievalQuery(BaseModel):
    """Structured query for vector and hybrid search across annual reports."""
    query_text: str = Field(min_length=2, description="Natural language search query")
    ticker: Optional[str] = Field(None, description="Filter by company ticker")
    fiscal_year: Optional[int] = Field(None, description="Filter by fiscal year")
    section: Optional[str] = Field(None, description="Filter by section, e.g. MD&A, AUDITOR_REPORT")
    document_type: Optional[DocumentType] = None
    top_k: int = Field(default=5, ge=1, le=20)
    min_relevance_score: float = Field(default=0.25, ge=0.0, le=1.0)


class DocumentRetrievalResult(BaseModel):
    """Single retrieved chunk with citation metadata."""
    chunk_id: int
    document_id: int
    document_title: str
    ticker: str
    fiscal_year: int
    page_number: int
    section_title: str
    chunk_text: str
    relevance_score: float
    citation: EvidenceCitation


class DocumentRetrievalResponse(BaseModel):
    """Complete retrieval response."""
    query_text: str
    filters_applied: Dict[str, Any]
    total_matches: int
    results: List[DocumentRetrievalResult]
    retrieval_latency_ms: float
    embedding_model: str
    methodology_version: str = "v1.0.0-phase6"


class IngestionUploadResponse(BaseModel):
    """Response when a document is uploaded and processed."""
    document_id: int
    ticker: str
    fiscal_year: int
    file_name: str
    file_hash_sha256: str
    page_count: int
    total_chunks_indexed: int
    sections_detected: List[str]
    processing_status: DocumentProcessingStatus
    message: str
