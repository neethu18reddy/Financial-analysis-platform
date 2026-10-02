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
