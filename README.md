<div align="center">

# 🏛️ AI-Powered Fundamental Analysis & Financial Decision Intelligence Platform
### *Institutional-Grade Quantitative Research, Deterministic Financial Data Engine & Grounded AI for Indian Equities (NSE & BSE)*

[![Python 3.14](https://img.shields.io/badge/Python-3.14.3-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0_Async-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Vite](https://img.shields.io/badge/Vite-6.1-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vite.dev/)
[![Phase 7 Checkpoint](https://img.shields.io/badge/Phase_7-AI_Analyst_%26_Research_Product_Complete-success?style=for-the-badge&logo=checkmarx&logoColor=white)](docs/phase-checkpoints/phase_7_checkpoint.md)
[![Test Coverage](https://img.shields.io/badge/Test_Suite-92_Passed_100%25-10b981?style=for-the-badge&logo=pytest&logoColor=white)](tests/)

<p align="center">
  <a href="#-executive-summary">Executive Summary</a> •
  <a href="#-phase-7-ai-analyst--research-product">Phase 7 AI Analyst</a> •
  <a href="#-phase-6-document-intelligence--rag">Phase 6 Document RAG</a> •
  <a href="#-phase-4-valuation-engine--scenario-modeling">Phase 4 Valuation</a> •
  <a href="#-phase-3-forensic-intelligence-engine">Phase 3 Forensics</a> •
  <a href="#-phase-2-fundamental-analysis-engine">Phase 2 Fundamentals</a> •
  <a href="#-phase-1-financial-data-engine">Phase 1 Data Engine</a> •
  <a href="#-system-architecture">Architecture</a> •
  <a href="#-deterministic-validation">Validation</a> •
  <a href="#-api-endpoints">API Spec</a> •
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

## 🤖 Phase 7: AI Analyst, Historical Validation & Research Product

Phase 7 delivers a production-grade, zero-hallucination institutional research experience:

1. **Deterministic & Pluggable AI Architecture**:
   - Zero-hallucination offline financial reasoner producing structured, verifiable analytical claims.
   - Configurable for Google Gemini and OpenAI external LLM backends with strict JSON schema adherence.
2. **Financial Question Router**:
   - Classifies user intent across 11 financial dimensions (ROCE, margins, cash quality, forensics, DCF assumptions, management guidance).
3. **Point-in-Time (PIT) Temporal Guardrails**:
   - Reconstructs historical financial analysis strictly bounded by chosen cut-off periods, completely eliminating lookahead bias.
4. **Mandatory Citation Verification & Accusation Interception**:
   - Cross-references every analytical claim against underlying numbers or exact Annual Report PDF quotations.
   - Intercepts inflammatory accusations and sanitizes statistical anomalies into compliant screening findings.
5. **Management "Said vs Did" Credibility Tracker**:
   - Evaluates forward-looking management guidance against multi-year audited outcomes with an objective credibility percentage.
6. **14-Section Institutional Equity Research Report Generator**:
   - Synthesizes business overview, 5-step DuPont decomposition, forensic scoreboard, DCF valuation, and statutory caveats into a publication-grade report.
7. **Watchlist & Metric Anomaly Alert Engine**:
   - Screens monitored equities for margin shifts (>200 bps), working capital stress, and credit health transitions.

---

## 📑 Phase 6: Document Intelligence & Annual Report RAG

Phase 6 implements a statutory document processing and retrieval-augmented generation (RAG) pipeline:

1. **Multi-Stage Document Ingestion**: PDF parsing, SHA-256 fingerprinting, page preservation, and table boundary detection.
2. **Deterministic Financial Vector Embeddings**: 64-dimensional semantic projection with cosine similarity retrieval.
3. **Structured Citation Provenance**: Every retrieved passage retains document ID, ticker, fiscal year, page number, section title, and exact quote.

---

## 💎 Phase 4: Valuation Engine & Scenario Modeling Capabilities

Phase 4 delivers an institutional valuation suite with pure Python determinism, real-time expectation solving, and multi-scenario risk analysis:

1. **Multi-Stage Free Cash Flow to Firm (FCFF) DCF:**
   - Pro-forma forecasting (3 to 10 years) covering Revenue, EBIT, NOPAT, Capex, and Working Capital.
   - WACC derivation incorporating Indian G-Sec risk-free rate ($\sim 7.10\%$), Equity Risk Premium ($6.00\%$), and after-tax cost of debt.
   - Dual terminal value approaches: Gordon Growth Model and Exit Multiple with balance sheet bridge to Equity Value.
2. **Reverse DCF Market Expectation Solver:**
   - Backs out the implied 5-year revenue CAGR and FCF generation embedded in current market prices using a deterministic bisection solver.
   - Categorizes market expectations into `CONSERVATIVE`, `REALISTIC`, `AGGRESSIVE`, and `EXTREME`.
3. **Relative Multiples Benchmarking:**
   - Comprehensive multi-multiple engine (P/E, EV/EBITDA, P/B, EV/Sales) benchmarked against 1-Yr, 3-Yr, and 5-Yr historical percentiles.
4. **Probabilistic Scenario Modeling:**
   - Explicit Bear (25%), Base (50%), and Bull (25%) valuation trajectories with probability-weighted expected fair value and risk/reward asymmetry skew.
5. **2D Sensitivity Matrices:**
   - Dynamic 5x5 grids for Discount Rate (WACC) vs Terminal Growth Rate and Revenue Growth vs Operating Margin.
6. **Financial Institutions Valuation Engine:**
   - Multi-Stage Dividend Discount Model (DDM) constrained by RBI Tier-1 Capital Adequacy retention minimums and Gordon Justified Price-to-Book ($\frac{\text{ROE}-g}{K_e-g}$).

---

## 🕵️ Phase 3: Forensic Intelligence Engine Capabilities

Phase 3 introduces institutional-grade forensic screening, statistical manipulation detection, and distress modeling:

1. **Beneish 8-Variable M-Score Model:**
   - Detects earnings distortion & aggressive accounting ($DSRI, GMI, AQI, SGI, DEPI, SGAI, TATA, LVGI$).
   - Statistical cutoff: $M > -1.78$ flagged as anomalous earnings manipulation risk.
   - Built-in financial/banking sector inapplicability guardrails.
2. **Piotroski 9-Point F-Score Matrix:**
   - Binary scoring evaluating fundamental momentum across **Profitability** (4 pts), **Leverage/Liquidity** (3 pts), and **Operating Efficiency** (2 pts).
   - High-conviction classification ($8-9$: Strong, $5-7$: Stable, $0-4$: Weak/Distressed).
3. **Emerging Market Altman Z''-Score:**
   - 4-variable solvency model tailored for Indian corporate balance sheets.
   - Classification zones: Safe ($Z'' > 2.60$), Grey ($1.10 \le Z'' \le 2.60$), Distress ($Z'' < 1.10$).
4. **Granular Anomaly Screening Matrix:**
   - Sloan Balance Sheet Accruals vs Total Assets.
   - Channel Stuffing / Trade Receivables vs Revenue divergence.
   - Inventory Buildup vs COGS divergence.
   - Debt Escalation vs Operating Profit (EBIT).
   - Non-Operating Other Income dependency & Effective Tax Rate anomalies.
5. **Zero-Accusation Compliance & Lineage:**
   - Standardized terminology (`ANOMALY`, `POTENTIAL_CONCERN`, `REQUIRES_INVESTIGATION`).
   - Interactive Forensic Lineage & Formula Inspector modal on frontend.

---

## 📈 Phase 2: Fundamental Analysis Engine Capabilities

Phase 2 builds directly upon the Phase 1 Financial Data Engine to provide institutional-grade fundamental analysis for Indian listed companies with pure Python calculation determinism:

1. **Profitability & Return Ratios:**
   - Margins: Gross Margin, EBITDA Margin, EBIT Margin, PAT (Net Profit) Margin.
   - Capital Efficiency: Return on Equity (ROE), Return on Capital Employed (ROCE), Return on Invested Capital (ROIC with dynamic NOPAT and bounded tax rates), Return on Assets (ROA).
2. **Growth Trajectory & Multi-Year CAGR:**
   - YoY growth rates across Revenue, EBITDA, EBIT, PAT, CFO, and FCF.
   - Multi-year Compound Annual Growth Rate (CAGR) with strict boundary protections (non-positive bases flagged as undefined).
3. **Working Capital & Efficiency:**
   - Operating cycles: Days Sales Outstanding (DSO), Days Inventory Outstanding (DIO), Days Payables Outstanding (DPO), Cash Conversion Cycle (CCC).
   - Liquidity & Turnover: Total Asset Turnover, Current Ratio, Quick Ratio.
4. **Cash Quality & Earnings Integrity:**
   - Cash Realization: CFO/PAT Ratio, FCF/PAT Ratio.
   - Sloan Balance Sheet Accrual Ratio (% of Total Assets).
   - Solvency: Operating Cash Flow to Total Debt.
5. **DuPont Multiplicative Decomposition:**
   - 3-Step DuPont Identity: $\text{ROE} = \text{Net Margin} \times \text{Asset Turnover} \times \text{Equity Multiplier}$.
   - 5-Step Extended DuPont Identity: $\text{ROE} = \text{Tax Burden} \times \text{Interest Burden} \times \text{Operating Margin} \times \text{Asset Turnover} \times \text{Equity Multiplier}$.
6. **Vertical Common-Size Financial Statements:**
   - Standardized Common-Size Income Statement (% of Total Revenue).
   - Standardized Common-Size Balance Sheet (% of Total Assets).
7. **Lineage & Methodology Versioning:**
   - Every metric delivers full data contracts (`CalculatedMetric`) with methodology `v1.0.0`, mathematical formulas, and input dictionaries.
   - Interactive UI **Formula & Lineage Inspector Modal** provides instantaneous auditability.

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
