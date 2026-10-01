"""Pydantic schemas for healthcheck and system status."""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    """Database connection status schema."""
    status: str = Field(..., description="Database health status ('healthy' or 'unhealthy')")
    dialect: str = Field(..., description="Database engine dialect (e.g., sqlite, postgresql)")
    connected: bool = Field(..., description="Whether a connection test succeeded")
    error: Optional[str] = Field(None, description="Error message if connection failed")


class HealthResponse(BaseModel):
    """System health check response schema."""
    status: str = Field("healthy", description="Overall platform health status")
    project_name: str = Field(..., description="Platform application name")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Execution environment")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp of check")
    database: DatabaseHealth = Field(..., description="Database subsystem status")
    system_info: Dict[str, Any] = Field(default_factory=dict, description="Runtime environment telemetry")
