"""FastAPI REST Endpoints for Forensic Intelligence Engine."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.db.session import get_db
from app.models.company import Company
from app.models.financial_statements import StatementType
from app.models.forensic import (
    CompanyForensicResponse,
    BeneishMScoreResult,
    PiotroskiFScoreResult,
    AltmanZScoreResult,
    ForensicSignal,
)
from app.engine.forensic.forensic_service import ForensicAnalysisService

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


@router.get(
    "/companies/{identifier}/forensics/summary",
    response_model=CompanyForensicResponse,
    summary="Get full multi-period forensic intelligence scorecard"
)
async def get_forensic_summary(
    identifier: str,
    statement_type: StatementType = Query(StatementType.CONSOLIDATED, description="CONSOLIDATED or STANDALONE"),
    limit_periods: int = Query(5, ge=1, le=10, description="Number of historical periods to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve full company forensic intelligence report including Beneish M-Score, Piotroski F-Score, Altman Z''-Score, and anomaly signals."""
    company = await resolve_company(db, identifier)
    return await ForensicAnalysisService.analyze_company(db, company, statement_type, limit_periods)


@router.get(
    "/companies/{identifier}/forensics/beneish",
    summary="Get Beneish 8-variable M-Score historical trajectory"
)
async def get_beneish_trajectory(
    identifier: str,
    statement_type: StatementType = Query(StatementType.CONSOLIDATED),
    limit_periods: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve historical Beneish M-Scores and individual 8-variable contributions."""
    company = await resolve_company(db, identifier)
    report = await ForensicAnalysisService.analyze_company(db, company, statement_type, limit_periods)
    return {
        "company_id": company.id,
        "ticker": company.ticker,
        "legal_name": company.legal_name,
        "sector": company.sector,
        "statement_type": statement_type,
        "threshold": -1.78,
        "periods": [
            {
                "period_id": sc.period_id,
                "period_label": sc.period_label,
                "fiscal_year": sc.fiscal_year,
                "beneish": sc.beneish_m_score
            }
            for sc in report.historical_scorecards
        ]
    }


@router.get(
    "/companies/{identifier}/forensics/piotroski",
    summary="Get Piotroski 9-point F-Score breakdown"
)
async def get_piotroski_breakdown(
    identifier: str,
    statement_type: StatementType = Query(StatementType.CONSOLIDATED),
    limit_periods: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve historical Piotroski F-Scores and detailed 9-point signal evaluations."""
    company = await resolve_company(db, identifier)
    report = await ForensicAnalysisService.analyze_company(db, company, statement_type, limit_periods)
    return {
        "company_id": company.id,
        "ticker": company.ticker,
        "legal_name": company.legal_name,
        "statement_type": statement_type,
        "periods": [
            {
                "period_id": sc.period_id,
                "period_label": sc.period_label,
                "fiscal_year": sc.fiscal_year,
                "piotroski": sc.piotroski_f_score
            }
            for sc in report.historical_scorecards
        ]
    }


@router.get(
    "/companies/{identifier}/forensics/altman",
    summary="Get Altman Z-Score & distress zone classification"
)
async def get_altman_distress(
    identifier: str,
    statement_type: StatementType = Query(StatementType.CONSOLIDATED),
    limit_periods: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve historical Altman Z''-Score and zone classifications."""
    company = await resolve_company(db, identifier)
    report = await ForensicAnalysisService.analyze_company(db, company, statement_type, limit_periods)
    return {
        "company_id": company.id,
        "ticker": company.ticker,
        "legal_name": company.legal_name,
        "statement_type": statement_type,
        "periods": [
            {
                "period_id": sc.period_id,
                "period_label": sc.period_label,
                "fiscal_year": sc.fiscal_year,
                "altman": sc.altman_z_score
            }
            for sc in report.historical_scorecards
        ]
    }


@router.get(
    "/companies/{identifier}/forensics/signals",
    summary="Get granular forensic screening anomaly signals"
)
async def get_forensic_signals(
    identifier: str,
    statement_type: StatementType = Query(StatementType.CONSOLIDATED),
    limit_periods: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve granular screening signals for accrual, working capital, debt, and margin anomalies."""
    company = await resolve_company(db, identifier)
    report = await ForensicAnalysisService.analyze_company(db, company, statement_type, limit_periods)
    return {
        "company_id": company.id,
        "ticker": company.ticker,
        "legal_name": company.legal_name,
        "statement_type": statement_type,
        "periods": [
            {
                "period_id": sc.period_id,
                "period_label": sc.period_label,
                "fiscal_year": sc.fiscal_year,
                "overall_risk_level": sc.overall_risk_level,
                "anomalous_signals_count": sc.anomalous_signals_count,
                "signals": sc.screening_signals
            }
            for sc in report.historical_scorecards
        ]
    }
