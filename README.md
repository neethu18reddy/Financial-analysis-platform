<div align="center">

# 🏛️ AI-Powered Fundamental Analysis & Financial Decision Intelligence Platform
### *Institutional-Grade Quantitative Research, Deterministic Financial Data Engine & Grounded AI for Indian Equities (NSE & BSE)*

[![Python 3.14](https://img.shields.io/badge/Python-3.14.3-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0_Async-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Vite](https://img.shields.io/badge/Vite-6.1-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vite.dev/)
[![Phase 1 Checkpoint](https://img.shields.io/badge/Phase_1-Data_Engine_Complete-success?style=for-the-badge&logo=checkmarx&logoColor=white)](docs/phase-checkpoints/phase_1_checkpoint.md)
[![Test Coverage](https://img.shields.io/badge/Test_Suite-27_Passed_100%25-10b981?style=for-the-badge&logo=pytest&logoColor=white)](tests/)

<p align="center">
  <a href="#-executive-summary">Executive Summary</a> •
  <a href="#-the-cardinal-law-of-financial-computing">Core Law</a> •
  <a href="#-phase-1-financial-data-engine">Phase 1 Engine</a> •
  <a href="#-system-architecture">Architecture</a> •
  <a href="#-data-provenance--audit-trail">Provenance</a> •
  <a href="#-deterministic-validation">Validation</a> •
  <a href="#-api-endpoints">API Spec</a> •
  <a href="#-quickstart--installation">Quickstart</a> •
  <a href="#-testing--verification">Testing</a> •
  <a href="#-documentation-index">Docs</a>
</p>

</div>

---

## 📌 Executive Summary

Modern LLM-powered financial applications frequently fail in production because they delegate mathematical calculations to generative models, causing **hallucinated numbers, ungrounded valuations, and regulatory compliance risks**.

This platform solves this fundamental problem through a **hard computational boundary**:
1. **Deterministic Financial Engine:** Pure Python algorithms execute accounting computations without LLM interference.
2. **Deterministic Validation Invariants:** Double-entry accounting checks ($\text{Assets} \equiv \text{Liabilities} + \text{Equity}$, Cash Flow continuity) run automatically before any metric is persisted or analyzed.
3. **Field-Level Data Provenance:** Every metric answers *"Where did this number come from?"* with original filing links, page numbers, table titles, raw reported strings, and confidence scores.
4. **Grounded AI Interface:** LLMs are reserved strictly for qualitative synthesis, regulatory text summaries, and natural language query translation—**never for mathematical calculations**.

---

## 🏛️ The Cardinal Law of Financial Computing

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────────┐
│   1. DATA    │ ──> │2. VALIDATION │ ──> │3.CALCULATION │ ──> │ 4. ANALYTICS │ ──> │ 5. EVIDENCE  │ ──> │6. AI EXPLANATION│
│ (NSE/BSE/MCA)│     │(Ind AS Rules)│     │(Pure Python) │     │ (Forensics)  │     │(Audit Lineage│     │ (Zero-Math LLM)│
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └────────────────┘
```

> **Cardinal Rule:** The LLM is **NOT** a source of truth or a calculator. Mathematical correctness is guaranteed by code, verified by deterministic tests, and backed by immutable audit lineage.

---

## 📊 Phase 1: Financial Data Engine Capabilities

### 1. Indian Listed Equities Sourcing Matrix
All data providers and fixtures are rigorously tracked in the `source_registry`:
- **National Stock Exchange of India (NSE)**: Statutory LODR filings & XBRL disclosures.
- **Bombay Stock Exchange (BSE)**: Corporate filings and investor disclosures portal.
- **Ministry of Corporate Affairs (MCA)**: MCA21 Ind AS XBRL corporate repository.
- **Reserve Bank of India (RBI DBIE)**: Sectoral and macro banking data warehouse.
- **Audited Annual Reports (PDF)**: Statutory annual disclosures under Companies Act 2013.
- **Deterministic Golden Fixtures**: Audited golden datasets for Reliance Industries (`RELIANCE`), Tata Consultancy Services (`TCS`), and synthetic edge-case rejection benchmarks (`SYNTH_BROKEN_BS`, `SYNTH_BROKEN_CF`).

### 2. Strict Data Origin Classification
Datasets are labeled with explicit metadata flags:
- `REAL`: Sourced directly from audited financial statements without modification.
- `SYNTHETIC`: Generated test cases designed to test mathematical failure boundaries.
- `MOCK`: Offline fixtures for unit testing.
- `DERIVED`: Computed ratios, free cash flows, and split adjustment multipliers.

### 3. Three-Statement Normalized Financial Models
- **Income Statement (P&L)**: Revenue from Operations, Other Income, Total Revenue, Materials Consumed, Employee Expenses, Finance Costs, Depreciation & Amortization, Other Expenses, Total Expenses, PBT, Tax, PAT, and Basic/Diluted EPS.
- **Balance Sheet (Schedule III Ind AS)**: Non-Current Assets, Current Assets, Total Assets, Equity Share Capital, Other Equity & Reserves, Non-Current Liabilities, Current Liabilities, and Total Equity & Liabilities.
- **Cash Flow Statement (Ind AS 7)**: Cash from Operating Activities (CFO), Investing (CFI), Financing (CFF), Net Change in Cash, Cash at Beginning/End of Period, CapEx, and Free Cash Flow.
- **Corporate Actions**: Stock splits, bonus issues, dividends, buybacks, and adjustment multipliers.

---

## 🔍 Data Provenance & Audit Trail ("Where did this number come from?")

Clicking any financial value in the platform activates the **Provenance Lineage Drawer**, displaying:
- **Statutory Document**: e.g., *"Reliance Industries Annual Report 2023-24 (Audited)"*.
- **Reported As**: Original line-item title as printed in statutory report (e.g., *"Revenue from Sale of Products & Services"*).
- **Raw Filing Value**: e.g., `INR 9,14,472 Crores`.
- **Page & Table Reference**: Exact filing PDF page (e.g., `Page 348`, `Statement of Profit & Loss`).
- **Confidence Score**: Extraction certainty rating (1.0 for statutory audited filings).
- **Direct Link**: Source PDF / Exchange filing URL.

---

## 🛡️ Deterministic Validation Engine

The platform enforces deterministic accounting invariants with **Zero Silent Repair**:

$$\text{Total Assets} \equiv \text{Total Liabilities} + \text{Total Equity}$$

$$\text{Ending Cash} \equiv \text{Beginning Cash} + \text{Net Increase in Cash} + \text{FX Effect}$$

$$\text{Total Revenue} \equiv \text{Revenue from Operations} + \text{Other Income}$$

$$\text{Profit After Tax} \equiv \text{Profit Before Tax} - \text{Total Tax Expense} + \text{Share of Associates}$$

$$\text{Net Increase in Cash} \equiv \text{CFO} + \text{CFI} + \text{CFF}$$

Any discrepancy is recorded immutably in `validation_results` and highlighted with visual variance badges in the UI.

---

## 🌐 API Endpoints Specification

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/companies` | List companies with ticker/sector search filters |
| `GET` | `/api/v1/companies/{identifier}` | Retrieve company profile, ISIN, CIN, and securities |
| `GET` | `/api/v1/companies/{identifier}/periods` | List available chronological financial periods |
| `GET` | `/api/v1/companies/{identifier}/statements` | Multi-period 3-statement financials (`CONSOLIDATED`/`STANDALONE`) |
| `GET` | `/api/v1/companies/{identifier}/corporate-actions` | Historical stock splits, bonuses, dividends, and multipliers |
| `GET` | `/api/v1/companies/{identifier}/validation-report` | Complete accounting reconciliation audit report |
| `GET` | `/api/v1/provenance/{entity_type}/{entity_id}` | Field-level provenance lineage and source filing references |
| `GET` | `/api/v1/sources` | Source registry, compliance terms, and rate limits |
| `GET` | `/api/v1/health` | System health probe and database connectivity |

---

## 🚀 Quickstart & Installation

### Prerequisites
- Python 3.14+ (or Python 3.11+)
- Node.js 20+ & npm
- Git

### 1. Backend Setup & Seeding
```bash
# Activate virtual environment
.venv\Scripts\activate       # Windows
# or: source .venv/bin/activate # Linux/macOS

# Run database migrations
python -m alembic -c backend/alembic.ini upgrade head

# Seed golden Indian equity fixtures (Reliance, TCS, Synthetic test cases)
python backend/app/fixtures/seed_runner.py

# Start FastAPI backend server
uvicorn backend.app.main:app --reload --port 8000
```
Interactive Swagger API documentation: `http://localhost:8000/api/v1/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open application: `http://localhost:5173`

---

## 🧪 Testing & Verification

Run the master test runner to execute both backend Pytest suites and frontend TypeScript bundle compilation:

```bash
python scripts/run_all_tests.py
```

### Test Suite Breakdown (27/27 Passed, 100%)
- `test_deterministic_validator.py`: Balance Sheet reconciliation, Cash Flow continuity, Income Statement math, Period Chronology, and rejection of broken synthetic fixtures.
- `test_normalizer.py`: Unit conversions (Crores, Lakhs, Millions, Units) and string sanitization.
- `test_corporate_actions.py`: Stock split & bonus adjustment factor calculations.
- `test_financial_api.py`: FastAPI endpoints for companies, statements, validation reports, provenance, and corporate actions.
- `test_database.py` & `test_health_api.py`: Async database session and health probe lifecycles.
- `Frontend Build`: `tsc -b && vite build` (0 TypeScript errors).

---

## 📁 Repository Structure

```
├── backend/
│   ├── alembic/                 # Alembic migration versioning
│   ├── app/
│   │   ├── api/v1/endpoints/    # REST API endpoints (financial_engine, health)
│   │   ├── core/                # Configuration & logging
│   │   ├── db/                  # Async database engine & sessions
│   │   ├── engine/              # Core Ingestion, Normalizer, Validator & Provenance
│   │   ├── fixtures/            # Golden Indian equity datasets & seed runner
│   │   ├── models/              # SQLAlchemy 2.0 async models
│   │   └── schemas/             # Pydantic v2 API response schemas
├── frontend/
│   ├── src/
│   │   ├── components/layout/   # Institutional Bloomberg-style shell
│   │   ├── services/            # Typed API client
│   │   ├── types/               # TypeScript interfaces
│   │   └── views/               # FinancialDataEngineView & SystemHealthView
├── docs/
│   ├── architecture/            # System overview & ADRs
│   ├── compliance/              # SEBI compliance & audit guidelines
│   ├── data-sources/            # Sourcing strategy & source registry
│   ├── engineering-journal/     # Phase 0 & Phase 1 development logs
│   ├── methodology/             # Deterministic calculation specifications
│   ├── phase-checkpoints/       # Formal Phase Checkpoint audit reports
│   └── testing/                 # Test strategy documentation
├── scripts/
│   └── run_all_tests.py         # Master automated test suite runner
├── tests/backend/               # 27 Pytest unit and integration test cases
└── README.md                    # Project overview & documentation
```

---

## 📚 Documentation Index

- 📘 [Phase 1 Checkpoint Report](docs/phase-checkpoints/phase_1_checkpoint.md)
- 📗 [Source Registry & Compliance Matrix](docs/data-sources/source_registry_and_compliance.md)
- 📙 [Phase 1 Engineering Journal](docs/engineering-journal/phase_1_journal.md)
- 📕 [System Architecture & Design Patterns](docs/architecture/system_overview.md)
- 📓 [SEBI Compliance & Auditability](docs/compliance/sebi_compliance_and_audit.md)
- 📒 [Deterministic Calculation Methodology](docs/methodology/deterministic_calculations.md)

---

## 🔒 Roadmap & Hard Stop Checkpoints

- [x] **Phase 0**: Foundation, Async DB, Health Telemetry & UI Shell (`phase-0-foundation`)
- [x] **Phase 1**: Financial Data Engine, Normalization, Provenance, & Validation (`phase-1-data-engine`)
- [ ] **Phase 2**: Forensic Financial Analytics & Anomaly Detection (Locked — Awaiting Approval)
- [ ] **Phase 3**: Valuation Modeling & AI Decision Intelligence Engine (Locked)

---

<div align="center">
  <b>Built for Institutional Financial Research • Grounded in Deterministic Truth</b>
</div>
