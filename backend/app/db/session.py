"""Database engine and session management with async connectivity check."""

from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
try:
    from backend.app.core.config import settings
    from backend.app.core.logging import logger
except ImportError:
    from app.core.config import settings
    from app.core.logging import logger

# Create async database engine
# SQLite requires check_same_thread=False for async connection pools
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    connect_args=connect_args,
    future=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining database sessions in FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_connectivity() -> Dict[str, Any]:
    """Tests active database connectivity and returns connection health details."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            scalar_res = result.scalar()
            is_healthy = scalar_res == 1
            dialect_name = engine.dialect.name
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "dialect": dialect_name,
                "connected": is_healthy,
                "error": None,
            }
    except Exception as e:
        logger.error(f"Database connectivity check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "dialect": engine.dialect.name if hasattr(engine, "dialect") else "unknown",
            "connected": False,
            "error": str(e),
        }
