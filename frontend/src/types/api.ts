export interface DatabaseHealth {
  status: string;
  dialect: string;
  connected: boolean;
  error?: string | null;
}

export interface HealthResponse {
  status: string;
  project_name: string;
  version: string;
  environment: string;
  timestamp: string;
  database: DatabaseHealth;
  system_info: {
    python_version: string;
    os: string;
    os_release: string;
    debug: boolean;
  };
}

export interface Security {
  id: number;
  symbol: string;
  series: string;
  isin: string;
  exchange: string;
  currency: string;
  lot_size: number;
  is_suspended: boolean;
}

export interface Company {
  id: number;
  cin: string;
  ticker: string;
  legal_name: string;
  trade_name?: string | null;
  sector: string;
  industry: string;
  isin: string;
  primary_exchange: string;
  founded_year?: number | null;
  registered_state?: string | null;
  description?: string | null;
  website?: string | null;
  is_active: boolean;
}

export interface CompanyDetail extends Company {
  securities: Security[];
}

export interface FinancialPeriod {
  id: number;
  company_id: number;
  period_type: 'ANNUAL' | 'QUARTERLY' | 'HALF_YEARLY' | 'TTM';
  fiscal_year: number;
  fiscal_quarter?: number | null;
  period_label: string;
  start_date: string;
  end_date: string;
  filing_date?: string | null;
  reporting_standard: 'IND_AS' | 'IGAAP' | 'IFRS' | 'US_GAAP';
  currency: string;
  canonical_unit: 'CRORES' | 'LAKHS' | 'MILLIONS' | 'BILLIONS' | 'UNITS';
  is_audited: boolean;
}

export interface IncomeStatement {
  id: number;
  period_id: number;
  statement_type: 'CONSOLIDATED' | 'STANDALONE';
  revenue_from_operations: number;
  other_income: number;
  total_revenue: number;
  cost_of_materials_consumed: number;
  purchases_of_stock_in_trade: number;
  changes_in_inventories: number;
  employee_benefit_expenses: number;
  finance_costs: number;
  depreciation_and_amortization: number;
  other_expenses: number;
  total_expenses: number;
  operating_profit: number;
  profit_before_exceptional_items_and_tax: number;
  exceptional_items: number;
  profit_before_tax: number;
  current_tax: number;
  deferred_tax: number;
  total_tax_expense: number;
  profit_after_tax: number;
  minority_interest: number;
  share_of_profit_associates: number;
  net_profit_attributable_to_owners: number;
  basic_eps?: number | null;
  diluted_eps?: number | null;
}

export interface BalanceSheet {
  id: number;
  period_id: number;
  statement_type: 'CONSOLIDATED' | 'STANDALONE';
  property_plant_equipment: number;
  capital_work_in_progress: number;
  goodwill_and_intangibles: number;
  non_current_investments: number;
  deferred_tax_assets: number;
  other_non_current_assets: number;
  total_non_current_assets: number;
  inventories: number;
  trade_receivables: number;
  cash_and_cash_equivalents: number;
  bank_balances_other: number;
  short_term_loans_and_advances: number;
  other_current_assets: number;
  total_current_assets: number;
  total_assets: number;
  equity_share_capital: number;
  other_equity_and_reserves: number;
  non_controlling_interests: number;
  total_equity: number;
  non_current_borrowings: number;
  deferred_tax_liabilities: number;
  other_non_current_liabilities: number;
  total_non_current_liabilities: number;
  current_borrowings: number;
  trade_payables: number;
  other_current_liabilities: number;
  short_term_provisions: number;
  total_current_liabilities: number;
  total_liabilities: number;
  total_equity_and_liabilities: number;
}

export interface CashFlowStatement {
  id: number;
  period_id: number;
  statement_type: 'CONSOLIDATED' | 'STANDALONE';
  cash_from_operating_activities: number;
  cash_from_investing_activities: number;
  cash_from_financing_activities: number;
  net_increase_in_cash: number;
  foreign_exchange_effect: number;
  cash_beginning_of_period: number;
  cash_end_of_period: number;
  capital_expenditure: number;
  free_cash_flow: number;
  dividend_paid: number;
}

export interface MultiPeriodFinancialSet {
  period: FinancialPeriod;
  income_statement?: IncomeStatement | null;
  balance_sheet?: BalanceSheet | null;
  cash_flow?: CashFlowStatement | null;
  validation_status: 'PASSED' | 'FAILED' | 'WARNING';
  validation_passed_count: number;
  validation_failed_count: number;
}

