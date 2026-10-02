"""Primary API v1 Router."""

from fastapi import APIRouter
from app.api.v1.endpoints import health, financial_engine

api_router = APIRouter()

# Register endpoint routers
api_router.include_router(health.router, tags=["Health & System"])
api_router.include_router(financial_engine.router, tags=["Financial Data Engine"])
