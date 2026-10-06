"""Valuation API Endpoints.

Provides deterministic endpoints for:
- Full Company Valuation Summary & Synthesis
- Custom DCF (FCFF) modeling
- Reverse DCF Market Expectation Solver
- Multiples & Relative Valuation
- Bear / Base / Bull Scenario Analysis
- 2D Sensitivity Matrices (WACC vs Terminal Growth, Growth vs Margin)
- Bank & NBFC DDM / Justified P/B
- Conglomerate SOTP (Sum-of-the-Parts)
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from app.db.session import get_db
    from app.models.valuation import (
        ValuationSummaryResponse,
        DCFValuationInputs,
        DCFValuationResult,
        ReverseDCFInputs,
        ReverseDCFResult,
        MultiplesValuationResult,
        ScenarioAnalysisResult,
        SensitivityMatrixResult,
        BankValuationResult,
        SOTPSegment,
        SOTPValuationResult,
    )
    from app.engine.valuation.valuation_service import ValuationService
    from app.engine.valuation.dcf import DCFValuationEngine
    from app.engine.valuation.reverse_dcf import ReverseDCFEngine
    from app.engine.valuation.multiples import MultiplesValuationEngine
    from app.engine.valuation.scenarios import ScenarioValuationEngine
    from app.engine.valuation.sensitivity import SensitivityValuationEngine
    from app.engine.valuation.financial_institutions import BankValuationEngine
    from app.engine.valuation.sotp import SOTPValuationEngine
except ImportError:
    from backend.app.db.session import get_db
    from backend.app.models.valuation import (
        ValuationSummaryResponse,
        DCFValuationInputs,
        DCFValuationResult,
        ReverseDCFInputs,
        ReverseDCFResult,
        MultiplesValuationResult,
        ScenarioAnalysisResult,
        SensitivityMatrixResult,
        BankValuationResult,
        SOTPSegment,
        SOTPValuationResult,
    )
    from backend.app.engine.valuation.valuation_service import ValuationService
    from backend.app.engine.valuation.dcf import DCFValuationEngine
    from backend.app.engine.valuation.reverse_dcf import ReverseDCFEngine
    from backend.app.engine.valuation.multiples import MultiplesValuationEngine
    from backend.app.engine.valuation.scenarios import ScenarioValuationEngine
    from backend.app.engine.valuation.sensitivity import SensitivityValuationEngine
    from backend.app.engine.valuation.financial_institutions import BankValuationEngine
    from backend.app.engine.valuation.sotp import SOTPValuationEngine

router = APIRouter(prefix="/companies/{company_id}/valuation", tags=["Valuation Engine"])


@router.get("/summary", response_model=ValuationSummaryResponse)
async def get_valuation_summary(
    company_id: int,
    market_price: Optional[float] = Query(None, description="Optional custom market price override"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves full institutional valuation report combining DCF, Reverse DCF, Multiples, and Scenarios."""
    service = ValuationService(db)
    try:
        return await service.get_valuation_summary(company_id=company_id, custom_price=market_price)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Valuation calculation failed: {str(e)}")


@router.post("/dcf", response_model=DCFValuationResult)
async def run_custom_dcf(
    company_id: int,
    inputs: DCFValuationInputs,
    market_price: Optional[float] = Query(None, description="Current market price for upside calculation"),
    db: AsyncSession = Depends(get_db),
):
    """Executes deterministic DCF valuation with custom assumption inputs."""
    service = ValuationService(db)
    summary = await service.get_valuation_summary(company_id=company_id, custom_price=market_price)
    
    # Fill defaults from company financial data if not supplied
    if inputs.base_revenue is None or inputs.base_revenue <= 0:
        inputs.base_revenue = summary.dcf_result.inputs_applied.base_revenue if summary.dcf_result else 50000.0
    if inputs.shares_outstanding_crores is None or inputs.shares_outstanding_crores <= 0:
        inputs.shares_outstanding_crores = summary.shares_outstanding_crores
    if inputs.total_debt_crores is None:
        inputs.total_debt_crores = summary.dcf_result.total_debt if summary.dcf_result else 0.0
    if inputs.cash_and_investments_crores is None:
        inputs.cash_and_investments_crores = summary.dcf_result.cash_and_investments if summary.dcf_result else 0.0

    dcf_engine = DCFValuationEngine()
    return dcf_engine.calculate(
        company_id=company_id,
        ticker=summary.ticker,
        inputs=inputs,
        current_market_price=market_price or summary.current_market_price,
    )


