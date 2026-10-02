"""API response and request schemas for the Financial Data Engine."""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.source import DataClassification, SourceType
from app.models.financial_period import PeriodType, ReportingStandard, FinancialUnit
from app.models.financial_statements import StatementType
from app.models.corporate_actions import ActionType
from app.models.validation import ValidationStatus, ValidationCategory


# --- Source Registry Schemas ---
class SourceProviderOut(BaseModel):
    provider_id: str
    provider_name: str
    source_type: SourceType
    access_method: str
    terms_and_license: str
    storage_restrictions: str
    redistribution_restrictions: str
    attribution_requirements: str
    rate_limits: str
    primary_url: str
    supported_classifications: List[DataClassification]


class SourceDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_name: str
    provider: str
    source_type: SourceType
    data_classification: DataClassification
    file_path_or_url: Optional[str] = None
    retrieval_date: datetime
    filing_date: Optional[datetime] = None
    terms_and_license: str
    redistribution_allowed: bool
    attribution_notes: Optional[str] = None


# --- Company Schemas ---
class SecurityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    series: str
    isin: str
    exchange: str
    currency: str
    lot_size: int
    is_suspended: bool


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cin: str
    ticker: str
    legal_name: str
    trade_name: Optional[str] = None
    sector: str
    industry: str
    isin: str
    primary_exchange: str
    founded_year: Optional[int] = None
    registered_state: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    is_active: bool


class CompanyDetailOut(CompanyOut):
    securities: List[SecurityOut] = []


# --- Financial Period Schemas ---
class FinancialPeriodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    period_type: PeriodType
    fiscal_year: int
    fiscal_quarter: Optional[int] = None
    period_label: str
    start_date: date
    end_date: date
    filing_date: Optional[date] = None
    reporting_standard: ReportingStandard
    currency: str
    canonical_unit: FinancialUnit
    is_audited: bool


# --- Statement Schemas ---
class IncomeStatementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    period_id: int
    statement_type: StatementType
    revenue_from_operations: float
    other_income: float
    total_revenue: float
    cost_of_materials_consumed: float
    purchases_of_stock_in_trade: float
    changes_in_inventories: float
    employee_benefit_expenses: float
    finance_costs: float
    depreciation_and_amortization: float
    other_expenses: float
    total_expenses: float
    operating_profit: float
    profit_before_exceptional_items_and_tax: float
    exceptional_items: float
    profit_before_tax: float
    current_tax: float
    deferred_tax: float
    total_tax_expense: float
    profit_after_tax: float
    minority_interest: float
    share_of_profit_associates: float
    net_profit_attributable_to_owners: float
    basic_eps: Optional[float] = None
    diluted_eps: Optional[float] = None


class BalanceSheetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    period_id: int
    statement_type: StatementType
    property_plant_equipment: float
    capital_work_in_progress: float
    goodwill_and_intangibles: float
    non_current_investments: float
    deferred_tax_assets: float
    other_non_current_assets: float
    total_non_current_assets: float
    inventories: float
    trade_receivables: float
    cash_and_cash_equivalents: float
    bank_balances_other: float
    short_term_loans_and_advances: float
    other_current_assets: float
    total_current_assets: float
    total_assets: float
    equity_share_capital: float
    other_equity_and_reserves: float
    non_controlling_interests: float
    total_equity: float
    non_current_borrowings: float
    deferred_tax_liabilities: float
    other_non_current_liabilities: float
    total_non_current_liabilities: float
    current_borrowings: float
    trade_payables: float
    other_current_liabilities: float
    short_term_provisions: float
    total_current_liabilities: float
    total_liabilities: float
    total_equity_and_liabilities: float


class CashFlowStatementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    period_id: int
    statement_type: StatementType
    cash_from_operating_activities: float
    cash_from_investing_activities: float
    cash_from_financing_activities: float
    net_increase_in_cash: float
    foreign_exchange_effect: float
    cash_beginning_of_period: float
    cash_end_of_period: float
    capital_expenditure: float
    free_cash_flow: float
    dividend_paid: float


class MultiPeriodFinancialSet(BaseModel):
    period: FinancialPeriodOut
    income_statement: Optional[IncomeStatementOut] = None
    balance_sheet: Optional[BalanceSheetOut] = None
    cash_flow: Optional[CashFlowStatementOut] = None
    validation_status: str = "PASSED"
    validation_passed_count: int = 0
    validation_failed_count: int = 0


class CompanyStatementsResponse(BaseModel):
    company: CompanyOut
    statement_type: StatementType
    display_unit: FinancialUnit
    periods_data: List[MultiPeriodFinancialSet]


# --- Provenance Schemas ---
class DataProvenanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_document_id: int
    entity_type: str
    entity_id: int
    field_name: str
    reported_label: str
    reported_value_raw: str
    reported_unit: str
    reported_currency: str
    normalized_value: float
    normalized_unit: str
    page_number: Optional[int] = None
    table_reference: Optional[str] = None
    note_reference: Optional[str] = None
    extraction_method: str
    confidence_score: float
    transformation_applied: Optional[str] = None
    source_document: Optional[SourceDocumentOut] = None


# --- Validation Schemas ---
class ValidationResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: str
    entity_id: int
    company_id: Optional[int] = None
    period_id: Optional[int] = None
    rule_name: str
    category: ValidationCategory
    status: ValidationStatus
    formula_checked: str
    expected_value: Optional[float] = None
    actual_value: Optional[float] = None
    discrepancy: Optional[float] = None
    tolerance: float
    message: str
    validated_at: datetime


class ValidationAuditReport(BaseModel):
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    is_fully_reconciled: bool
    results: List[ValidationResultOut]


# --- Corporate Action Schemas ---
class CorporateActionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    action_type: ActionType
    ex_date: date
    record_date: Optional[date] = None
    ratio_numerator: Optional[float] = None
    ratio_denominator: Optional[float] = None
    adjustment_factor: float
    dividend_per_share: Optional[float] = None
    notes: Optional[str] = None
