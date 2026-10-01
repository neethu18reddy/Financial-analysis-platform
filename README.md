# AI-Powered Fundamental Analysis and Financial Decision Intelligence Platform

> **Indian Listed Equities (NSE & BSE) · Institutional Grade Fundamental Research & Forensic Intelligence**

---

## 🏛️ Core Architectural Law

```
DATA ──> VALIDATION ──> CALCULATIONS ──> ANALYTICS ──> EVIDENCE ──> AI EXPLANATION
```

> **CRITICAL RULE**: The Large Language Model (LLM) is **NOT** the source of truth for financial data or deterministic financial calculations. All ratios, metrics, valuations, and forensic scores are computed purely in deterministic, verifiable Python code with strict mathematical rigor. The AI is restricted solely to explaining verified facts, synthesizing evidence, and assisting user inquiries based strictly on cited financial disclosures.

---

## 🚀 Current Status: Phase 0 (Foundation & Architecture)

| Component | Status | Details |
| :--- | :--- | :--- |
| **Backend Engine** | ✅ Operational | FastAPI, Python 3.14, Async ASGI, Pydantic v2 |
| **Database Subsystem** | ✅ Operational | SQLAlchemy 2.0 Async Engine, Alembic Migrations |
| **Frontend Shell** | ✅ Operational | React 18, TypeScript, Vite, Dark-Mode Institutional Layout |
| **Testing Infrastructure**| ✅ Operational | Pytest, Asyncio runner, Frontend build validation (100% Pass) |
| **Documentation Suite** | ✅ Complete | Architecture, Data Sources, Methodology, Compliance, Journal |
| **Future Phases (1-3)** | 🔒 Locked | Documented only; awaiting explicit approval |

---

## 📁 Repository Structure

```
├── backend/
│   ├── alembic/                # Database migration scripts and environment
│   ├── alembic.ini             # Alembic configuration
│   ├── app/
│   │   ├── api/v1/             # API version 1 routers and endpoints
│   │   │   └── endpoints/
│   │   │       └── health.py   # System & subsystem healthcheck endpoint
│   │   ├── core/               # Configuration (Pydantic Settings) and logging
│   │   ├── db/                 # Database engine, session manager, Declarative Base
│   │   ├── schemas/            # Pydantic data schemas
│   │   └── main.py             # FastAPI entrypoint, middleware, error handlers
│   ├── requirements.txt        # Production dependencies
│   └── requirements-dev.txt    # Testing & dev dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/         # Layout & Reusable UI elements (Card, Badge, Alert, Spinner)
│   │   ├── services/           # Typed API service client
│   │   ├── types/              # TypeScript interface definitions
│   │   ├── views/              # Foundation views (Health, Architecture, Data Pipeline)
│   │   ├── App.tsx             # Root React application
│   │   └── main.tsx            # React DOM mounting
│   ├── package.json            # Node.js dependencies
│   └── vite.config.ts          # Vite configuration with API proxying
│
├── tests/
│   └── backend/                # Pytest suites for config, database, health, errors
│
├── docs/
│   ├── architecture/           # Architecture overview & Architectural Decision Records (ADRs)
│   ├── data-sources/           # Ingestion strategies for NSE, BSE, XBRL, annual reports
│   ├── methodology/            # Financial ratios, formulas, forensic math specifications
│   ├── testing/                # Testing strategies and test coverage documentation
│   ├── compliance/             # SEBI disclaimers, audit trail rules, regulatory compliance
│   ├── engineering-journal/    # Chronological engineering decisions & environment logs
│   └── phase-checkpoints/      # Phase milestone records & artifacts
│
├── scripts/
│   ├── run_all_tests.py        # Cross-stack automated test runner
│   └── run_tests.ps1           # PowerShell test runner script
│
├── .env.example                # Safe environment variable configuration template
├── .gitignore                  # Comprehensive secret and build artifact exclusion
└── pytest.ini                  # Pytest configuration
```

---

## ⚡ Quickstart & Local Setup

### 1. Prerequisites
- Python 3.11+ (Tested on Python 3.14)
- Node.js 18+ (Tested on Node.js v24.13.1, npm 11.8.0)
- Git

### 2. Environment Configuration
Copy the template environment file:
```bash
cp .env.example .env
```

### 3. Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements-dev.txt
```

### 4. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

### 5. Running the Application

#### Start Backend:
```bash
.venv\Scripts\uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Root: `http://127.0.0.1:8000/`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/api/v1/docs`
- Healthcheck Endpoint: `http://127.0.0.1:8000/api/v1/health`

#### Start Frontend:
```bash
cd frontend
npm run dev
```
- Frontend UI: `http://localhost:5173/`

---

## 🧪 Running Automated Tests

Run the complete backend test suite and frontend build check in a single command:
```bash
.venv\Scripts\python scripts/run_all_tests.py
```
Or directly via Pytest:
```bash
.venv\Scripts\pytest tests/backend -v
```

---

## 🔒 Roadmap & Phase Progression

- [x] **Phase 0: Foundation & Architecture** (Current)
- [ ] **Phase 1: Indian Equities Data Ingestion & Reconciliation** *(Locked)*
- [ ] **Phase 2: Deterministic Financial Analytics & Forensic Engine** *(Locked)*
- [ ] **Phase 3: Evidence-Linked AI Synthesis & Decision Platform** *(Locked)*

---

## 📜 Compliance & Disclaimers

This platform is intended solely for academic, quantitative research, and analytical purposes. It does not provide personalized investment advice or buy/sell recommendations under SEBI (Research Analysts) Regulations, 2014. All financial calculations must be verified by a qualified financial professional.