export interface CompanyStatementsResponse {
  company: Company;
  statement_type: 'CONSOLIDATED' | 'STANDALONE';
  display_unit: string;
  periods_data: MultiPeriodFinancialSet[];
}

export interface SourceDocument {
  id: number;
  document_name: string;
  provider: string;
  source_type: string;
  data_classification: 'REAL' | 'SYNTHETIC' | 'MOCK' | 'DERIVED';
  file_path_or_url?: string | null;
  retrieval_date: string;
  filing_date?: string | null;
  terms_and_license: string;
  redistribution_allowed: boolean;
  attribution_notes?: string | null;
}

export interface DataProvenance {
  id: number;
  source_document_id: number;
  entity_type: string;
  entity_id: number;
  field_name: string;
  reported_label: string;
  reported_value_raw: string;
  reported_unit: string;
  reported_currency: string;
  normalized_value: number;
  normalized_unit: string;
  page_number?: number | null;
  table_reference?: string | null;
  note_reference?: string | null;
  extraction_method: string;
  confidence_score: number;
  transformation_applied?: string | null;
  source_document?: SourceDocument | null;
}

export interface ValidationResult {
  id: number;
  entity_type: string;
  entity_id: number;
  company_id?: number | null;
  period_id?: number | null;
  rule_name: string;
  category: string;
  status: 'PASSED' | 'FAILED' | 'WARNING';
  formula_checked: string;
  expected_value?: number | null;
  actual_value?: number | null;
  discrepancy?: number | null;
  tolerance: number;
  message: string;
  validated_at: string;
}

export interface ValidationAuditReport {
  total_checks: number;
  passed_checks: number;
  failed_checks: number;
  warning_checks: number;
  is_fully_reconciled: boolean;
  results: ValidationResult[];
}

export interface CorporateAction {
  id: number;
  company_id: number;
  action_type: string;
  ex_date: string;
  record_date?: string | null;
  ratio_numerator?: number | null;
  ratio_denominator?: number | null;
  adjustment_factor: number;
  dividend_per_share?: number | null;
  notes?: string | null;
}

export interface SourceProviderMetadata {
  provider_id: string;
  provider_name: string;
  source_type: string;
  access_method: string;
  terms_and_license: string;
  storage_restrictions: string;
  redistribution_restrictions: string;
  attribution_requirements: string;
  rate_limits: string;
  primary_url: string;
  supported_classifications: string[];
}

export interface CalculatedMetric {
  metric_key: string;
  metric_label: string;
  value?: number | null;
  formatted_value: string;
  unit: string;
  methodology_version: string;
  formula_expression: string;
  inputs: Record<string, any>;
  is_valid: boolean;
  notes?: string | null;
}

export interface MultiPeriodCAGRSummary {
  num_years: number;
  base_period_label: string;
  latest_period_label: string;
  revenue_cagr?: number | null;
  ebitda_cagr?: number | null;
  ebit_cagr?: number | null;
  pat_cagr?: number | null;
  cfo_cagr?: number | null;
}

export interface DuPont3Step {
  net_profit_margin: number;
  asset_turnover: number;
  financial_leverage: number;
  roe_calculated: number;
  roe_reported: number;
  is_valid: boolean;
  formula_expression: string;
}

export interface DuPont5Step {
  tax_burden: number;
  interest_burden: number;
  operating_margin: number;
  asset_turnover: number;
  financial_leverage: number;
  roe_calculated: number;
  roe_reported: number;
  is_valid: boolean;
  formula_expression: string;
}

export interface DuPontDecompositionResult {
  methodology_version: string;
  dupont_3step?: DuPont3Step | null;
  dupont_5step?: DuPont5Step | null;
  inputs: Record<string, any>;
  key_driver_analysis: string;
}

export interface CommonSizeLineItem {
  line_item_key: string;
  line_item_label: string;
  raw_value: number;
  percentage_of_base: number;
  base_label: string;
}

export interface CommonSizeIncomeStatement {
  base_revenue: number;
  items: CommonSizeLineItem[];
}

export interface CommonSizeBalanceSheet {
  base_assets: number;
  items: CommonSizeLineItem[];
}

