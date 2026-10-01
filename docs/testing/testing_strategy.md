# Testing Strategy and Verification Protocols

## Overview
Quality and accuracy are non-negotiable in financial computing. The platform enforces multi-level automated testing.

## Test Pyramid

1. **Unit Tests (Backend & Math)**:
   - Verification of individual formula routines against verified benchmark filings.
   - Pydantic schema validation for incoming and outgoing payloads.
   - Configuration and environment parsing.

2. **Integration Tests (API & Database)**:
   - Database connection pool lifecycle and query execution.
   - FastAPI route handler integration using `httpx.AsyncClient`.
   - Error middleware handling for 404, 422, and 500 scenarios.

3. **Frontend Compile & Typecheck**:
   - Strict TypeScript compiler check (`tsc -b`).
   - Production bundle assembly via Vite (`vite build`).

## Running Tests

### Automated Multi-Tier Test Suite
```bash
.venv\Scripts\python scripts/run_all_tests.py
```

### Pytest Specific Backend Run
```bash
.venv\Scripts\pytest tests/backend -v --tb=short
```

### Frontend Typecheck & Build Run
```bash
cd frontend
npm run build
```