@router.post("/reverse-dcf", response_model=ReverseDCFResult)
async def run_reverse_dcf_solver(
    company_id: int,
    inputs: ReverseDCFInputs,
    db: AsyncSession = Depends(get_db),
):
    """Solves for implied revenue growth, margins, and FCF embedded in current market price."""
    service = ValuationService(db)
    summary = await service.get_valuation_summary(company_id=company_id, custom_price=inputs.current_market_price)
    
    base_rev = summary.dcf_result.inputs_applied.base_revenue if summary.dcf_result else 50000.0
    shares = inputs.shares_outstanding_crores or summary.shares_outstanding_crores
    
    rev_engine = ReverseDCFEngine()
    return rev_engine.calculate(
        company_id=company_id,
        ticker=summary.ticker,
        inputs=inputs,
        base_revenue=base_rev,
        historical_revenue_cagr_3yr=summary.reverse_dcf_result.historical_revenue_cagr_3yr if summary.reverse_dcf_result else None,
        default_shares=shares,
        default_debt=summary.dcf_result.total_debt if summary.dcf_result else 0.0,
        default_cash=summary.dcf_result.cash_and_investments if summary.dcf_result else 0.0,
    )


@router.get("/multiples", response_model=MultiplesValuationResult)
async def get_multiples_valuation(
    company_id: int,
    market_price: Optional[float] = Query(None, description="Current market price"),
    target_pe: Optional[float] = Query(None, description="Custom target P/E"),
    target_ev_ebitda: Optional[float] = Query(None, description="Custom target EV/EBITDA"),
    target_pb: Optional[float] = Query(None, description="Custom target P/B"),
    db: AsyncSession = Depends(get_db),
):
    """Calculates relative multiples (P/E, EV/EBITDA, P/B, EV/Sales) benchmarked against historical percentiles."""
    service = ValuationService(db)
    summary = await service.get_valuation_summary(company_id=company_id, custom_price=market_price)
    if not summary.multiples_result:
        raise HTTPException(status_code=400, detail="Multiples not available for company.")
    
    # If custom targets are supplied, re-evaluate
    if any([target_pe, target_ev_ebitda, target_pb]):
        multiples_engine = MultiplesValuationEngine()
        mult = summary.multiples_result
        return multiples_engine.calculate(
            company_id=company_id,
            ticker=summary.ticker,
            current_market_price=market_price or summary.current_market_price,
            eps=mult.multiples[0].underlying_financial_metric,
            book_value_per_share=mult.multiples[2].underlying_financial_metric,
            ebitda_per_share=mult.multiples[1].underlying_financial_metric,
            revenue_per_share=mult.multiples[3].underlying_financial_metric,
            custom_target_pe=target_pe,
            custom_target_ev_ebitda=target_ev_ebitda,
            custom_target_pb=target_pb,
        )
    return summary.multiples_result


@router.post("/scenarios", response_model=ScenarioAnalysisResult)
async def run_scenario_analysis(
    company_id: int,
    market_price: Optional[float] = Query(None),
    base_growth_pct: float = Query(11.5),
    base_margin_pct: float = Query(18.0),
    base_wacc_pct: float = Query(11.2),
    base_terminal_growth_pct: float = Query(5.0),
    db: AsyncSession = Depends(get_db),
):
    """Evaluates Bear, Base, and Bull valuation scenarios with explicit probability weighting."""
    service = ValuationService(db)
    summary = await service.get_valuation_summary(company_id=company_id, custom_price=market_price)
    
    base_rev = summary.dcf_result.inputs_applied.base_revenue if summary.dcf_result else 50000.0
    shares = summary.shares_outstanding_crores
    debt = summary.dcf_result.total_debt if summary.dcf_result else 0.0
    cash = summary.dcf_result.cash_and_investments if summary.dcf_result else 0.0
    
    scenario_engine = ScenarioValuationEngine()
    return scenario_engine.calculate(
        company_id=company_id,
        ticker=summary.ticker,
        current_market_price=market_price or summary.current_market_price,
        base_revenue=base_rev,
        shares_outstanding_crores=shares,
        total_debt_crores=debt,
        cash_and_investments_crores=cash,
        base_growth_pct=base_growth_pct,
        base_margin_pct=base_margin_pct,
        base_wacc_pct=base_wacc_pct,
        base_terminal_growth_pct=base_terminal_growth_pct,
    )