export interface PeriodFundamentalAnalysis {
  period_id: number;
  period_label: string;
  fiscal_year: number;
  end_date: string;
  statement_type: string;
  profitability: Record<string, CalculatedMetric>;
  growth: Record<string, CalculatedMetric>;
  working_capital: Record<string, CalculatedMetric>;
  cash_quality: Record<string, CalculatedMetric>;
  dupont?: DuPontDecompositionResult | null;
  common_size_income?: CommonSizeIncomeStatement | null;
  common_size_balance?: CommonSizeBalanceSheet | null;
}

export interface FundamentalAnalysisResponse {
  company_id: number;
  ticker: string;
  legal_name: string;
  sector: string;
  statement_type: string;
  methodology_version: string;
  periods_analysis: PeriodFundamentalAnalysis[];
  cagr_summary?: MultiPeriodCAGRSummary | null;
}

export type CompanyFundamentalResponse = FundamentalAnalysisResponse;

export interface CompanyDuPontResponse {
  company_id: number;
  ticker: string;
  statement_type: string;
  periods: Array<{
    period_id: number;
    period_label: string;
    fiscal_year: number;
    dupont?: DuPontDecompositionResult | null;
  }>;
}

export interface CompanyCommonSizeResponse {
  company_id: number;
  ticker: string;
  statement_type: string;
  periods: Array<{
    period_id: number;
    period_label: string;
    fiscal_year: number;
    common_size_income?: CommonSizeIncomeStatement | null;
    common_size_balance?: CommonSizeBalanceSheet | null;
  }>;
}

export type ForensicRiskLevel = 'LOW' | 'MODERATE' | 'ELEVATED' | 'HIGH' | 'CRITICAL' | 'INFO' | 'NOT_APPLICABLE';

export type SignalCategory =
  | 'MANIPULATION_RISK'
  | 'FINANCIAL_HEALTH'
  | 'BANKRUPTCY_RISK'
  | 'ACCRUAL_QUALITY'
  | 'WORKING_CAPITAL'
  | 'REVENUE_RECOGNITION'
  | 'DEBT_SOLVENCY'
  | 'MARGIN_ANOMALY'
  | 'AUDIT_GOVERNANCE';

export interface ForensicSignal {
  signal_key: string;
  signal_label: string;
  category: SignalCategory;
  risk_level: ForensicRiskLevel;
  value?: number | null;
  formatted_value: string;
  benchmark_threshold: string;
  formula_expression: string;
  inputs: Record<string, any>;
  interpretation: string;
  is_applicable: boolean;
  inapplicable_reason?: string | null;
  limitations: string;
  methodology_version: string;
}

export interface BeneishVariable {
  key: string;
  name: string;
  value?: number | null;
  coefficient: number;
  contribution?: number | null;
  formula: string;
  interpretation: string;
}

export interface BeneishMScoreResult {
  period_id: number;
  period_label: string;
  fiscal_year: number;
  m_score?: number | null;
  risk_classification: ForensicRiskLevel;
  is_applicable: boolean;
  inapplicable_reason?: string | null;
  threshold: number;
  probability_of_manipulation_flag: string;
  variables: Record<string, BeneishVariable>;
  formula_expression: string;
  interpretation: string;
  limitations: string;
  methodology_version: string;
}

export interface PiotroskiSignal {
  key: string;
  category: string;
  name: string;
  passed: boolean;
  score: number;
  description: string;
  formula: string;
  inputs: Record<string, any>;
}

export interface PiotroskiFScoreResult {
  period_id: number;
  period_label: string;
  fiscal_year: number;
  f_score: number;
  max_score: number;
  risk_classification: ForensicRiskLevel;
  financial_health_label: string;
  profitability_score: number;
  leverage_liquidity_score: number;
  operating_efficiency_score: number;
  signals: PiotroskiSignal[];
  is_applicable: boolean;
  inapplicable_reason?: string | null;
  interpretation: string;
  limitations: string;
  methodology_version: string;
}

export interface AltmanZScoreResult {
  period_id: number;
  period_label: string;
  fiscal_year: number;
  model_type: string;
  z_score?: number | null;
  zone: string;
  risk_classification: ForensicRiskLevel;
  safe_threshold: number;
  distress_threshold: number;
  components: Record<string, number>;
  formula_expression: string;
  is_applicable: boolean;
  inapplicable_reason?: string | null;
  interpretation: string;
  limitations: string;
  methodology_version: string;
}

