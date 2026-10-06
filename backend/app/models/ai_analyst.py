"""Data Models and Contracts for Phase 7 AI Analyst, Historical Validation, and Research Product.

Defines schemas and ORM tables for:
- AI Query and Cited Analyst Responses
- Question Intent Classification
- Verifiable Analytical Claims and Grounding Check Status
- Management 'Said vs Did' Historical Commitments vs Outturns
- Point-in-Time (PIT) As-Of Date Simulators (Zero-Leakage)
- Watchlist Items & Metric Anomaly Alert Triggers
- Institutional Comprehensive Research Reports
"""

import enum
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy import String, Integer, Text, Float, Boolean, DateTime, Date, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, Field

try:
    from app.db.base import Base, TimestampMixin
    from app.models.document_intelligence import EvidenceCitation
except ImportError:
    from backend.app.db.base import Base, TimestampMixin
    from backend.app.models.document_intelligence import EvidenceCitation


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class QuestionIntent(str, enum.Enum):
    """Classified analytical intent of user financial inquiries."""
    FINANCIAL_PERFORMANCE = "FINANCIAL_PERFORMANCE"
    PROFITABILITY_ROCE = "PROFITABILITY_ROCE"
    WORKING_CAPITAL_CASH_FLOW = "WORKING_CAPITAL_CASH_FLOW"
    FORENSIC_INTEGRITY = "FORENSIC_INTEGRITY"
    VALUATION_DRIVERS = "VALUATION_DRIVERS"
    MANAGEMENT_COMMENTARY = "MANAGEMENT_COMMENTARY"
    SAID_VS_DID = "SAID_VS_DID"
    RISK_GOVERNANCE = "RISK_GOVERNANCE"
    GENERAL_RESEARCH = "GENERAL_RESEARCH"


class ClaimGroundingStatus(str, enum.Enum):
    """Grounding verification state for an analytical assertion."""
    VERIFIED_DATA = "VERIFIED_DATA"          # Proven directly by audited financial figures
    VERIFIED_CITATION = "VERIFIED_CITATION"  # Proven by verbatim filing text quote
    SCREENING_SIGNAL = "SCREENING_SIGNAL"    # Statistical indicator, not factual assertion
    UNSUPPORTED_REJECTED = "UNSUPPORTED_REJECTED" # AI claim rejected for lack of source evidence


class GuidanceCategory(str, enum.Enum):
    """Categories of management forward guidance."""
    CAPEX_EXPANSION = "CAPEX_EXPANSION"
    REVENUE_GROWTH = "REVENUE_GROWTH"
    MARGIN_TARGET = "MARGIN_TARGET"
    DELEVERAGING = "DELEVERAGING"
    PRODUCT_LAUNCH = "PRODUCT_LAUNCH"
    DIVIDEND_PAYOUT = "DIVIDEND_PAYOUT"


class DeliveryStatus(str, enum.Enum):
    """Outturn status of management guidance."""
    MET = "MET"
    EXCEEDED = "EXCEEDED"
    MISSED = "MISSED"
    IN_PROGRESS = "IN_PROGRESS"
    UNVERIFIABLE = "UNVERIFIABLE"


