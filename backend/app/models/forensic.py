"""Forensic Intelligence Data Models and Serialization Contracts."""

from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class ForensicRiskLevel(str, Enum):
    """Standardized Forensic Risk Classification."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    INFO = "INFO"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class SignalCategory(str, Enum):
    """Categories for forensic screening signals."""
    MANIPULATION_RISK = "MANIPULATION_RISK"
    FINANCIAL_HEALTH = "FINANCIAL_HEALTH"
    BANKRUPTCY_RISK = "BANKRUPTCY_RISK"
    ACCRUAL_QUALITY = "ACCRUAL_QUALITY"
    WORKING_CAPITAL = "WORKING_CAPITAL"
    REVENUE_RECOGNITION = "REVENUE_RECOGNITION"
    DEBT_SOLVENCY = "DEBT_SOLVENCY"
    MARGIN_ANOMALY = "MARGIN_ANOMALY"
    AUDIT_GOVERNANCE = "AUDIT_GOVERNANCE"


class ForensicSignal(BaseModel):
    """Granular forensic screening indicator."""
    signal_key: str
    signal_label: str
    category: SignalCategory
    risk_level: ForensicRiskLevel
    value: Optional[float] = None
    formatted_value: str
    benchmark_threshold: str
    formula_expression: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    interpretation: str
    is_applicable: bool = True
    inapplicable_reason: Optional[str] = None
    limitations: str
    methodology_version: str = "v1.0.0"


class BeneishVariable(BaseModel):
    """Single variable component of Beneish M-Score."""
    key: str
    name: str
    value: Optional[float] = None
    coefficient: float
    contribution: Optional[float] = None
    formula: str
    interpretation: str


class BeneishMScoreResult(BaseModel):
    """Beneish 8-Variable M-Score Model Output."""
    period_id: int
    period_label: str
    fiscal_year: int
    m_score: Optional[float] = None
    risk_classification: ForensicRiskLevel
    is_applicable: bool = True
    inapplicable_reason: Optional[str] = None
    threshold: float = -1.78
    probability_of_manipulation_flag: str
    variables: Dict[str, BeneishVariable]
    formula_expression: str = (
        "-4.84 + 0.920*DSRI + 0.528*GMI + 0.404*AQI + 0.892*SGI + "
        "0.115*DEPI - 0.172*SGAI + 4.037*TATA + 0.0327*LVGI"
    )
    interpretation: str
    limitations: str
    methodology_version: str = "v1.0.0"


class PiotroskiSignal(BaseModel):
    """Individual binary test for Piotroski F-Score."""
    key: str
    category: str  # Profitability, Leverage, Operating Efficiency
    name: str
    passed: bool
    score: int  # 0 or 1
    description: str
    formula: str
    inputs: Dict[str, Any] = Field(default_factory=dict)


class PiotroskiFScoreResult(BaseModel):
    """Piotroski 9-Point F-Score Model Output."""
    period_id: int
    period_label: str
    fiscal_year: int
    f_score: int  # 0 to 9
    max_score: int = 9
    risk_classification: ForensicRiskLevel
    financial_health_label: str  # Strong (8-9), Moderate (5-7), Weak (0-4)
    profitability_score: int
    leverage_liquidity_score: int
    operating_efficiency_score: int
    signals: List[PiotroskiSignal]
    is_applicable: bool = True
    inapplicable_reason: Optional[str] = None
    interpretation: str
    limitations: str
    methodology_version: str = "v1.0.0"


class AltmanZScoreResult(BaseModel):
    """Altman Z-Score / Emerging Market Z''-Score Model Output."""
    period_id: int
    period_label: str
    fiscal_year: int
    model_type: str  # "Emerging_Market_Z_Double_Prime" or "Original_Z_Score"
    z_score: Optional[float] = None
    zone: str  # "Safe Zone", "Grey Zone", "Distress Zone"
    risk_classification: ForensicRiskLevel
    safe_threshold: float
    distress_threshold: float
    components: Dict[str, float]
    formula_expression: str
    is_applicable: bool = True
    inapplicable_reason: Optional[str] = None
    interpretation: str
    limitations: str
    methodology_version: str = "v1.0.0"


class PeriodForensicScorecard(BaseModel):
    """Complete forensic intelligence scorecard for a financial period."""
    period_id: int
    period_label: str
    fiscal_year: int
    end_date: str
    statement_type: str
    overall_risk_level: ForensicRiskLevel
    risk_summary_text: str
    beneish_m_score: Optional[BeneishMScoreResult] = None
    piotroski_f_score: Optional[PiotroskiFScoreResult] = None
    altman_z_score: Optional[AltmanZScoreResult] = None
    screening_signals: List[ForensicSignal] = Field(default_factory=list)
    anomalous_signals_count: int = 0
    total_signals_evaluated: int = 0


class CompanyForensicResponse(BaseModel):
    """Company-level multi-period forensic intelligence payload."""
    company_id: int
    ticker: str
    legal_name: str
    sector: str
    industry: str
    statement_type: str
    overall_forensic_stance: str
    latest_scorecard: Optional[PeriodForensicScorecard] = None
    historical_scorecards: List[PeriodForensicScorecard] = Field(default_factory=list)
    sector_applicability_notes: List[str] = Field(default_factory=list)
    methodology_version: str = "v1.0.0"
