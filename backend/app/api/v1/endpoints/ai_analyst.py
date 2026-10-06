"""AI Analyst and Research Product FastAPI Endpoints.

Provides endpoints for:
- Conversational financial research with verifiable claims and citations
- Management 'Said vs Did' historical commitment tracking
- Point-in-Time historical simulation with zero future leakage
- End-to-end institutional Company Research Reports
- Real-time stock watchlist management and anomaly alert screening
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from app.db.session import get_db
    from app.models.ai_analyst import (
        AIAnalystQuery,
        AIAnalystResponse,
        ManagementSaidVsDidResponse,
        PointInTimeAnalysisRequest,
        PointInTimeAnalysisResponse,
        CompanyResearchReport,
        WatchlistItemDTO,
    )
    from app.engine.ai.ai_analyst_service import AIAnalystService
    from app.engine.ai.said_vs_did_engine import SaidVsDidEngine
    from app.engine.ai.watchlist_engine import WatchlistEngine
    from app.engine.ai.research_report_generator import CompanyResearchReportGenerator
except ImportError:
    from backend.app.db.session import get_db
    from backend.app.models.ai_analyst import (
        AIAnalystQuery,
        AIAnalystResponse,
        ManagementSaidVsDidResponse,
        PointInTimeAnalysisRequest,
        PointInTimeAnalysisResponse,
        CompanyResearchReport,
        WatchlistItemDTO,
    )
    from backend.app.engine.ai.ai_analyst_service import AIAnalystService
    from backend.app.engine.ai.said_vs_did_engine import SaidVsDidEngine
    from backend.app.engine.ai.watchlist_engine import WatchlistEngine
    from backend.app.engine.ai.research_report_generator import CompanyResearchReportGenerator

router = APIRouter(prefix="/ai", tags=["AI Analyst & Research Product"])


@router.post("/query", response_model=AIAnalystResponse)
async def query_ai_analyst(
    query: AIAnalystQuery,
    db: AsyncSession = Depends(get_db),
):
    """Submits natural language financial inquiry to the cited AI Analyst pipeline."""
    service = AIAnalystService(db)
    try:
        return await service.query_analyst(query)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI analysis failed: {str(e)}")


@router.get("/said-vs-did/{ticker}", response_model=ManagementSaidVsDidResponse)
async def get_said_vs_did(
    ticker: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves management forward guidance vs actual historical outturn scorecard."""
    engine = SaidVsDidEngine(db)
    return await engine.get_said_vs_did(ticker=ticker.upper())


@router.post("/point-in-time", response_model=PointInTimeAnalysisResponse)
async def run_point_in_time_simulation(
    request: PointInTimeAnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """Executes historical simulation strictly bounded by historical cut-off date to prevent future leakage."""
    service = AIAnalystService(db)
    try:
        return await service.run_point_in_time_simulation(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/research-report/{company_id}", response_model=CompanyResearchReport)
async def get_company_research_report(
    company_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Generates complete institutional-grade company research report across all analytical dimensions."""
    generator = CompanyResearchReportGenerator(db)
    try:
        return await generator.generate_report(company_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# Watchlist Endpoints
# ---------------------------------------------------------------------------

watchlist_router = APIRouter(prefix="/watchlist", tags=["Watchlist & Alert Engine"])


@watchlist_router.get("", response_model=List[WatchlistItemDTO])
async def list_watchlist_items(
    db: AsyncSession = Depends(get_db),
):
    """Lists user monitored equities with live metric anomaly alerts."""
    engine = WatchlistEngine(db)
    return await engine.list_watchlist()


@watchlist_router.post("", response_model=WatchlistItemDTO)
async def add_watchlist_item(
    ticker: str = Query(..., description="Company ticker to monitor"),
    notes: Optional[str] = Query(None, description="Optional research note"),
    db: AsyncSession = Depends(get_db),
):
    """Adds a company to the active monitoring watchlist."""
    engine = WatchlistEngine(db)
    return await engine.add_to_watchlist(ticker=ticker, notes=notes)


@watchlist_router.delete("/{ticker}", response_model=dict)
async def remove_watchlist_item(
    ticker: str,
    db: AsyncSession = Depends(get_db),
):
    """Removes a company from the active watchlist."""
    engine = WatchlistEngine(db)
    success = await engine.remove_from_watchlist(ticker)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticker {ticker} not found in watchlist.")
    return {"success": True, "ticker": ticker.upper(), "message": "Removed from watchlist."}
