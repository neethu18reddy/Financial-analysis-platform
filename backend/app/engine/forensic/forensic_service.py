"""Forensic Analysis Orchestration Service.

Coordinates:
- BeneishMScoreEngine (8-variable earnings manipulation test)
- PiotroskiFScoreEngine (9-point fundamental health test)
- AltmanZScoreEngine (Emerging Market Z''-score & distress zones)
- ForensicSignalsEngine (Granular accrual, WC divergence, debt anomalies)
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.company import Company
from app.models.financial_period import FinancialPeriod
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement, StatementType
from app.models.forensic import (
    CompanyForensicResponse,
    PeriodForensicScorecard,
    ForensicRiskLevel,
    BeneishMScoreResult,
    PiotroskiFScoreResult,
    AltmanZScoreResult,
    ForensicSignal,
)
from app.engine.forensic.beneish import BeneishMScoreEngine
from app.engine.forensic.piotroski import PiotroskiFScoreEngine
from app.engine.forensic.altman import AltmanZScoreEngine
from app.engine.forensic.signals import ForensicSignalsEngine


class ForensicAnalysisService:
    """Orchestrator generating comprehensive forensic scorecards and signal histories."""

    METHODOLOGY_VERSION = "v1.0.0"

    FINANCIAL_SECTOR_KEYWORDS = [
        "bank", "banking", "finance", "financial", "insurance", "nbfc", "lending", "credit"
    ]

    @classmethod
    def is_financial_entity(cls, company: Company) -> bool:
        """Check if company belongs to the banking/financial services sector."""
        sector_str = f"{company.sector or ''} {company.industry or ''}".lower()
        return any(kw in sector_str for kw in cls.FINANCIAL_SECTOR_KEYWORDS)

    @classmethod
    async def analyze_company(
        cls,
        db: AsyncSession,
        company: Company,
        statement_type: StatementType = StatementType.CONSOLIDATED,
        limit_periods: int = 5
    ) -> CompanyForensicResponse:
        """Execute full forensic analysis across historical periods for a company."""
        # 1. Check Sector Eligibility
        is_fin = cls.is_financial_entity(company)
        sector_notes: List[str] = []
        if is_fin:
            sector_notes.append(
                "Company identified as a Banking/Financial Services institution. Industrial accrual models (Beneish M-Score, Altman Z-Score) are classified as NOT_APPLICABLE."
            )
        else:
            sector_notes.append("Standard Non-Financial Corporate: Full industrial forensic suite applied (Beneish, Piotroski, Altman Z'', Accrual Divergence).")

        # 2. Fetch financial periods ordered chronologically (oldest -> newest)
        p_stmt = (
            select(FinancialPeriod)
            .where(FinancialPeriod.company_id == company.id)
            .order_by(FinancialPeriod.end_date.asc())
            .limit(limit_periods)
        )
        p_res = await db.execute(p_stmt)
        periods = p_res.scalars().all()

        # Pre-fetch all statements
        statements_by_period: Dict[int, Dict[str, Any]] = {}
        for period in periods:
            # Income statement
            is_stmt = select(IncomeStatement).where(
                IncomeStatement.period_id == period.id,
                IncomeStatement.statement_type == statement_type
            )
            is_res = await db.execute(is_stmt)
            inc = is_res.scalar_one_or_none()

            # Balance sheet
            bs_stmt = select(BalanceSheet).where(
                BalanceSheet.period_id == period.id,
                BalanceSheet.statement_type == statement_type
            )
            bs_res = await db.execute(bs_stmt)
            bal = bs_res.scalar_one_or_none()

            # Cash flow
            cf_stmt = select(CashFlowStatement).where(
                CashFlowStatement.period_id == period.id,
                CashFlowStatement.statement_type == statement_type
            )
            cf_res = await db.execute(cf_stmt)
            cf = cf_res.scalar_one_or_none()

            statements_by_period[period.id] = {"inc": inc, "bal": bal, "cf": cf, "period": period}

        scorecards: List[PeriodForensicScorecard] = []

        # 3. Iterate through periods and execute models
        for idx, period in enumerate(periods):
            curr = statements_by_period[period.id]
            prev = statements_by_period[periods[idx - 1].id] if idx > 0 else None

            inc_curr = curr["inc"]
            bal_curr = curr["bal"]
            cf_curr = curr["cf"]

            inc_prev = prev["inc"] if prev else None
            bal_prev = prev["bal"] if prev else None
            cf_prev = prev["cf"] if prev else None

            # Calculate Beneish M-Score
            beneish_res = BeneishMScoreEngine.calculate(
                inc_curr=inc_curr,
                bal_curr=bal_curr,
                cf_curr=cf_curr,
                inc_prev=inc_prev,
                bal_prev=bal_prev,
                is_financial_sector=is_fin,
                period_id=period.id,
                period_label=period.period_label,
                fiscal_year=period.fiscal_year,
            )

            # Calculate Piotroski F-Score
            piotroski_res = PiotroskiFScoreEngine.calculate(
                inc_curr=inc_curr,
                bal_curr=bal_curr,
                cf_curr=cf_curr,
                inc_prev=inc_prev,
                bal_prev=bal_prev,
                period_id=period.id,
                period_label=period.period_label,
                fiscal_year=period.fiscal_year,
            )

            # Calculate Altman Z''-Score
            altman_res = AltmanZScoreEngine.calculate(
                inc=inc_curr,
                bal=bal_curr,
                is_financial_sector=is_fin,
                period_id=period.id,
                period_label=period.period_label,
                fiscal_year=period.fiscal_year,
                prefer_emerging_market=True,
            )

            # Calculate Granular Signals
            granular_signals = ForensicSignalsEngine.evaluate_all(
                inc_curr=inc_curr,
                bal_curr=bal_curr,
                cf_curr=cf_curr,
                inc_prev=inc_prev,
                bal_prev=bal_prev,
                cf_prev=cf_prev,
                is_financial_sector=is_fin,
            )

            # Overall Risk Synthesis for this period
            anomalous_signals = [s for s in granular_signals if s.risk_level in [ForensicRiskLevel.HIGH, ForensicRiskLevel.CRITICAL, ForensicRiskLevel.ELEVATED]]
            moderate_signals = [s for s in granular_signals if s.risk_level == ForensicRiskLevel.MODERATE]

            # Composite stance
            if beneish_res.risk_classification == ForensicRiskLevel.ELEVATED or len(anomalous_signals) >= 2 or altman_res.risk_classification == ForensicRiskLevel.HIGH:
                period_risk = ForensicRiskLevel.ELEVATED
                risk_summary = "Elevated Forensic Scrutiny: Multiple screening anomalies or elevated distress/accrual indicators detected."
            elif len(anomalous_signals) == 1 or len(moderate_signals) >= 2 or piotroski_res.risk_classification == ForensicRiskLevel.HIGH:
                period_risk = ForensicRiskLevel.MODERATE
                risk_summary = "Moderate Watchlist: Selected working capital or margin indicators warrant ongoing review."
            else:
                period_risk = ForensicRiskLevel.LOW
                risk_summary = "Clean Forensic Profile: All primary accounting, accrual, and solvency indicators within safe empirical ranges."

            scorecard = PeriodForensicScorecard(
                period_id=period.id,
                period_label=period.period_label,
                fiscal_year=period.fiscal_year,
                end_date=period.end_date.isoformat() if hasattr(period.end_date, 'isoformat') else str(period.end_date),
                statement_type=str(statement_type),
                overall_risk_level=period_risk,
                risk_summary_text=risk_summary,
                beneish_m_score=beneish_res,
                piotroski_f_score=piotroski_res,
                altman_z_score=altman_res,
                screening_signals=granular_signals,
                anomalous_signals_count=len(anomalous_signals),
                total_signals_evaluated=len(granular_signals),
            )
            scorecards.append(scorecard)

        # Reverse scorecards so newest period is first
        scorecards.reverse()
        latest_scorecard = scorecards[0] if scorecards else None

        overall_stance = (
            latest_scorecard.risk_summary_text
            if latest_scorecard
            else "No financial period data available for forensic screening."
        )

        return CompanyForensicResponse(
            company_id=company.id,
            ticker=company.ticker,
            legal_name=company.legal_name,
            sector=company.sector or "Unclassified",
            industry=company.industry or "Unclassified",
            statement_type=str(statement_type),
            overall_forensic_stance=overall_stance,
            latest_scorecard=latest_scorecard,
            historical_scorecards=scorecards,
            sector_applicability_notes=sector_notes,
            methodology_version=cls.METHODOLOGY_VERSION,
        )
