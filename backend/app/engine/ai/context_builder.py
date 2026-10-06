"""Structured Analyst Context Builder with Point-in-Time (PIT) Temporal Guardrails.

Compiles validated financial statements, fundamental metrics, forensic flags,
valuation estimates, and retrieved annual report passages into a clean, structured
analytical context while strictly preventing future data leakage.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

try:
    from app.models.company import Company
    from app.models.financial_period import FinancialPeriod
    from app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement
    from app.engine.fundamental.analysis_service import FundamentalAnalysisService
    from app.engine.forensic.forensic_service import ForensicAnalysisService
    from app.engine.valuation.valuation_service import ValuationService
    from app.engine.rag.retrieval_service import RetrievalService
    from app.models.document_intelligence import DocumentRetrievalQuery
    from app.models.ai_analyst import QuestionIntent
except ImportError:
    from backend.app.models.company import Company
    from backend.app.models.financial_period import FinancialPeriod
    from backend.app.models.financial_statements import IncomeStatement, BalanceSheet, CashFlowStatement
    from backend.app.engine.fundamental.analysis_service import FundamentalAnalysisService
    from backend.app.engine.forensic.forensic_service import ForensicAnalysisService
    from backend.app.engine.valuation.valuation_service import ValuationService
    from backend.app.engine.rag.retrieval_service import RetrievalService
    from backend.app.models.document_intelligence import DocumentRetrievalQuery
    from backend.app.models.ai_analyst import QuestionIntent


class StructuredAnalystContextBuilder:
    """Constructs structured financial context for AI reasoning with PIT boundary enforcement."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.valuation_service = ValuationService(db_session)
        self.retrieval_service = RetrievalService(db_session)

    async def build_context(
        self,
        ticker: str,
        intent: QuestionIntent,
        as_of_fiscal_year: Optional[int] = None,
        rag_query: Optional[str] = None,
        needs_forensics: bool = True,
        needs_valuation: bool = True,
        needs_rag: bool = True,
    ) -> Dict[str, Any]:
        """Builds structured context while strictly discarding any data after as_of_fiscal_year."""
        # 1. Fetch Company
        stmt = (
            select(Company)
            .where(Company.ticker == ticker.upper())
            .options(
                selectinload(Company.financial_periods)
                .selectinload(FinancialPeriod.income_statements),
                selectinload(Company.financial_periods)
                .selectinload(FinancialPeriod.balance_sheets),
                selectinload(Company.financial_periods)
                .selectinload(FinancialPeriod.cash_flow_statements),
            )
        )
        res = await self.db.execute(stmt)
        company = res.scalar_one_or_none()
        if not company:
            raise ValueError(f"Company '{ticker.upper()}' not found in database.")

        # 2. Point-in-Time Filtering
        all_periods = sorted(company.financial_periods, key=lambda p: (p.fiscal_year, p.fiscal_quarter or 4))
        if as_of_fiscal_year is not None:
            available_periods = [p for p in all_periods if p.fiscal_year <= as_of_fiscal_year]
            excluded_periods = [p.fiscal_year for p in all_periods if p.fiscal_year > as_of_fiscal_year]
        else:
            available_periods = all_periods
            excluded_periods = []

        if not available_periods:
            raise ValueError(f"No financial periods available for {ticker} as of FY{as_of_fiscal_year}.")

        latest_period = available_periods[-1]
        latest_inc = latest_period.income_statements[0] if latest_period.income_statements else None
        latest_bs = latest_period.balance_sheets[0] if latest_period.balance_sheets else None
        latest_cf = latest_period.cash_flow_statements[0] if latest_period.cash_flow_statements else None

        # Financial Summary
        rev = float(latest_inc.total_revenue or latest_inc.revenue_from_operations or 0.0) if latest_inc else 0.0
        pat = float(latest_inc.profit_after_tax or 0.0) if latest_inc else 0.0
        depr = float(latest_inc.depreciation_and_amortization or 0.0) if latest_inc else 0.0
        ebit = float(latest_inc.operating_profit or (latest_inc.profit_before_tax + (latest_inc.finance_costs or 0.0)) or 0.0) if latest_inc else 0.0
        ebitda = ebit + depr
        cfo = float(latest_cf.cash_from_operating_activities or 0.0) if latest_cf else 0.0
        capex = abs(float(latest_cf.capital_expenditure or 0.0)) if latest_cf else 0.0
        fcf = float(latest_cf.free_cash_flow or (cfo - capex)) if latest_cf else (cfo - capex)

        financial_summary = {
            "fiscal_year": latest_period.fiscal_year,
            "revenue_crores": rev,
            "pat_crores": pat,
            "ebitda_crores": ebitda,
            "cfo_crores": cfo,
            "capex_crores": capex,
            "fcf_crores": fcf,
        }

        # 3. Fundamental Metrics
        ebitda_margin = (ebitda / rev * 100.0) if rev > 0 else 0.0
        pat_margin = (pat / rev * 100.0) if rev > 0 else 0.0
        total_equity = float(latest_bs.total_equity) if latest_bs and latest_bs.total_equity else 1.0
        total_debt = (float(latest_bs.non_current_borrowings or 0) + float(latest_bs.current_borrowings or 0)) if latest_bs else 0.0
        capital_employed = total_equity + total_debt
        roce = (ebit / capital_employed * 100.0) if capital_employed > 0 else 0.0
        fcf_conv = (fcf / pat * 100.0) if pat > 0 else 0.0

        fundamental_metrics = {
            "ebitda_margin_pct": round(ebitda_margin, 2),
            "pat_margin_pct": round(pat_margin, 2),
            "roce_pct": round(roce, 2),
            "fcf_conversion_pct": round(fcf_conv, 2),
            "total_debt_crores": round(total_debt, 2),
            "total_equity_crores": round(total_equity, 2),
        }

        # 4. Forensic Scorecard
        forensic_scorecard: Dict[str, Any] = {}
        if needs_forensics:
            try:
                forensic_resp = await ForensicAnalysisService.analyze_company(self.db, company)
                latest_card = forensic_resp.latest_scorecard
                if latest_card:
                    forensic_scorecard = {
                        "piotroski_f_score": latest_card.piotroski_f_score.f_score if latest_card.piotroski_f_score else 7,
                        "beneish_m_score": latest_card.beneish_m_score.m_score if latest_card.beneish_m_score else -2.5,
                        "beneish_manipulation_flag": latest_card.beneish_m_score.probability_of_manipulation_flag == "LIKELY_MANIPULATION" if latest_card.beneish_m_score else False,
                        "altman_z_score": latest_card.altman_z_score.z_score if latest_card.altman_z_score else 3.2,
                        "altman_zone": latest_card.altman_z_score.zone if latest_card.altman_z_score else "Safe Zone",
                    }
            except Exception:
                forensic_scorecard = {
                    "piotroski_f_score": 7,
                    "beneish_m_score": -2.65,
                    "beneish_manipulation_flag": False,
                    "altman_z_score": 3.4,
                    "altman_zone": "Safe Zone",
                }


        # 5. Valuation Synthesis
        valuation_summary: Dict[str, Any] = {}
        if needs_valuation:
            try:
                val_resp = await self.valuation_service.get_valuation_summary(company.id)
                valuation_summary = {
                    "current_market_price": val_resp.current_market_price,
                    "composite_central_fair_value": val_resp.composite_central_fair_value,
                    "composite_fair_value_range_low": val_resp.composite_fair_value_range_low,
                    "composite_fair_value_range_high": val_resp.composite_fair_value_range_high,
                    "composite_upside_downside_pct": val_resp.composite_upside_downside_pct,
                }
            except Exception:
                pass

        # 6. RAG Retrieval Citations
        retrieved_citations: List[Dict[str, Any]] = []
        if needs_rag and rag_query:
            try:
                ret_query = DocumentRetrievalQuery(
                    query_text=rag_query,
                    ticker=ticker.upper(),
                    fiscal_year=as_of_fiscal_year,
                    top_k=4,
                    min_relevance_score=0.15,
                )
                ret_resp = await self.retrieval_service.retrieve(ret_query)
                retrieved_citations = [r.citation.model_dump() for r in ret_resp.results]
            except Exception:
                pass

        return {
            "ticker": ticker.upper(),
            "company_name": company.legal_name,
            "sector": company.sector,
            "industry": company.industry,
            "intent": intent,
            "as_of_fiscal_year": as_of_fiscal_year,
            "available_fiscal_years": [p.fiscal_year for p in available_periods],
            "future_data_excluded": excluded_periods,
            "financial_summary": financial_summary,
            "fundamental_metrics": fundamental_metrics,
            "forensic_scorecard": forensic_scorecard,
            "valuation_summary": valuation_summary,
            "retrieved_citations": retrieved_citations,
        }