export interface PeriodForensicScorecard {
  period_id: number;
  period_label: string;
  fiscal_year: number;
  end_date: string;
  statement_type: string;
  overall_risk_level: ForensicRiskLevel;
  risk_summary_text: string;
  beneish_m_score?: BeneishMScoreResult | null;
  piotroski_f_score?: PiotroskiFScoreResult | null;
  altman_z_score?: AltmanZScoreResult | null;
  screening_signals: ForensicSignal[];
  anomalous_signals_count: number;
  total_signals_evaluated: number;
}

export interface CompanyForensicResponse {
  company_id: number;
  ticker: string;
  legal_name: string;
  sector: string;
  industry: string;
  statement_type: string;
  overall_forensic_stance: string;
  latest_scorecard?: PeriodForensicScorecard | null;
  historical_scorecards: PeriodForensicScorecard[];
  sector_applicability_notes: string[];
  methodology_version: string;
}

// ============================================================================
// PHASE 4: VALUATION ENGINE TYPES
// ============================================================================

export type ValuationMethodType =
  | 'DCF_FCFF'
  | 'DCF_FCFE'
  | 'REVERSE_DCF'
  | 'MULTIPLES_RELATIVE'
  | 'DDM_BANKS'
  | 'RESIDUAL_INCOME'
  | 'SOTP';

export type TerminalValueMethodType = 'GORDON_GROWTH' | 'EXIT_MULTIPLE';

export type ScenarioType = 'BEAR' | 'BASE' | 'BULL' | 'CUSTOM';

export interface CashFlowProjectionYear {
  year_index: number;
  fiscal_year: number;
  revenue: number;
  revenue_growth_pct: number;
  operating_profit_ebit: number;
  ebit_margin_pct: number;
  effective_tax_rate_pct: number;
  nopat: number;
  depreciation_amortization: number;
  capital_expenditure: number;
  change_in_nwc: number;
  free_cash_flow: number;
  discount_factor: number;
  discounted_fcf: number;
}

export interface WACCBreakdown {
  risk_free_rate: number;
  equity_risk_premium: number;
  beta: number;
  cost_of_equity: number;
  pre_tax_cost_of_debt: number;
  effective_tax_rate: number;
  after_tax_cost_of_debt: number;
  equity_weight_pct: number;
  debt_weight_pct: number;
  wacc_pct: number;
  formula_expression: string;
}

export interface TerminalValueDiagnostics {
  terminal_value_raw: number;
  pv_terminal_value: number;
  pv_explicit_cash_flows: number;
  enterprise_value: number;
  terminal_value_pct_of_ev: number;
  implied_exit_ev_ebitda_multiple?: number | null;
  implied_perpetual_growth_rate?: number | null;
  is_terminal_value_dominant: boolean;
  growth_vs_gdp_warning: boolean;
  warning_notes: string[];
}

export interface DCFValuationInputs {
  forecast_years: number;
  base_revenue?: number | null;
  revenue_growth_rates?: number[] | null;
  constant_revenue_growth_pct: number;
  target_ebit_margin_pct: number;
  effective_tax_rate_pct: number;
  reinvestment_rate_pct: number;
  wacc_pct?: number | null;
  cost_of_equity_pct?: number | null;
  risk_free_rate_pct: number;
  equity_risk_premium_pct: number;
  beta: number;
  pre_tax_cost_of_debt_pct: number;
  debt_to_capital_pct: number;
  terminal_value_method: TerminalValueMethodType;
  terminal_growth_rate_pct: number;
  exit_ev_ebitda_multiple: number;
  shares_outstanding_crores?: number | null;
  total_debt_crores?: number | null;
  cash_and_investments_crores?: number | null;
  minority_interest_crores?: number | null;
}

export interface DCFValuationResult {
  company_id: number;
  ticker: string;
  valuation_method: ValuationMethodType;
  valuation_date: string;
  currency: string;
  unit: string;
  inputs_applied: DCFValuationInputs;
  wacc_breakdown: WACCBreakdown;
  projections: CashFlowProjectionYear[];
  pv_explicit_forecast: number;
  terminal_value_raw: number;
  pv_terminal_value: number;
  enterprise_value: number;
  total_debt: number;
  cash_and_investments: number;
  net_debt: number;
  minority_interest: number;
  equity_value: number;
  shares_outstanding_crores: number;
  estimated_fair_value_per_share: number;
  current_market_price?: number | null;
  upside_downside_pct?: number | null;
  terminal_diagnostics: TerminalValueDiagnostics;
  formula_lineage: Record<string, string>;
  methodology_version: string;
}

