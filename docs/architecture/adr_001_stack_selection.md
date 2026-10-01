# ADR 001: Technology Stack and Architectural Foundations

## Status
Accepted

## Context
Building an institutional-grade fundamental analysis and forensic intelligence platform for publicly listed Indian equities requires:
1. High-precision numerical computing and deterministic mathematical calculations.
2. Robust async API capabilities for data ingestion and high concurrency.
3. Strict database migration management and ORM modeling.
4. Fast, responsive, and type-safe front-end user experience.
5. Strict local environment compatibility without imposing uninstalled external dependencies (e.g. Docker/native psql daemon not present in the local Windows environment).

## Decision

### 1. Backend: FastAPI (Python 3.14)
- **Rationale**: Python is the standard for financial engineering, data science, and XBRL parsing. FastAPI offers high-performance ASGI async execution, native Pydantic v2 data validation, and automated OpenAPI documentation.
- **Alternatives Considered**: Flask (lacks native async ASGI and modern type validation), Django (excessive monolith overhead for decoupled architecture).

### 2. Database & Migration Layer: SQLAlchemy 2.0 (Async) + Alembic
- **Rationale**: SQLAlchemy 2.0 provides an asynchronous ORM interface and SQL expression engine. It supports PostgreSQL as the primary target in containerized/production environments while cleanly supporting SQLite with `aiosqlite` for local zero-dependency developer agility.
- **Alembic**: Provides version-controlled, reproducible schema migrations across both dialects.

### 3. Frontend: React 18 + TypeScript + Vite
- **Rationale**: React with TypeScript guarantees strict type-safety matching backend Pydantic models. Vite provides instantaneous Hot Module Replacement (HMR) and optimized rollup production bundles.
- **Alternatives Considered**: Next.js (unnecessary server-side complexity for internal research workstations), Angular (unnecessary boilerplate).

### 4. Testing Framework: Pytest + Asyncio + HTTPX
- **Rationale**: Pytest is the industry benchmark for Python testing, with native async test fixture support and fast execution times.

## Consequences
- The system achieves clear architectural separation between backend, frontend, database, and documentation.
- Local developer setup requires zero external daemon installs while remaining 100% production-ready for PostgreSQL deployment.
