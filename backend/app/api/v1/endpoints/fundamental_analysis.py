"""FastAPI REST endpoints for Fundamental Analysis Engine."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.db.session import get_db
from app.models.company import Company
from app.models.financial_statements import StatementType
from app.engine.fundamental.analysis_service import (
    FundamentalAnalysisService,
    FundamentalAnalysisResponse,
    PeriodFundamentalAnalysis,
    MultiPeriodCAGRSummary,
)
from app.engine.fundamental.profitability import CalculatedMetric
from app.engine.fundamental.dupont import DuPontDecompositionResult
from app.engine.fundamental.common_size import CommonSizeIncomeStatement, CommonSizeBalanceSheet

router = APIRouter()


async def resolve_company(db: AsyncSession, identifier: str) -> Company:
    """Helper to resolve company by numeric ID, ticker symbol, or CIN."""
    query = select(Company)
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
            detail=f"Company with identifier '{identifier}' was not found."
        )
    return company


@router.get("/companies/{identifier}/analysis/full", response_model=FundamentalAnalysisResponse, summary="Get comprehensive fundamental analysis")
async def get_full_fundamental_analysis(
    identifier: str,
    statement_type: StatementType = Query(StatementType.CONSOLIDATED, description="CONSOLIDATED or STANDALONE"),
    limit_periods: int = Query(5, ge=1, le=10, description="Number of historical periods to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve full fundamental analysis package across all periods with profitability, growth, working capital, cash quality, DuPont, and common-size statements."""
    company = await resolve_company(db, identifier)
    return await FundamentalAnalysisService.analyze_company(db, company, statement_type, limit_periods)


@router.get("/companies/{identifier}/analysis/profitability", summary="Get profitability & return metrics")
async def get_profitability_metrics(
    identifier: str,
    statement_type: StatementType = Query(StatementType.CONSOLIDATED),
    limit_periods: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve gross margin, EBITDA margin, EBIT margin, PAT margin, ROE, ROCE, ROIC, and ROA."""
    company = await resolve_company(db, identifier)
    analysis = await FundamentalAnalysisService.analyze_company(db, company, statement_type, limit_periods)
    return {
        "company_id": company.id,
        "ticker": company.ticker,
        "statement_type": statement_type,
        "methodology_version": analysis.methodology_version,
        "periods": [
            {
                "period_id": p.period_id,
                "period_label": p.period_label,
                "fiscal_year": p.fiscal_year,
                "end_date": p.end_date,
                "metrics": p.profitability
            }
            for p in analysis.periods_analysis
        ]
    }


@router.get("/companies/{identifier}/analysis/growth", summary="Get YoY and CAGR growth rates")
async def get_growth_metrics(
    identifier: str,
    statement_type: StatementType = Query(StatementType.CONSOLIDATED),
    limit_periods: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve YoY growth rates for revenue, EBITDA, EBIT, PAT, CFO, and multi-year CAGR summary."""
    company = await resolve_company(db, identifier)
    analysis = await FundamentalAnalysisService.analyze_company(db, company, statement_type, limit_periods)
    return {
        "company_id": company.id,
        "ticker": company.ticker,
        "statement_type": statement_type,
        "cagr_summary": analysis.cagr_summary,
        "yoy_growth_periods": [
            {
                "period_id": p.period_id,
                "period_label": p.period_label,
                "fiscal_year": p.fiscal_year,
                "growth_metrics": p.growth
            }
            for p in analysis.periods_analysis
        ]
    }


@router.get("/companies/{identifier}/analysis/working-capital", summary="Get working capital and efficiency cycles")
async def get_working_capital_metrics(
    identifier: str,
    statement_type: StatementType = Query(StatementType.CONSOLIDATED),
    limit_periods: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve DSO, DIO, DPO, Cash Conversion Cycle (CCC), and Asset Turnover."""
    company = await resolve_company(db, identifier)
    analysis = await FundamentalAnalysisService.analyze_company(db, company, statement_type, limit_periods)
    return {
        "company_id": company.id,
        "ticker": company.ticker,
        "statement_type": statement_type,
        "periods": [
            {
                "period_id": p.period_id,
                "period_label": p.period_label,
                "fiscal_year": p.fiscal_year,
                "working_capital_metrics": p.working_capital
            }
            for p in analysis.periods_analysis
        ]
    }


@router.get("/companies/{identifier}/analysis/dupont", summary="Get 3-step and 5-step DuPont ROE decomposition")
async def get_dupont_decomposition(
    identifier: str,
    statement_type: StatementType = Query(StatementType.CONSOLIDATED),
    limit_periods: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve 3-step and 5-step DuPont ROE breakdown explaining margins, efficiency, leverage, and tax drivers."""
    company = await resolve_company(db, identifier)
    analysis = await FundamentalAnalysisService.analyze_company(db, company, statement_type, limit_periods)
    return {
        "company_id": company.id,
        "ticker": company.ticker,
        "statement_type": statement_type,
        "periods": [
            {
                "period_id": p.period_id,
                "period_label": p.period_label,
                "fiscal_year": p.fiscal_year,
                "dupont": p.dupont
            }
            for p in analysis.periods_analysis
        ]
    }


@router.get("/companies/{identifier}/analysis/common-size", summary="Get vertical common-size financial statements")
async def get_common_size_statements(
    identifier: str,
    statement_type: StatementType = Query(StatementType.CONSOLIDATED),
    limit_periods: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve common-size Income Statement (% of Total Revenue) and Balance Sheet (% of Total Assets)."""
    company = await resolve_company(db, identifier)
    analysis = await FundamentalAnalysisService.analyze_company(db, company, statement_type, limit_periods)
    return {
        "company_id": company.id,
        "ticker": company.ticker,
        "statement_type": statement_type,
        "periods": [
            {
                "period_id": p.period_id,
                "period_label": p.period_label,
                "fiscal_year": p.fiscal_year,
                "common_size_income": p.common_size_income,
                "common_size_balance": p.common_size_balance
            }
            for p in analysis.periods_analysis
        ]
    }
