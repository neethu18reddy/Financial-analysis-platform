"""Primary API v1 Router."""

from fastapi import APIRouter
from app.api.v1.endpoints import health, financial_engine, fundamental_analysis, forensic_analysis, valuation, document_intelligence

api_router = APIRouter()

# Register endpoint routers
api_router.include_router(health.router, tags=["Health & System"])
api_router.include_router(financial_engine.router, tags=["Financial Data Engine"])
api_router.include_router(fundamental_analysis.router, tags=["Fundamental Analysis Engine"])
api_router.include_router(forensic_analysis.router, tags=["Forensic Intelligence Engine"])
api_router.include_router(valuation.router, tags=["Valuation Engine"])
api_router.include_router(document_intelligence.router, tags=["Document Intelligence & RAG"])

