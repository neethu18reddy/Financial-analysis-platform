"""Deterministic Financial Data Engine Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.company import Company, Security
from app.models.financial_period import FinancialPeriod, FinancialUnit
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement, StatementType
from app.models.corporate_actions import CorporateAction
from app.models.provenance import DataProvenance
from app.models.validation import ValidationResult, ValidationStatus
from app.engine.source_registry import SOURCE_REGISTRY
from app.schemas.financial_engine import (
    CompanyOut,
    CompanyDetailOut,
    FinancialPeriodOut,
    CompanyStatementsResponse,
    MultiPeriodFinancialSet,
    IncomeStatementOut,
    BalanceSheetOut,
    CashFlowStatementOut,
    DataProvenanceOut,
    ValidationResultOut,
    ValidationAuditReport,
    CorporateActionOut,
    SourceProviderOut,
)

router = APIRouter()


async def get_company_by_identifier(db: AsyncSession, identifier: str) -> Company:
    """Helper to resolve company by numeric ID, ticker symbol, or CIN."""
    query = select(Company).options(selectinload(Company.securities))
    if identifier.isdigit():
        query = query.where(Company.id == int(identifier))
    else:
        ident_upper = identifier.upper().strip()
        query = query.where(or_(Company.ticker == ident_upper, Company.cin == ident_upper))
    
    result = await db.execute(query)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with identifier '{identifier}' was not found in registry."
        )
    return company


@router.get("/companies", response_model=List[CompanyOut], summary="List all listed companies")
async def list_companies(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    search: Optional[str] = Query(None, description="Search by ticker, legal name, or CIN"),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve list of listed companies in registry with optional sector or search filters."""
    query = select(Company).where(Company.is_active.is_(True))
    if sector:
        query = query.where(Company.sector.ilike(f"%{sector}%"))
    if search:
        s_term = f"%{search}%"
        query = query.where(
            or_(
                Company.ticker.ilike(s_term),
                Company.legal_name.ilike(s_term),
                Company.cin.ilike(s_term),
                Company.trade_name.ilike(s_term)
            )
        )
    query = query.order_by(Company.ticker.asc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/companies/{identifier}", response_model=CompanyDetailOut, summary="Get company profile details")
async def get_company(identifier: str, db: AsyncSession = Depends(get_db)):
    """Retrieve comprehensive profile, ISIN, CIN, and securities for a specific company."""
    return await get_company_by_identifier(db, identifier)


@router.get("/companies/{identifier}/periods", response_model=List[FinancialPeriodOut], summary="List financial reporting periods")
async def get_company_periods(identifier: str, db: AsyncSession = Depends(get_db)):
    """Retrieve all available reporting periods (annual, quarterly) for a company in chronological order."""
    company = await get_company_by_identifier(db, identifier)
    query = select(FinancialPeriod).where(FinancialPeriod.company_id == company.id).order_by(FinancialPeriod.end_date.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/companies/{identifier}/statements", response_model=CompanyStatementsResponse, summary="Get multi-period financial statements")
async def get_financial_statements(
    identifier: str,
    statement_type: StatementType = Query(StatementType.CONSOLIDATED, description="Statement type: CONSOLIDATED or STANDALONE"),
    limit_periods: int = Query(5, ge=1, le=10, description="Number of recent historical periods to fetch"),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve multi-period normalized financial statements (Income Statement, Balance Sheet, Cash Flow) with validation counts."""
    company = await get_company_by_identifier(db, identifier)

    # Fetch recent periods
    p_query = (
        select(FinancialPeriod)
        .where(FinancialPeriod.company_id == company.id)
        .order_by(FinancialPeriod.end_date.desc())
        .limit(limit_periods)
    )
    p_res = await db.execute(p_query)
    periods = p_res.scalars().all()

    periods_data: List[MultiPeriodFinancialSet] = []

    for period in periods:
        # Fetch Income Statement
        is_stmt = select(IncomeStatement).where(
            IncomeStatement.period_id == period.id,
            IncomeStatement.statement_type == statement_type
        )
        is_res = await db.execute(is_stmt)
        income_stmt = is_res.scalar_one_or_none()

        # Fetch Balance Sheet
        bs_stmt = select(BalanceSheet).where(
            BalanceSheet.period_id == period.id,
            BalanceSheet.statement_type == statement_type
        )
        bs_res = await db.execute(bs_stmt)
        balance_sheet = bs_res.scalar_one_or_none()

        # Fetch Cash Flow
        cf_stmt = select(CashFlowStatement).where(
            CashFlowStatement.period_id == period.id,
            CashFlowStatement.statement_type == statement_type
        )
        cf_res = await db.execute(cf_stmt)
        cash_flow = cf_res.scalar_one_or_none()

        # Fetch validation counts for this period
        val_query = select(ValidationResult).where(ValidationResult.period_id == period.id)
        val_res = await db.execute(val_query)
        val_records = val_res.scalars().all()
        
        passed_count = sum(1 for v in val_records if v.status == ValidationStatus.PASSED)
        failed_count = sum(1 for v in val_records if v.status == ValidationStatus.FAILED)
        period_val_status = "FAILED" if failed_count > 0 else "PASSED"

        periods_data.append(MultiPeriodFinancialSet(
            period=FinancialPeriodOut.model_validate(period),
            income_statement=IncomeStatementOut.model_validate(income_stmt) if income_stmt else None,
            balance_sheet=BalanceSheetOut.model_validate(balance_sheet) if balance_sheet else None,
            cash_flow=CashFlowStatementOut.model_validate(cash_flow) if cash_flow else None,
            validation_status=period_val_status,
            validation_passed_count=passed_count,
            validation_failed_count=failed_count
        ))

    return CompanyStatementsResponse(
        company=CompanyOut.model_validate(company),
        statement_type=statement_type,
        display_unit=FinancialUnit.CRORES,
        periods_data=periods_data
    )


@router.get("/companies/{identifier}/corporate-actions", response_model=List[CorporateActionOut], summary="List corporate actions")
async def get_corporate_actions(identifier: str, db: AsyncSession = Depends(get_db)):
    """Retrieve all corporate actions (dividends, splits, bonuses, buybacks) for a company."""
    company = await get_company_by_identifier(db, identifier)
    query = (
        select(CorporateAction)
        .where(CorporateAction.company_id == company.id)
        .order_by(CorporateAction.ex_date.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/companies/{identifier}/validation-report", response_model=ValidationAuditReport, summary="Get deterministic validation audit report")
async def get_validation_report(identifier: str, db: AsyncSession = Depends(get_db)):
    """Retrieve comprehensive deterministic validation report for all periods and statements of a company."""
    company = await get_company_by_identifier(db, identifier)
    query = (
        select(ValidationResult)
        .where(ValidationResult.company_id == company.id)
        .order_by(ValidationResult.validated_at.desc(), ValidationResult.id.asc())
    )
    result = await db.execute(query)
    records = result.scalars().all()

    total = len(records)
    passed = sum(1 for r in records if r.status == ValidationStatus.PASSED)
    failed = sum(1 for r in records if r.status == ValidationStatus.FAILED)
    warning = sum(1 for r in records if r.status == ValidationStatus.WARNING)

    return ValidationAuditReport(
        total_checks=total,
        passed_checks=passed,
        failed_checks=failed,
        warning_checks=warning,
        is_fully_reconciled=(failed == 0 and total > 0),
        results=[ValidationResultOut.model_validate(r) for r in records]
    )


@router.get("/provenance/{entity_type}/{entity_id}", response_model=List[DataProvenanceOut], summary="Field-level provenance and source audit lineage")
async def get_provenance_records(
    entity_type: str,
    entity_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve field-level provenance audit records linking financial data to exact source filings."""
    query = (
        select(DataProvenance)
        .options(selectinload(DataProvenance.source_document))
        .where(
            DataProvenance.entity_type == entity_type,
            DataProvenance.entity_id == entity_id
        )
    )
    result = await db.execute(query)
    records = result.scalars().all()
    return records


@router.get("/sources", response_model=List[SourceProviderOut], summary="Source registry and compliance policies")
async def list_sources():
    """Retrieve registry of external data sources with compliance terms, rate limits, and licensing restrictions."""
    return list(SOURCE_REGISTRY.values())
