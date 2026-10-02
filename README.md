<div align="center">

# 🏛️ AI-Powered Fundamental Analysis & Financial Decision Intelligence Platform
### *Institutional-Grade Quantitative Research, Forensic Analytics & Grounded AI for Indian Equities (NSE & BSE)*

[![Python 3.14](https://img.shields.io/badge/Python-3.14.3-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0_Async-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Vite](https://img.shields.io/badge/Vite-6.1-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vite.dev/)
[![Phase 1 Complete](https://img.shields.io/badge/Phase_1-Data_Engine_Complete-success?style=for-the-badge&logo=checkmarx&logoColor=white)](docs/phase-checkpoints/phase_1_checkpoint.md)
[![Tests Passing](https://img.shields.io/badge/Test_Suite-27_Passed_100%25-10b981?style=for-the-badge&logo=pytest&logoColor=white)](tests/)

<p align="center">
  <a href="#-executive-summary">Executive Summary</a> •
  <a href="#-the-cardinal-law-of-financial-computing">Core Engineering Law</a> •
  <a href="#-architectural-highlights--design-patterns">Architecture & Design</a> •
  <a href="#-technology-stack--skills-showcase">Tech Stack</a> •
  <a href="#-deterministic-financial-engine">Financial Engine</a> •
  <a href="#-quickstart--local-deployment">Quickstart</a> •
  <a href="#-engineering-journal--adrs">ADRs & Documentation</a> •
  <a href="#-contact--hire-me">Hire the Author</a>
</p>

</div>

---

## 📌 Executive Summary

Modern LLM-powered financial applications often fail in production because they rely on generative models to "calculate" numbers, leading to **hallucinations, non-reproducible valuation metrics, and compliance breaches**.

This platform is engineered from the ground up to solve that problem. Built for **institutional equity research on 4,000+ publicly traded companies on the NSE (National Stock Exchange of India) and BSE (Bombay Stock Exchange)**, it enforces a **strict computational boundary**:

1. **Deterministic Financial Engine:** Pure, verifiable mathematical routines compute accounting metrics (ROCE, ROE, 5-Step DuPont, Piotroski F-Score, Altman Z''-Score, Working Capital Cycles).
2. **Reconciliation & Validation Engine:** Double-entry accounting invariants (`Assets == Liabilities + Equity`, cash flow reconciliation) run before any metric is computed.
3. **Audit Trail & Evidence Store:** Every calculated metric links directly to the filing date, raw line item, and SHA-256 document checksum.
4. **Grounded AI Explanation:** The LLM is strictly used as an analytical synthesizer and natural language interface—**never as a calculator**.

---

## 🏛️ The Cardinal Law of Financial Computing

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────────┐
│   1. DATA    │ ──> │2. VALIDATION │ ──> │3.CALCULATION │ ──> │ 4. ANALYTICS │ ──> │ 5. EVIDENCE  │ ──> │6. AI EXPLANATION│
│ (NSE/BSE/MCA)│     │(Ind AS Rules)│     │(Pure Python) │     │ (Forensics)  │     │(Audit Lineage│     │ (Zero-Math LLM)│
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └────────────────┘
```

> **Engineering Principle:** The LLM is **NOT** the source of truth for financial data or deterministic calculations. Mathematical correctness is guaranteed by code, validated by automated suites, and proven with immutable audit lineage.

---

## 🚀 Key Engineering Highlights & Competencies Demonstrated

### ⚡ 1. High-Performance Asynchronous Backend (Python 3.14 & FastAPI)
- Fully asynchronous ASGI architecture designed for high-concurrency market data streaming.
- Pydantic v2 `BaseSettings` for strongly typed configuration management and zero-secret leaks.
- Request observability middleware injecting `X-Request-ID` UUIDs and microsecond-level execution profiling `X-Process-Time-Ms`.
- Global error handling returning structured RFC-compliant JSON responses for all 4xx/5xx exceptions.

### 🗄️ 2. Resilient Database & Migration Architecture (SQLAlchemy 2.0 Async + Alembic)
- Dual-dialect database abstraction: Native asynchronous connection pooling (`asyncpg`/`psycopg`) for production PostgreSQL, with seamless `aiosqlite` local fallback for zero-dependency development.
- Automated migration management with Alembic versioning.
- Active connection health probes validating database responsiveness on every healthcheck tick.

### 🎨 3. Institutional Bloomberg/FactSet-Grade UI Shell (React 18 + TypeScript + Vite)
- Precision dark-mode layout engineered for equity analysts, financial engineers, and risk officers.
- Strict TypeScript contracts mirroring backend Pydantic schemas.
- Modular component hierarchy (`AppLayout`, `Header`, `Sidebar`, `Card`, `Badge`, `Alert`, `Spinner`).
- Live subsystem telemetry visualizing real-time backend, database, and OS health.

### 🧪 4. Enterprise-Grade Testing & CI/CD Hygiene
- 100% test pass rate across unit tests, database session lifecycles, and API endpoints via Pytest.
- Unified cross-platform automated test runner (`scripts/run_all_tests.py`) validating both backend test suites and frontend TypeScript builds in a single step.
- Strict Git commit discipline adhering to the **Conventional Commits** standard with semantic release tagging (`phase-0-foundation`).

---

## 🛠️ Technology Stack & Skills Showcase

| Domain | Technologies & Libraries | Key Skills Demonstrated |
| :--- | :--- | :--- |
| **Backend & Systems** | Python 3.14, FastAPI, Uvicorn, Pydantic v2, HTTPX | Async ASGI, REST API Architecture, Concurrency, Middleware, Error Handling |
| **Database & ORM** | SQLAlchemy 2.0 (Async), Alembic, PostgreSQL / SQLite | Connection Pooling, Async Sessions, Schema Migrations, DDL Management |
| **Frontend & UI/UX** | React 18, TypeScript 5.6, Vite 6, Lucide Icons | Component Architecture, State Management, Strict Typing, Modern CSS Design |
| **Quantitative Finance** | Pure Python, NumPy, Ind AS Standards, MCA XBRL | Financial Statement Analysis, Ratio Math, DuPont Analysis, Forensic Scoring |
| **Testing & Quality** | Pytest, Pytest-Asyncio, Pytest-Cov, TypeScript Compiler | Test-Driven Development (TDD), Integration Testing, Automated Test Runners |
| **DevOps & Architecture** | Git, Environment Configurations, Markdown Documentation | Architectural Decision Records (ADRs), Clean Code, Git Tagging, Auditability |

---

## 📐 Deterministic Financial Engine (Phase 0 Spec)

The platform implements exact mathematical algorithms for fundamental valuation and forensic accounting:

### 1. Capital Efficiency & Operating Returns
$$\text{ROCE} = \frac{\text{EBIT}}{\text{Total Assets} - \text{Current Liabilities}} \qquad\qquad \text{ROE} = \frac{\text{Net Income}}{\text{Shareholders' Equity}}$$

### 2. DuPont 3-Step & 5-Step Decomposition
$$\text{ROE} = \underbrace{\left(\frac{\text{Net Income}}{\text{Revenue}}\right)}_{\text{Net Profit Margin}} \times \underbrace{\left(\frac{\text{Revenue}}{\text{Total Assets}}\right)}_{\text{Asset Turnover}} \times \underbrace{\left(\frac{\text{Total Assets}}{\text{Equity}}\right)}_{\text{Financial Leverage}}$$

### 3. Forensic & Solvency Scoring Models
- **Piotroski F-Score (9-Point Fundamental Quality Matrix)**: Evaluates profitability, leverage/liquidity, and operating efficiency.
- **Altman Z''-Score for Emerging Markets (Indian Manufacturing & Services)**:
  $$Z'' = 6.56X_1 + 3.26X_2 + 6.72X_3 + 1.05X_4$$

### 4. Working Capital & Cash Conversion Cycle (CCC)
$$\text{CCC} = \text{DIO (Days Inventory)} + \text{DSO (Days Sales Outstanding)} - \text{DPO (Days Payables Outstanding)}$$

---

## 📁 Repository Architecture

```
├── backend/
│   ├── alembic/                # Version-controlled database migration scripts
│   ├── alembic.ini             # Alembic configuration
│   ├── app/
│   │   ├── api/v1/             # Modular REST API endpoints
│   │   │   └── endpoints/
│   │   │       └── health.py   # Deep subsystem healthcheck endpoint
│   │   ├── core/               # Pydantic BaseSettings, logging, and CORS config
│   │   ├── db/                 # Async database engine, session factory, Declarative Base
│   │   ├── schemas/            # Strongly-typed Pydantic request/response schemas
│   │   └── main.py             # ASGI entrypoint, middleware, and exception handlers
│   ├── requirements.txt        # Production dependencies
│   └── requirements-dev.txt    # Testing & development dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable UI primitives (Card, Badge, Alert, Spinner, Layout)
│   │   ├── services/           # Typed Axios/Fetch API client service
│   │   ├── types/              # TypeScript interface definitions
│   │   ├── views/              # Live Foundation Views (Health Telemetry, Architecture, Pipeline)
│   │   ├── App.tsx             # Root React application component
│   │   └── main.tsx            # DOM mounting and React 18 strict mode
│   ├── package.json            # Node dependencies
│   └── vite.config.ts          # Vite build config with reverse API proxy
│
├── tests/
│   └── backend/                # Pytest suites (Config, Database, Health API, Error Handlers)
│
├── docs/
│   ├── architecture/           # Architecture Blueprint & ADR 001 (Stack Selection)
│   ├── data-sources/           # Ingestion strategy for NSE/BSE filings & MCA XBRL
│   ├── methodology/            # Mathematical formulas for ratios & forensic scores
│   ├── testing/                # Multi-tier QA and testing strategy
│   ├── compliance/             # SEBI (Research Analysts) Regulations & audit trails
│   ├── engineering-journal/    # Chronological implementation logs and decision records
│   └── phase-checkpoints/      # Phase milestone verification records
│
├── scripts/
│   ├── run_all_tests.py        # Unified cross-stack test runner (Backend + Frontend)
│   └── run_tests.ps1           # Windows PowerShell test automation script
│
├── CHANGELOG.md                # Full chronological commit history and release notes
├── .env.example                # Safe environment variable configuration template
├── .gitignore                  # Production-grade secret and artifact protection
└── pytest.ini                  # Pytest configuration
```

---

## ⚡ Quickstart & Local Deployment

### 1. Clone the Repository
```bash
git clone https://github.com/neethu18reddy/Financial-analysis-platform.git
cd Financial-analysis-platform
```

### 2. Configure Environment
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

# Install dependencies
pip install -r backend/requirements-dev.txt
```

### 4. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

### 5. Start Development Servers

**Start FastAPI Backend:**
```bash
.venv\Scripts\uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
* **Interactive OpenAPI Docs:** [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)
* **Subsystem Health Status:** [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

**Start Frontend Application:**
```bash
cd frontend
npm run dev
```
* **Application Shell:** [http://localhost:5173/](http://localhost:5173/)

---

## 🧪 Running Automated Tests

Run the complete cross-stack test suite with a single command:
```bash
.venv\Scripts\python scripts/run_all_tests.py
```

Expected output:
```
========================================================
PHASE 0 TEST SUITE: BACKEND, DATABASE, AND FRONTEND
========================================================
[*] RUNNING: Backend Unit & Integration Tests (FastAPI, DB, Health, Errors)
[PASS] Backend Unit & Integration Tests (FastAPI, DB, Health, Errors) (0.87s)

[*] RUNNING: Frontend TypeScript Compile & Production Bundle Build
[PASS] Frontend TypeScript Compile & Production Bundle Build (2.04s)

========================================================
TEST SUITE SUMMARY
========================================================
Total Suites: 2 | Passed: 2 | Failed: 0
[ALL PASS] ALL PHASE 0 TESTS COMPLETED SUCCESSFULLY!
```

---

## 📚 Deep-Dive Documentation & ADRs

The repository includes enterprise-grade documentation reflecting real-world engineering standards:

* 🏛️ **[System Architecture](docs/architecture/system_overview.md)** — Architectural design and computation flow.
* 📝 **[ADR 001: Technology Stack](docs/architecture/adr_001_stack_selection.md)** — Rationale behind FastAPI, React, SQLAlchemy 2.0, and Vite.
* 📊 **[Indian Equities Data Strategy](docs/data-sources/indian_equities_strategy.md)** — NSE/BSE filings, MCA XBRL, and disclosures.
* 🧮 **[Deterministic Methodology](docs/methodology/deterministic_calculations.md)** — Mathematical formulations for forensic and fundamental ratios.
* 🧪 **[Testing Protocols](docs/testing/testing_strategy.md)** — Multi-level quality assurance protocols.
* ⚖️ **[SEBI Compliance & Auditability](docs/compliance/sebi_compliance_and_audit.md)** — Regulatory guidelines and lineage.
* 📔 **[Engineering Journal](docs/engineering-journal/phase_0_journal.md)** — Implementation and environment records.
* 📜 **[Commit History & Changelog](CHANGELOG.md)** — Semantic commit log and release milestones.

---

## 🔒 Roadmap & Phased Execution

- [x] **Phase 0: Foundation & Architecture** *(Completed & Verified)*
- [ ] **Phase 1: Indian Equities Data Ingestion & Financial Statement Reconciliation** *(Locked)*
- [ ] **Phase 2: Deterministic Financial Analytics & Forensic Screening Engine** *(Locked)*
- [ ] **Phase 3: Evidence-Linked AI Synthesis & Decision Platform** *(Locked)*

---

## 👨‍💻 Contact & Hire Me

I am a passionate software engineer specializing in **full-stack engineering, high-performance Python backends, quantitative systems, and data-intensive applications**.

If you are looking for an engineer who writes **clean, self-documenting, fully tested code with deep architectural rigor**, let's connect!

* 🐙 **GitHub:** [@neethu18reddy](https://github.com/neethu18reddy)
* 💼 **Open to Roles:** Full Stack Engineer • Backend Engineer • Python / FastAPI Specialist • Quant Developer • Fintech Software Engineer

---

## 📜 Compliance & Regulatory Disclaimer

*This platform is developed strictly for quantitative research, academic analysis, and financial education purposes. It does not provide personalized investment advice, stock recommendations, or price targets under SEBI (Research Analysts) Regulations, 2014. All financial calculations must be independently verified by a certified financial professional.*