@router.post("/sensitivity/wacc-terminal-growth", response_model=SensitivityMatrixResult)
async def get_wacc_vs_terminal_growth_sensitivity(
    company_id: int,
    base_wacc_pct: float = Query(11.2),
    base_terminal_growth_pct: float = Query(5.0),
    base_growth_pct: float = Query(11.5),
    base_margin_pct: float = Query(18.0),
    market_price: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Generates 2D sensitivity matrix of Discount Rate (WACC) vs Terminal Growth Rate."""
    service = ValuationService(db)
    summary = await service.get_valuation_summary(company_id=company_id, custom_price=market_price)
    
    base_rev = summary.dcf_result.inputs_applied.base_revenue if summary.dcf_result else 50000.0
    shares = summary.shares_outstanding_crores
    debt = summary.dcf_result.total_debt if summary.dcf_result else 0.0
    cash = summary.dcf_result.cash_and_investments if summary.dcf_result else 0.0
    
    sens_engine = SensitivityValuationEngine()
    return sens_engine.build_wacc_vs_terminal_growth_matrix(
        company_id=company_id,
        ticker=summary.ticker,
        current_market_price=market_price or summary.current_market_price,
        base_revenue=base_rev,
        shares_outstanding_crores=shares,
        total_debt_crores=debt,
        cash_and_investments_crores=cash,
        base_wacc_pct=base_wacc_pct,
        base_terminal_growth_pct=base_terminal_growth_pct,
        base_growth_pct=base_growth_pct,
        base_margin_pct=base_margin_pct,
    )


@router.post("/sensitivity/growth-margin", response_model=SensitivityMatrixResult)
async def get_growth_vs_margin_sensitivity(
    company_id: int,
    base_growth_pct: float = Query(11.5),
    base_margin_pct: float = Query(18.0),
    base_wacc_pct: float = Query(11.2),
    base_terminal_growth_pct: float = Query(5.0),
    market_price: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Generates 2D sensitivity matrix of Revenue Growth CAGR vs EBIT Operating Margin."""
    service = ValuationService(db)
    summary = await service.get_valuation_summary(company_id=company_id, custom_price=market_price)
    
    base_rev = summary.dcf_result.inputs_applied.base_revenue if summary.dcf_result else 50000.0
    shares = summary.shares_outstanding_crores
    debt = summary.dcf_result.total_debt if summary.dcf_result else 0.0
    cash = summary.dcf_result.cash_and_investments if summary.dcf_result else 0.0
    
    sens_engine = SensitivityValuationEngine()
    return sens_engine.build_growth_vs_margin_matrix(
        company_id=company_id,
        ticker=summary.ticker,
        current_market_price=market_price or summary.current_market_price,
        base_revenue=base_rev,
        shares_outstanding_crores=shares,
        total_debt_crores=debt,
        cash_and_investments_crores=cash,
        base_growth_pct=base_growth_pct,
        base_margin_pct=base_margin_pct,
        base_wacc_pct=base_wacc_pct,
        base_terminal_growth_pct=base_terminal_growth_pct,
    )


@router.get("/financial-institution", response_model=BankValuationResult)
async def get_bank_valuation(
    company_id: int,
    market_price: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Executes Dividend Discount Model (DDM) & Justified P/B for Banks and NBFCs."""
    service = ValuationService(db)
    summary = await service.get_valuation_summary(company_id=company_id, custom_price=market_price)
    if summary.bank_valuation_result:
        return summary.bank_valuation_result
    
    # If called on non-bank, run DDM using company's ROE & Book value as specialized benchmark
    bank_engine = BankValuationEngine()
    bvps = summary.multiples_result.multiples[2].underlying_financial_metric if summary.multiples_result else 500.0
    return bank_engine.calculate(
        company_id=company_id,
        ticker=summary.ticker,
        sector=summary.sector,
        current_market_price=market_price or summary.current_market_price,
        book_value_per_share=bvps,
        current_roe_pct=18.0,
        shares_outstanding_crores=summary.shares_outstanding_crores,
    )


@router.post("/sotp", response_model=SOTPValuationResult)
async def run_sotp_valuation(
    company_id: int,
    segments: List[SOTPSegment],
    net_debt_crores: float = Query(0.0),
    holding_company_discount_pct: float = Query(15.0),
    market_price: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Executes Sum-of-the-Parts (SOTP) multi-segment valuation."""
    service = ValuationService(db)
    summary = await service.get_valuation_summary(company_id=company_id, custom_price=market_price)
    
    sotp_engine = SOTPValuationEngine()
    return sotp_engine.calculate(
        company_id=company_id,
        ticker=summary.ticker,
        segments=segments,
        net_debt_crores=net_debt_crores,
        shares_outstanding_crores=summary.shares_outstanding_crores,
        holding_company_discount_pct=holding_company_discount_pct,
        current_market_price=market_price or summary.current_market_price,
    )
