"""AI Analyst, Historical Validation, and Research Product Engine Package."""

from app.engine.ai.base import (
    AI_METHODOLOGY_VERSION,
    BaseLLMProvider,
)
from app.engine.ai.llm_provider import (
    DeterministicFinancialLLMProvider,
    PluggableExternalLLMProvider,
    get_default_llm_provider,
)
from app.engine.ai.question_router import FinancialQuestionRouter
from app.engine.ai.context_builder import StructuredAnalystContextBuilder
from app.engine.ai.citation_validator import CitationAndClaimValidator
from app.engine.ai.said_vs_did_engine import SaidVsDidEngine
from app.engine.ai.watchlist_engine import WatchlistEngine
from app.engine.ai.research_report_generator import CompanyResearchReportGenerator
from app.engine.ai.ai_analyst_service import AIAnalystService

__all__ = [
    "AI_METHODOLOGY_VERSION",
    "BaseLLMProvider",
    "DeterministicFinancialLLMProvider",
    "PluggableExternalLLMProvider",
    "get_default_llm_provider",
    "FinancialQuestionRouter",
    "StructuredAnalystContextBuilder",
    "CitationAndClaimValidator",
    "SaidVsDidEngine",
    "WatchlistEngine",
    "CompanyResearchReportGenerator",
    "AIAnalystService",
]