class WatchlistAlertSeverity(str, enum.Enum):
    """Severity classification for watchlist metric alerts."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# ---------------------------------------------------------------------------
# SQLAlchemy ORM Models
# ---------------------------------------------------------------------------

class WatchlistRecord(Base, TimestampMixin):
    """User monitored stock watchlist with custom tracking flags."""
    __tablename__ = "watchlist_records"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sector: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ManagementGuidanceRecord(Base, TimestampMixin):
    """Tracked management forward-looking statement for 'Said vs Did' verification."""
    __tablename__ = "management_guidance_records"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    source_fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)
    source_document_title: Mapped[str] = mapped_column(String(255), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    category: Mapped[GuidanceCategory] = mapped_column(SQLEnum(GuidanceCategory, native_enum=False), nullable=False)
    verbatim_quote: Mapped[str] = mapped_column(Text, nullable=False)
    stated_commitment: Mapped[str] = mapped_column(Text, nullable=False)
    target_timeline: Mapped[str] = mapped_column(String(100), nullable=False)
    
    evaluation_fiscal_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    actual_outturn: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivery_status: Mapped[DeliveryStatus] = mapped_column(SQLEnum(DeliveryStatus, native_enum=False), default=DeliveryStatus.IN_PROGRESS, nullable=False)
    variance_commentary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


# ---------------------------------------------------------------------------
# Pydantic Schemas & DTOs
# ---------------------------------------------------------------------------

class AnalyticalClaim(BaseModel):
    """Discrete factual or inferential claim made by the AI Analyst."""
    claim_id: str
    claim_text: str
    grounding_status: ClaimGroundingStatus
    supporting_metric_names: List[str] = Field(default_factory=list)
    supporting_values: Dict[str, Any] = Field(default_factory=dict)
    citation: Optional[EvidenceCitation] = None
    verification_notes: str


class AIAnalystQuery(BaseModel):
    """Natural language query submitted by equity research analyst."""
    ticker: str = Field(..., description="Target company ticker (e.g., RELIANCE, TCS, HDFCBANK)")
    question: str = Field(..., min_length=3, description="Financial or forensic inquiry")
    as_of_fiscal_year: Optional[int] = Field(None, description="Optional PIT historical simulation boundary")
    include_annual_report_rag: bool = Field(default=True, description="Whether to retrieve and cite annual report chunks")


class AIAnalystResponse(BaseModel):
    """Institutional cited response produced by the AI Analyst pipeline."""
    ticker: str
    company_name: str
    classified_intent: QuestionIntent
    executive_summary: str
    detailed_analysis: str
    key_claims: List[AnalyticalClaim] = Field(default_factory=list)
    supporting_citations: List[EvidenceCitation] = Field(default_factory=list)
    unsupported_claims_rejected_count: int = 0
    forensic_screening_caveats: List[str] = Field(default_factory=list)
    methodology_version: str = "v1.0.0-phase7"
    response_latency_ms: float
    confidence_score: float = Field(ge=0.0, le=1.0)


class ManagementSaidVsDidItem(BaseModel):
    """DTO for evaluating a single management forward-looking commitment."""
    id: int
    ticker: str
    source_fiscal_year: int
    source_document_title: str
    page_number: int
    category: GuidanceCategory
    verbatim_quote: str
    stated_commitment: str
    target_timeline: str
    evaluation_fiscal_year: Optional[int] = None
    actual_outturn: Optional[str] = None
    delivery_status: DeliveryStatus
    variance_commentary: Optional[str] = None


class ManagementSaidVsDidResponse(BaseModel):
    """Aggregated Said vs Did score for a company."""
    ticker: str
    company_name: str
    total_commitments: int
    met_count: int
    exceeded_count: int
    missed_count: int
    in_progress_count: int
    credibility_score_pct: float
    items: List[ManagementSaidVsDidItem]


class PointInTimeAnalysisRequest(BaseModel):
    """Request for historical financial analysis with strict temporal boundaries."""
    ticker: str
    as_of_year: int = Field(ge=2015, le=2025, description="Cutoff fiscal year")
    custom_question: Optional[str] = None


class PointInTimeAnalysisResponse(BaseModel):
    """Response strictly bounded by historical cut-off date with future leakage prevention."""
    ticker: str
    as_of_year: int
    available_fiscal_years: List[int]
    financial_summary: Dict[str, Any]
    forensic_scores: Dict[str, Any]
    valuation_at_date: Dict[str, Any]
    future_data_excluded: List[int]
    leakage_guard_passed: bool = True
    commentary: str


class WatchlistAlert(BaseModel):
    """Triggered anomaly alert for a monitored company."""
    ticker: str
    metric_name: str
    current_value: Any
    previous_value: Any
    variance_pct: Optional[float] = None
    severity: WatchlistAlertSeverity
    message: str
    triggered_at: str


class WatchlistItemDTO(BaseModel):
    """DTO for watchlist management."""
    id: int
    ticker: str
    company_name: str
    sector: str
    notes: Optional[str] = None
    is_active: bool
    latest_pe: Optional[float] = None
    latest_roce_pct: Optional[float] = None
    forensic_status: Optional[str] = None
    active_alerts: List[WatchlistAlert] = Field(default_factory=list)


class CompanyResearchReport(BaseModel):
    """Full institutional company research report spanning all analytical dimensions."""
    ticker: str
    legal_name: str
    sector: str
    industry: str
    current_market_price: float
    generated_at: str
    methodology_version: str = "v1.0.0-phase7"
    
    # Report Sections
    executive_summary: str
    business_overview: str
    financial_performance: Dict[str, Any]
    profitability_analysis: Dict[str, Any]
    growth_analysis: Dict[str, Any]
    cash_flow_quality: Dict[str, Any]
    working_capital_dynamics: Dict[str, Any]
    dupont_decomposition: Dict[str, Any]
    forensic_scoreboard: Dict[str, Any]
    valuation_synthesis: Dict[str, Any]
    business_quality_and_risks: Dict[str, Any]
    management_said_vs_did: Dict[str, Any]
    annual_report_evidence: List[EvidenceCitation]
    research_caveats_and_uncertainty: List[str]