export interface ReverseDCFInputs {
  current_market_price: number;
  shares_outstanding_crores?: number | null;
  forecast_years?: number;
  target_ebit_margin_pct?: number | null;
  wacc_pct?: number;
  terminal_growth_rate_pct?: number;
  effective_tax_rate_pct?: number;
  reinvestment_rate_pct?: number;
  net_debt_crores?: number | null;
}

export interface ReverseDCFResult {
  company_id: number;
  ticker: string;
  current_market_price: number;
  current_market_cap_crores: number;
  implied_enterprise_value: number;
  wacc_pct: number;
  terminal_growth_rate_pct: number;
  assumed_ebit_margin_pct: number;
  implied_revenue_cagr_pct: number;
  implied_fcf_cagr_pct: number;
  historical_revenue_cagr_3yr?: number | null;
  growth_premium_vs_historical_pct?: number | null;
  implied_5yr_revenue_target: number;
  implied_5yr_fcf_target: number;
  plausibility_assessment: 'CONSERVATIVE' | 'REALISTIC' | 'AGGRESSIVE' | 'EXTREME';
  plausibility_reasoning: string;
  sensitivities: Array<{
    wacc_pct: number;
    ebit_margin_pct: number;
    implied_growth_needed_pct: number;
  }>;
  methodology_version: string;
}

export interface MultipleMetricComparison {
  multiple_name: string;
  current_multiple?: number | null;
  historical_1yr_median?: number | null;
  historical_3yr_median?: number | null;
  historical_5yr_median?: number | null;
  historical_min?: number | null;
  historical_max?: number | null;
  peer_benchmark_median?: number | null;
  underlying_financial_metric: number;
  target_multiple_applied: number;
  implied_fair_value_per_share: number;
  upside_downside_pct?: number | null;
  limitations: string;
}

export interface MultiplesValuationResult {
  company_id: number;
  ticker: string;
  current_market_price: number;
  multiples: MultipleMetricComparison[];
  composite_median_fair_value: number;
  composite_upside_downside_pct?: number | null;
  methodology_notes: string[];
  methodology_version: string;
}

export interface ScenarioCase {
  scenario_type: ScenarioType;
  probability_weight_pct: number;
  revenue_growth_pct: number;
  ebit_margin_pct: number;
  wacc_pct: number;
  terminal_growth_pct: number;
  estimated_fair_value_per_share: number;
  upside_downside_pct?: number | null;
  key_assumptions: string[];
}

export interface ScenarioAnalysisResult {
  company_id: number;
  ticker: string;
  current_market_price: number;
  scenarios: ScenarioCase[];
  probability_weighted_fair_value: number;
  expected_upside_downside_pct: number;
  risk_reward_skew: 'FAVORABLE' | 'SYMMETRIC' | 'UNFAVORABLE';
  methodology_version: string;
}

export interface SensitivityCell {
  row_value: number;
  col_value: number;
  fair_value_per_share: number;
  upside_downside_pct?: number | null;
}

export interface SensitivityMatrixResult {
  matrix_name: string;
  row_parameter_name: string;
  row_parameter_unit: string;
  col_parameter_name: string;
  col_parameter_unit: string;
  row_values: number[];
  col_values: number[];
  grid: SensitivityCell[][];
  base_row_value: number;
  base_col_value: number;
  base_fair_value: number;
}

export interface BankDDMYear {
  year_index: number;
  fiscal_year: number;
  total_assets: number;
  loan_growth_pct: number;
  net_worth: number;
  return_on_equity_pct: number;
  net_profit_pat: number;
  tier1_capital_retention_pct: number;
  dividend_payout_pct: number;
  dividends_paid: number;
  discount_factor: number;
  discounted_dividend: number;
}

export interface BankValuationResult {
  company_id: number;
  ticker: string;
  sector: string;
  valuation_method: ValuationMethodType;
  is_financial_institution: boolean;
  current_book_value_per_share: number;
  current_roe_pct: number;
  cost_of_equity_pct: number;
  sustainable_growth_rate_pct: number;
  projections: BankDDMYear[];
  pv_explicit_dividends: number;
  terminal_value_dividends: number;
  pv_terminal_value: number;
  ddm_fair_value_per_share: number;
  justified_pb_multiple: number;
  justified_pb_fair_value_per_share: number;
  current_market_price?: number | null;
  upside_downside_pct?: number | null;
  methodology_notes: string[];
  limitations: string;
  methodology_version: string;
}

