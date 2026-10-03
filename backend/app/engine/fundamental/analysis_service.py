"""Fundamental Analysis Orchestration Service.

Coordinates:
- ProfitabilityEngine (Margins, ROE, ROCE, ROIC, ROA)
- GrowthEngine (YoY growth rates, Multi-year CAGRs)
- WorkingCapitalEngine (DSO, DIO, DPO, CCC, Asset Turnover, Liquidity)
- CashQualityEngine (CFO/PAT, FCF/PAT, Sloan Accruals, Coverage)
- DuPontEngine (3-step and 5-step DuPont decomposition)
- CommonSizeEngine (Vertical % common-size statements)
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.company import Company
from app.models.financial_period import FinancialPeriod
from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement, StatementType
from app.engine.fundamental.profitability import ProfitabilityEngine, CalculatedMetric
from app.engine.fundamental.growth import GrowthEngine
from app.engine.fundamental.working_capital import WorkingCapitalEngine
from app.engine.fundamental.cash_quality import CashQualityEngine
from app.engine.fundamental.dupont import DuPontEngine, DuPontDecompositionResult
from app.engine.fundamental.common_size import CommonSizeEngine, CommonSizeIncomeStatement, CommonSizeBalanceSheet


class PeriodFundamentalAnalysis(BaseModel):
    """Complete fundamental metrics package for a single financial period."""
    period_id: int
    period_label: str
    fiscal_year: int
    end_date: str
    statement_type: str
    
    profitability: Dict[str, CalculatedMetric]
    growth: Dict[str, CalculatedMetric]
    working_capital: Dict[str, CalculatedMetric]
    cash_quality: Dict[str, CalculatedMetric]
    dupont: Optional[DuPontDecompositionResult] = None
    common_size_income: Optional[CommonSizeIncomeStatement] = None
    common_size_balance: Optional[CommonSizeBalanceSheet] = None


class MultiPeriodCAGRSummary(BaseModel):
    """Multi-year compound annual growth rates across available periods."""
    num_years: int
    base_period_label: str
    latest_period_label: str
    revenue_cagr: Optional[float] = None
    ebitda_cagr: Optional[float] = None
    ebit_cagr: Optional[float] = None
    pat_cagr: Optional[float] = None
    cfo_cagr: Optional[float] = None


class FundamentalAnalysisResponse(BaseModel):
    """Full company fundamental analysis response with historical periods and CAGRs."""
    company_id: int
    ticker: str
    legal_name: str
    sector: str
    statement_type: str
    methodology_version: str = "v1.0.0"
    periods_analysis: List[PeriodFundamentalAnalysis]
    cagr_summary: Optional[MultiPeriodCAGRSummary] = None


class FundamentalAnalysisService:
    """Service generating comprehensive fundamental financial metrics."""

    METHODOLOGY_VERSION = "v1.0.0"

    @classmethod
    async def analyze_company(
        cls,
        db: AsyncSession,
        company: Company,
        statement_type: StatementType = StatementType.CONSOLIDATED,
        limit_periods: int = 5
    ) -> FundamentalAnalysisResponse:
        """Run full fundamental analysis suite across chronological periods for a company."""
        # 1. Fetch periods sorted oldest -> newest for growth calculations
        p_stmt = (
            select(FinancialPeriod)
            .where(FinancialPeriod.company_id == company.id)
            .order_by(FinancialPeriod.end_date.asc())
            .limit(limit_periods)
        )
        p_res = await db.execute(p_stmt)
        periods = p_res.scalars().all()

        period_data_list = []
        raw_period_snapshots = []

        # 2. Fetch statements for each period
        for period in periods:
            # Income Statement
            is_stmt = select(IncomeStatement).where(
                IncomeStatement.period_id == period.id,
                IncomeStatement.statement_type == statement_type
            )
            is_res = await db.execute(is_stmt)
            inc = is_res.scalar_one_or_none()

            # Balance Sheet
            bs_stmt = select(BalanceSheet).where(
                BalanceSheet.period_id == period.id,
                BalanceSheet.statement_type == statement_type
            )
            bs_res = await db.execute(bs_stmt)
            bs = bs_res.scalar_one_or_none()

            # Cash Flow
            cf_stmt = select(CashFlowStatement).where(
                CashFlowStatement.period_id == period.id,
                CashFlowStatement.statement_type == statement_type
            )
            cf_res = await db.execute(cf_stmt)
            cf = cf_res.scalar_one_or_none()

            raw_period_snapshots.append({
                "period": period,
                "income": inc,
                "balance": bs,
                "cash_flow": cf,
                "summary": {
                    "total_revenue": inc.total_revenue if inc else None,
                    "ebitda": (
                        (inc.profit_before_tax or 0.0) + (inc.finance_costs or 0.0) + (inc.depreciation_and_amortization or 0.0) - (inc.exceptional_items or 0.0)
                    ) if inc else None,
                    "ebit": ((inc.profit_before_tax or 0.0) + (inc.finance_costs or 0.0)) if inc else None,
                    "net_profit": (inc.net_profit_attributable_to_owners or inc.profit_after_tax) if inc else None,
                    "cfo": cf.cash_from_operating_activities if cf else None,
                    "fcf": cf.free_cash_flow if cf else None,
                }
            })

        # 3. Calculate metrics per period
        for i, snap in enumerate(raw_period_snapshots):
            period = snap["period"]
            inc = snap["income"]
            bs = snap["balance"]
            cf = snap["cash_flow"]

            # Profitability
            prof_metrics = ProfitabilityEngine.calculate_all(inc, bs, cf)

            # Growth (comparing with previous period if available)
            prev_snap = raw_period_snapshots[i - 1]["summary"] if i > 0 else None
            growth_metrics = GrowthEngine.calculate_period_growth(snap["summary"], prev_snap)

            # Working Capital
            wc_metrics = WorkingCapitalEngine.calculate_all(inc, bs)

            # Cash Quality
            cq_metrics = CashQualityEngine.calculate_all(inc, bs, cf)

            # DuPont
            dupont_res = DuPontEngine.calculate(inc, bs)

            # Common-Size Statements
            cs_inc = CommonSizeEngine.calculate_income_statement(inc)
            cs_bs = CommonSizeEngine.calculate_balance_sheet(bs)

            period_data_list.append(PeriodFundamentalAnalysis(
                period_id=period.id,
                period_label=period.period_label,
                fiscal_year=period.fiscal_year,
                end_date=str(period.end_date),
                statement_type=str(statement_type),
                profitability=prof_metrics,
                growth=growth_metrics,
                working_capital=wc_metrics,
                cash_quality=cq_metrics,
                dupont=dupont_res,
                common_size_income=cs_inc,
                common_size_balance=cs_bs
            ))

        # 4. Calculate Multi-Year CAGR if >= 2 periods exist
        cagr_summary = None
        if len(raw_period_snapshots) >= 2:
            base_s = raw_period_snapshots[0]
            latest_s = raw_period_snapshots[-1]
            n_years = len(raw_period_snapshots) - 1

            cagr_summary = MultiPeriodCAGRSummary(
                num_years=n_years,
                base_period_label=base_s["period"].period_label,
                latest_period_label=latest_s["period"].period_label,
                revenue_cagr=GrowthEngine.calculate_cagr(latest_s["summary"]["total_revenue"], base_s["summary"]["total_revenue"], n_years),
                ebitda_cagr=GrowthEngine.calculate_cagr(latest_s["summary"]["ebitda"], base_s["summary"]["ebitda"], n_years),
                ebit_cagr=GrowthEngine.calculate_cagr(latest_s["summary"]["ebit"], base_s["summary"]["ebit"], n_years),
                pat_cagr=GrowthEngine.calculate_cagr(latest_s["summary"]["net_profit"], base_s["summary"]["net_profit"], n_years),
                cfo_cagr=GrowthEngine.calculate_cagr(latest_s["summary"]["cfo"], base_s["summary"]["cfo"], n_years),
            )

        # Present periods newest-first for standard institutional reporting
        period_data_list_reversed = list(reversed(period_data_list))

        return FundamentalAnalysisResponse(
            company_id=company.id,
            ticker=company.ticker,
            legal_name=company.legal_name,
            sector=company.sector,
            statement_type=str(statement_type),
            methodology_version=cls.METHODOLOGY_VERSION,
            periods_analysis=period_data_list_reversed,
            cagr_summary=cagr_summary
        )
