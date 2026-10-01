# AI-Powered Fundamental Analysis and Financial Decision Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-6.1-646CFF?logo=vite&logoColor=white)
![Build](https://img.shields.io/badge/Tests-100%25%20Passing-success)
![License](https://img.shields.io/badge/License-Proprietary-blue)

> **Institutional-Grade Fundamental Research, Deterministic Calculations, and Forensic Intelligence for Publicly Listed Indian Companies (NSE & BSE).**

---

## 🏛️ The Cardinal Law of Financial Computing

```
DATA ──> VALIDATION ──> CALCULATIONS ──> ANALYTICS ──> EVIDENCE ──> AI EXPLANATION
```

> [!IMPORTANT]
> **The Large Language Model (LLM) is NOT the source of truth for financial data or deterministic financial calculations.**
> All accounting metrics, financial ratios (ROCE, ROE, DuPont, Piotroski F-Score, Altman Z-Score), and forensic scores are computed purely via deterministic, verifiable Python algorithms with full mathematical traceability. The AI is restricted solely to explaining verified facts, summarizing evidence, and synthesizing citations from official corporate disclosures.

---

## 🚀 Status: Phase 0 (Foundation & Architecture)

| Subsystem | Technology Stack | Status | Verification |
| :--- | :--- | :---: | :--- |
| **Backend API** | FastAPI, Python 3.14, Async ASGI, Pydantic v2 | ✅ Active | Unit/Integration Tests Passing |
| **Database Engine** | SQLAlchemy 2.0 Async, Alembic Migrations | ✅ Active | Live Connection Pooling Tested |
| **Frontend Shell** | React 18, TypeScript, Vite, Dark-Mode Theme | ✅ Active | Zero-Error Production Build |
| **Testing Engine** | Pytest, Asyncio, Multi-Tier Test Runner | ✅ Active | 9/9 Backend Tests Passing (100%) |
| **Documentation** | ADRs, Data Strategies, Methodology, SEBI Compliance | ✅ Active | Complete in `/docs` |
| **Future Phases (1-3)** | Ingestion, Deterministic Analytics, AI Decision Engine | 🔒 Locked | Documented only; awaiting approval |

---

## 📁 Repository Directory Structure

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
│   │   ├── schemas/            # Pydantic request/response schemas
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

## ⚡ Quickstart & Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/neethu18reddy/Financial-analysis-platform.git
cd Financial-analysis-platform
```

### 2. Environment Configuration
Copy the sample environment file:
```bash
cp .env.example .env
```

### 3. Backend Setup
```bash
# Create and activate Python virtual environment
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# On Linux/macOS:
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements-dev.txt
```

### 4. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

---

## 🖥️ Running the Platform

### Start Backend API Server
```bash
.venv\Scripts\uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
* **API Root:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Interactive OpenAPI Docs:** [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)
* **Subsystem Health Status:** [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

### Start Frontend Application
```bash
cd frontend
npm run dev
```
* **Web UI Dashboard:** [http://localhost:5173/](http://localhost:5173/)

---

## 🧪 Automated Testing

To run the unified test suite verifying both backend test suites and frontend builds:
```bash
.venv\Scripts\python scripts/run_all_tests.py
```

To run Pytest directly:
```bash
.venv\Scripts\pytest tests/backend -v
```

---

## 📚 Project Documentation

Detailed specifications and architectural documents are located in `/docs`:

* **[Architecture Overview](docs/architecture/system_overview.md)** — Architectural design and computation flow.
* **[ADR 001: Technology Stack](docs/architecture/adr_001_stack_selection.md)** — Rationale behind technology choices.
* **[Indian Equities Data Strategy](docs/data-sources/indian_equities_strategy.md)** — NSE/BSE filings, MCA XBRL, and disclosures.
* **[Deterministic Methodology](docs/methodology/deterministic_calculations.md)** — Formulas for ROCE, DuPont, Piotroski, and Altman Z-score.
* **[Testing Protocols](docs/testing/testing_strategy.md)** — Quality assurance guidelines.
* **[SEBI Compliance & Auditability](docs/compliance/sebi_compliance_and_audit.md)** — Regulatory guidelines and lineage.
* **[Engineering Journal](docs/engineering-journal/phase_0_journal.md)** — Implementation and environment records.
* **[Phase 0 Checkpoint](docs/phase-checkpoints/phase_0_checkpoint.md)** — Milestone summary and verification.

---

## 🔒 Roadmap & Phased Execution

- [x] **Phase 0: Foundation & Architecture** *(Completed & Verified)*
- [ ] **Phase 1: Indian Equities Data Ingestion & Financial Statement Reconciliation** *(Locked)*
- [ ] **Phase 2: Deterministic Financial Analytics & Forensic Screening Engine** *(Locked)*
- [ ] **Phase 3: Evidence-Linked AI Synthesis & Decision Platform** *(Locked)*

---

## 📜 Compliance & Regulatory Disclaimer

This platform is developed strictly for quantitative research, academic analysis, and financial education purposes. It does not provide personalized investment advice, stock recommendations, or price targets under the SEBI (Research Analysts) Regulations, 2014. All financial calculations must be independently verified by a certified financial professional before making investment decisions.