export interface SOTPSegment {
  segment_name: string;
  segment_description: string;
  revenue: number;
  ebitda: number;
  benchmark_ev_ebitda_multiple: number;
  implied_enterprise_value: number;
  ownership_stake_pct: number;
  effective_enterprise_value: number;
}

export interface SOTPValuationResult {
  company_id: number;
  ticker: string;
  segments: SOTPSegment[];
  gross_enterprise_value: number;
  holding_company_discount_pct: number;
  net_enterprise_value: number;
  net_debt: number;
  equity_value: number;
  shares_outstanding_crores: number;
  fair_value_per_share: number;
  current_market_price?: number | null;
  upside_downside_pct?: number | null;
  methodology_version: string;
}

export interface ValuationSummaryResponse {
  company_id: number;
  ticker: string;
  legal_name: string;
  sector: string;
  is_financial_institution: boolean;
  current_market_price: number;
  shares_outstanding_crores: number;
  market_cap_crores: number;
  dcf_result?: DCFValuationResult | null;
  reverse_dcf_result?: ReverseDCFResult | null;
  multiples_result?: MultiplesValuationResult | null;
  scenario_result?: ScenarioAnalysisResult | null;
  bank_valuation_result?: BankValuationResult | null;
  composite_fair_value_range_low: number;
  composite_fair_value_range_high: number;
  composite_central_fair_value: number;
  composite_upside_downside_pct: number;
  valuation_summary_text: string;
  methodology_version: string;
}

// ---------------------------------------------------------------------------
// Phase 6: Document Intelligence & Annual Report RAG Types
// ---------------------------------------------------------------------------

export type DocumentType = 
  | 'ANNUAL_REPORT'
  | 'EARNINGS_CALL_TRANSCRIPT'
  | 'INVESTOR_PRESENTATION'
  | 'AUDITOR_REPORT'
  | 'REGULATORY_FILING';

export type DocumentProcessingStatus = 
  | 'PENDING'
  | 'PARSING'
  | 'CHUNKING'
  | 'INDEXING'
  | 'COMPLETED'
  | 'FAILED';

export interface DocumentPageDTO {
  page_number: number;
  detected_section?: string | null;
  char_count: number;
  has_tables: boolean;
  text: string;
}

export interface DocumentMetadataDTO {
  id: number;
  ticker: string;
  fiscal_year: number;
  document_type: DocumentType;
  title: string;
  file_name: string;
  source_url?: string | null;
  file_hash_sha256: string;
  page_count: number;
  file_size_bytes: number;
  extraction_method: string;
  processing_status: DocumentProcessingStatus;
  error_message?: string | null;
  retrieval_date: string;
  total_chunks: number;
}

export interface DocumentDetailDTO extends DocumentMetadataDTO {
  sections_detected: string[];
  pages: DocumentPageDTO[];
}

export interface EvidenceCitation {
  document_id: number;
  document_title: string;
  ticker: string;
  fiscal_year: number;
  page_number: number;
  section_title: string;
  exact_quote: string;
  char_start?: number | null;
  char_end?: number | null;
  relevance_score: number;
  source_url?: string | null;
  provenance_hash: string;
}

export interface DocumentRetrievalQuery {
  query_text: string;
  ticker?: string;
  fiscal_year?: number;
  section?: string;
  document_type?: DocumentType;
  top_k?: number;
  min_relevance_score?: number;
}

export interface DocumentRetrievalResult {
  chunk_id: number;
  document_id: number;
  document_title: string;
  ticker: string;
  fiscal_year: number;
  page_number: number;
  section_title: string;
  chunk_text: string;
  relevance_score: number;
  citation: EvidenceCitation;
}

export interface DocumentRetrievalResponse {
  query_text: string;
  filters_applied: Record<string, any>;
  total_matches: number;
  results: DocumentRetrievalResult[];
  retrieval_latency_ms: number;
  embedding_model: string;
  methodology_version: string;
}

export interface IngestionUploadResponse {
  document_id: number;
  ticker: string;
  fiscal_year: number;
  file_name: string;
  file_hash_sha256: string;
  page_count: number;
  total_chunks_indexed: number;
  sections_detected: string[];
  processing_status: DocumentProcessingStatus;
  message: string;
}





