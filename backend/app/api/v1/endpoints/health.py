"""Health check endpoint router."""

import platform
import sys
from datetime import datetime
from fastapi import APIRouter, status
try:
    from backend.app.core.config import settings
    from backend.app.db.session import check_database_connectivity
    from backend.app.schemas.health import HealthResponse, DatabaseHealth
except ImportError:
    from app.core.config import settings
    from app.db.session import check_database_connectivity
    from app.schemas.health import HealthResponse, DatabaseHealth

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System and subsystem health check",
    description="Returns real-time health and connectivity status of application and database.",
)
async def get_health() -> HealthResponse:
    """Performs deep health check across platform services."""
    db_health_data = await check_database_connectivity()

    overall_status = "healthy" if db_health_data.get("connected") else "degraded"

    return HealthResponse(
        status=overall_status,
        project_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.utcnow(),
        database=DatabaseHealth(
            status=db_health_data.get("status", "unknown"),
            dialect=db_health_data.get("dialect", "unknown"),
            connected=db_health_data.get("connected", False),
            error=db_health_data.get("error"),
        ),
        system_info={
            "python_version": sys.version.split()[0],
            "os": platform.system(),
            "os_release": platform.release(),
            "debug": settings.DEBUG,
        },
    )
