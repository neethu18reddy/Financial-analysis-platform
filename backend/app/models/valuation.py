"""Valuation Data Models and Serialization Contracts.

Defines Pydantic schemas and database/API entities for:
- FCFF & FCFE Discounted Cash Flow (DCF) Models
- Reverse DCF Market Expectation Solver
- Multi-Method Multiples & Relative Valuation
- Multi-Scenario Modeling (Bear, Base, Bull)
- 2D Sensitivity Analysis Grids
- Terminal Value Diagnostics
- Specialized Financial Institutions (DDM & Residual Income)
- Sum-of-the-Parts (SOTP) Valuation Foundation
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class ValuationMethod(str, Enum):
    """Supported Valuation Methodologies."""
    DCF_FCFF = "DCF_FCFF"
    DCF_FCFE = "DCF_FCFE"
    REVERSE_DCF = "REVERSE_DCF"
    MULTIPLES_RELATIVE = "MULTIPLES_RELATIVE"
    DDM_BANKS = "DDM_BANKS"
    RESIDUAL_INCOME = "RESIDUAL_INCOME"
    SOTP = "SOTP"


class TerminalValueMethod(str, Enum):
    """Terminal Value calculation approaches."""
    GORDON_GROWTH = "GORDON_GROWTH"
    EXIT_MULTIPLE = "EXIT_MULTIPLE"


class ScenarioType(str, Enum):
    """Explicit Scenario Classifications."""
    BEAR = "BEAR"
    BASE = "BASE"
    BULL = "BULL"
    CUSTOM = "CUSTOM"


# ---------------------------------------------------------------------------
# 1. DCF Valuation Models
# ---------------------------------------------------------------------------

class CashFlowProjectionYear(BaseModel):
    """Single-year cash flow projection breakdown."""
    year_index: int
    fiscal_year: int
    revenue: float
    revenue_growth_pct: float
    operating_profit_ebit: float
    ebit_margin_pct: float
    effective_tax_rate_pct: float
    nopat: float  # EBIT * (1 - tax)
    depreciation_amortization: float
    capital_expenditure: float
    change_in_nwc: float
    free_cash_flow: float  # FCFF or FCFE
    discount_factor: float
    discounted_fcf: float


class WACCBreakdown(BaseModel):
    """Detailed components of Weighted Average Cost of Capital."""
    risk_free_rate: float
    equity_risk_premium: float
    beta: float
    cost_of_equity: float  # Rf + Beta * ERP
    pre_tax_cost_of_debt: float
    effective_tax_rate: float
    after_tax_cost_of_debt: float  # Kd * (1 - t)
    equity_weight_pct: float  # E / (E + D)
    debt_weight_pct: float    # D / (E + D)
    wacc_pct: float
    formula_expression: str


class TerminalValueDiagnostics(BaseModel):
    """Diagnostics and sanity metrics for Terminal Value."""
    terminal_value_raw: float
    pv_terminal_value: float
    pv_explicit_cash_flows: float
    enterprise_value: float
    terminal_value_pct_of_ev: float
    implied_exit_ev_ebitda_multiple: Optional[float] = None
    implied_perpetual_growth_rate: Optional[float] = None
    is_terminal_value_dominant: bool  # True if > 75% of EV
    growth_vs_gdp_warning: bool       # True if g >= 6.5%
    warning_notes: List[str] = Field(default_factory=list)


class DCFValuationInputs(BaseModel):
    """Configurable inputs for DCF modeling."""
    forecast_years: int = Field(default=5, ge=3, le=10)
    base_revenue: Optional[float] = None
    revenue_growth_rates: Optional[List[float]] = None  # Per year or constant
    constant_revenue_growth_pct: float = 12.0
    target_ebit_margin_pct: float = 18.0
    effective_tax_rate_pct: float = 25.17
    reinvestment_rate_pct: float = 35.0  # Capex + delta NWC as % of NOPAT
    wacc_pct: Optional[float] = None     # If None, calculated from CAPM
    cost_of_equity_pct: Optional[float] = None
    risk_free_rate_pct: float = 7.10     # 10Y Indian G-Sec benchmark
    equity_risk_premium_pct: float = 6.00
    beta: float = 1.05
    pre_tax_cost_of_debt_pct: float = 8.50
    debt_to_capital_pct: float = 25.0
    terminal_value_method: TerminalValueMethod = TerminalValueMethod.GORDON_GROWTH
    terminal_growth_rate_pct: float = 5.00
    exit_ev_ebitda_multiple: float = 15.0
    shares_outstanding_crores: Optional[float] = None
    total_debt_crores: Optional[float] = None
    cash_and_investments_crores: Optional[float] = None
    minority_interest_crores: Optional[float] = 0.0


class DCFValuationResult(BaseModel):
    """Complete Output of DCF Valuation Engine."""
    company_id: int
    ticker: str
    valuation_method: ValuationMethod
    valuation_date: str
    currency: str = "INR"
    unit: str = "CRORES"
    
    inputs_applied: DCFValuationInputs
    wacc_breakdown: WACCBreakdown
    projections: List[CashFlowProjectionYear]
    
    pv_explicit_forecast: float
    terminal_value_raw: float
    pv_terminal_value: float
    enterprise_value: float
    
    # Bridge to Equity Value
    total_debt: float
    cash_and_investments: float
    net_debt: float
    minority_interest: float
    equity_value: float
    
    shares_outstanding_crores: float
    estimated_fair_value_per_share: float
    current_market_price: Optional[float] = None
    upside_downside_pct: Optional[float] = None
    
    terminal_diagnostics: TerminalValueDiagnostics
    formula_lineage: Dict[str, str]
    methodology_version: str = "v1.0.0-phase4"


# ---------------------------------------------------------------------------
# 2. Reverse DCF (Market Expectation Solver)
# ---------------------------------------------------------------------------

class ReverseDCFInputs(BaseModel):
    """Input assumptions for Reverse DCF solving."""
    current_market_price: float
    shares_outstanding_crores: Optional[float] = None
    forecast_years: int = 5
    target_ebit_margin_pct: Optional[float] = None  # If fixed, solves for growth
    wacc_pct: float = 11.5
    terminal_growth_rate_pct: float = 5.0
    effective_tax_rate_pct: float = 25.17
    reinvestment_rate_pct: float = 35.0
    net_debt_crores: Optional[float] = None


class ReverseDCFResult(BaseModel):
    """Result of solving for embedded market expectations."""
    company_id: int
    ticker: str
    current_market_price: float
    current_market_cap_crores: float
    implied_enterprise_value: float
    
    wacc_pct: float
    terminal_growth_rate_pct: float
    assumed_ebit_margin_pct: float
    
    # Solved Expectation Metric
    implied_revenue_cagr_pct: float
    implied_fcf_cagr_pct: float
    historical_revenue_cagr_3yr: Optional[float] = None
    growth_premium_vs_historical_pct: Optional[float] = None
    
    implied_5yr_revenue_target: float
    implied_5yr_fcf_target: float
    
    plausibility_assessment: str  # "CONSERVATIVE", "REALISTIC", "AGGRESSIVE", "EXTREME"
    plausibility_reasoning: str
    
    sensitivities: List[Dict[str, Any]] = Field(default_factory=list)
    methodology_version: str = "v1.0.0-phase4"


# ---------------------------------------------------------------------------
# 3. Relative Multiples Valuation
# ---------------------------------------------------------------------------

class MultipleMetricComparison(BaseModel):
    """Single valuation multiple analysis (e.g. P/E, EV/EBITDA)."""
    multiple_name: str  # "P/E", "EV/EBITDA", "P/B", "EV/Sales", "P/S"
    current_multiple: Optional[float] = None
    historical_1yr_median: Optional[float] = None
    historical_3yr_median: Optional[float] = None
    historical_5yr_median: Optional[float] = None
    historical_min: Optional[float] = None
    historical_max: Optional[float] = None
    peer_benchmark_median: Optional[float] = None
    
    underlying_financial_metric: float  # EPS, EBITDA, Book Value, etc.
    target_multiple_applied: float
    implied_fair_value_per_share: float
    upside_downside_pct: Optional[float] = None
    limitations: str


class MultiplesValuationResult(BaseModel):
    """Complete Multi-Metric Relative Valuation Suite."""
    company_id: int
    ticker: str
    current_market_price: float
    multiples: List[MultipleMetricComparison]
    composite_median_fair_value: float
    composite_upside_downside_pct: Optional[float] = None
    methodology_notes: List[str]
    methodology_version: str = "v1.0.0-phase4"


# ---------------------------------------------------------------------------
# 4. Multi-Scenario Analysis (Bear, Base, Bull)
# ---------------------------------------------------------------------------

class ScenarioCase(BaseModel):
    """Single valuation scenario configuration and outcome."""
    scenario_type: ScenarioType
    probability_weight_pct: float  # e.g., 25% Bear, 50% Base, 25% Bull
    revenue_growth_pct: float
    ebit_margin_pct: float
    wacc_pct: float
    terminal_growth_pct: float
    estimated_fair_value_per_share: float
    upside_downside_pct: Optional[float] = None
    key_assumptions: List[str]


class ScenarioAnalysisResult(BaseModel):
    """Synthesis of Bear, Base, and Bull Scenarios."""
    company_id: int
    ticker: str
    current_market_price: float
    scenarios: List[ScenarioCase]
    probability_weighted_fair_value: float
    expected_upside_downside_pct: float
    risk_reward_skew: str  # "FAVORABLE", "SYMMETRIC", "UNFAVORABLE"
    methodology_version: str = "v1.0.0-phase4"


# ---------------------------------------------------------------------------
# 5. 2D Sensitivity Matrix
# ---------------------------------------------------------------------------

class SensitivityCell(BaseModel):
    """Single cell in 2D sensitivity matrix."""
    row_value: float
    col_value: float
    fair_value_per_share: float
    upside_downside_pct: Optional[float] = None


class SensitivityMatrixResult(BaseModel):
    """2D valuation sensitivity table."""
    matrix_name: str
    row_parameter_name: str
    row_parameter_unit: str
    col_parameter_name: str
    col_parameter_unit: str
    row_values: List[float]
    col_values: List[float]
    grid: List[List[SensitivityCell]]
    base_row_value: float
    base_col_value: float
    base_fair_value: float


# ---------------------------------------------------------------------------
# 6. Specialized Financial Institutions Valuation (DDM & Residual Income)
# ---------------------------------------------------------------------------

class BankDDMYear(BaseModel):
    """Single year bank Dividend Discount Model projection."""
    year_index: int
    fiscal_year: int
    total_assets: float
    loan_growth_pct: float
    net_worth: float
    return_on_equity_pct: float
    net_profit_pat: float
    tier1_capital_retention_pct: float
    dividend_payout_pct: float
    dividends_paid: float
    discount_factor: float
    discounted_dividend: float


class BankValuationResult(BaseModel):
    """Specialized Bank / NBFC Valuation Result."""
    company_id: int
    ticker: str
    sector: str
    valuation_method: ValuationMethod
    is_financial_institution: bool
    
    current_book_value_per_share: float
    current_roe_pct: float
    cost_of_equity_pct: float
    sustainable_growth_rate_pct: float
    
    # Multi-stage DDM
    projections: List[BankDDMYear]
    pv_explicit_dividends: float
    terminal_value_dividends: float
    pv_terminal_value: float
    ddm_fair_value_per_share: float
    
    # Justified Price-to-Book (Gordon P/B)
    justified_pb_multiple: float  # (ROE - g) / (Ke - g)
    justified_pb_fair_value_per_share: float
    
    current_market_price: Optional[float] = None
    upside_downside_pct: Optional[float] = None
    
    methodology_notes: List[str]
    limitations: str
    methodology_version: str = "v1.0.0-phase4"


# ---------------------------------------------------------------------------
# 7. Sum-of-the-Parts (SOTP) Foundation
# ---------------------------------------------------------------------------

class SOTPSegment(BaseModel):
    """Individual business segment for SOTP valuation."""
    segment_name: str
    segment_description: str
    revenue: float
    ebitda: float
    benchmark_ev_ebitda_multiple: float
    implied_enterprise_value: float
    ownership_stake_pct: float = 100.0
    effective_enterprise_value: float


class SOTPValuationResult(BaseModel):
    """SOTP Multi-Segment Valuation Result."""
    company_id: int
    ticker: str
    segments: List[SOTPSegment]
    gross_enterprise_value: float
    holding_company_discount_pct: float = 15.0
    net_enterprise_value: float
    net_debt: float
    equity_value: float
    shares_outstanding_crores: float
    fair_value_per_share: float
    current_market_price: Optional[float] = None
    upside_downside_pct: Optional[float] = None
    methodology_version: str = "v1.0.0-phase4"


# ---------------------------------------------------------------------------
# 8. Composite Valuation Suite Summary
# ---------------------------------------------------------------------------

class ValuationSummaryResponse(BaseModel):
    """Unified Valuation Dashboard Response."""
    company_id: int
    ticker: str
    legal_name: str
    sector: str
    is_financial_institution: bool
    current_market_price: float
    shares_outstanding_crores: float
    market_cap_crores: float
    
    dcf_result: Optional[DCFValuationResult] = None
    reverse_dcf_result: Optional[ReverseDCFResult] = None
    multiples_result: Optional[MultiplesValuationResult] = None
    scenario_result: Optional[ScenarioAnalysisResult] = None
    bank_valuation_result: Optional[BankValuationResult] = None
    
    composite_fair_value_range_low: float
    composite_fair_value_range_high: float
    composite_central_fair_value: float
    composite_upside_downside_pct: float
    
    valuation_summary_text: str
    methodology_version: str = "v1.0.0-phase4"
