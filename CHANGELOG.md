# Changelog & Commit History

All notable changes, architectural milestones, and commit records for the **AI-Powered Fundamental Analysis and Financial Decision Intelligence Platform** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Phase 1 - Financial Data Engine] — Tag: `phase-1-data-engine` (2026-10-02)

### 📌 Milestone Overview
Implemented the complete, production-grade **Financial Data Engine for Indian Listed Equities (NSE & BSE)**. Features normalized data models for companies, securities, reporting periods, and 3-statement financials (Income Statement, Schedule III Balance Sheet, Ind AS 7 Cash Flows). Built deterministic zero-silent-repair validation, field-level provenance lineage ("Where did this number come from?"), scale normalizer, corporate action factor calculators, FastAPI endpoints, and interactive React UI viewer.

### 📝 Commit Log
* **`db38473`** - `docs(readme): generate comprehensive institutional README for Phase 1 Financial Data Engine`
* **`fca8ed8`** - `docs(phase-1): document source registry, engineering journal, and Phase 1 checkpoint`
* **`342d80f`** - `feat(web): add interactive financial data engine interface with three-statement viewer, provenance drawer, and validation inspector`
* **`199f033`** - `feat(api): expose financial statements, validation report, provenance, and corporate actions endpoints`
* **`86df279`** - `feat(engine): add ingestion pipeline, deterministic validator, normalizer, and provenance engine`
* **`67d9570`** - `feat(data): add normalized financial data models and database migrations`

### 🔍 Detailed Breakdown of Changes

#### 1. Normalized Financial Data Models & Migrations (`67d9570`)
- Created `Company` (CIN, Ticker, ISIN, Sector, Industry) & `Security` (Symbol, Exchange, Series) models.
- Created `FinancialPeriod` with explicit period types (`ANNUAL`, `QUARTERLY`, `TTM`) and Ind AS accounting standard attributes.
- Created `IncomeStatement`, `BalanceSheet`, and `CashFlowStatement` supporting both `CONSOLIDATED` and `STANDALONE` statements.
- Created `CorporateAction` (splits, bonuses, dividends, buybacks) and `ShareCountHistory`.
- Created `SourceDocument` with `DataClassification` (`REAL`, `SYNTHETIC`, `MOCK`, `DERIVED`) and licensing constraints.
- Created `DataProvenance` for field-level filing lineage.
- Created `ValidationResult` for immutable accounting audit records.
- Generated and applied Alembic async migration `d3664697577f_create_phase_1_financial_data_tables.py`.

#### 2. Ingestion Pipeline, Normalizer & Deterministic Validator (`86df279`)
- Built `source_registry.py` registering NSE, BSE, MCA XBRL, RBI DBIE, and Golden Fixture repositories with legal terms, rate limits, and redistribution constraints.
- Implemented `normalizer.py` with mathematical scale conversions (Crores, Lakhs, Millions, Units) and string sanitizers.
- Implemented `validator.py` executing deterministic double-entry accounting rules:
  - $\text{Total Assets} \equiv \text{Total Liabilities} + \text{Total Equity}$
  - Asset Sub-components Sum ($\text{Total Assets} = \text{Non-Current} + \text{Current}$)
  - Equity & Liability Sub-components Sum
  - Cash Flow Continuity ($\text{Ending Cash} = \text{Beginning Cash} + \text{Net Increase} + \text{FX}$)
  - Cash Flow Activities Sum ($\text{Net Change} = \text{CFO} + \text{CFI} + \text{CFF}$)
  - Income Statement Revenue & Net Tax arithmetic
  - Historical period chronology checks.
- Implemented `corporate_actions_calculator.py` for cumulative split and bonus multiplier lineages.
- Implemented `provenance_tracker.py` and `ingestion_service.py` separating acquisition, normalization, validation, and storage.

#### 3. API Endpoints, Golden Fixtures & Tests (`199f033`)
- Created seed fixtures with real audited Indian equities (Reliance Industries, TCS) and synthetic intentionally broken fixtures (`SYNTH_BROKEN_BS`, `SYNTH_BROKEN_CF`).
- Built REST API endpoints in `backend/app/api/v1/endpoints/financial_engine.py`:
  - `GET /companies` (Search & sector filtering)
  - `GET /companies/{id}` (Company profile, ISIN, CIN)
  - `GET /companies/{id}/periods` (Chronological fiscal periods)
  - `GET /companies/{id}/statements` (Multi-period statements with `statement_type=CONSOLIDATED|STANDALONE`)
  - `GET /companies/{id}/corporate-actions` (Historical actions and adjustment factors)
  - `GET /companies/{id}/validation-report` (Reconciliation audit checks)
  - `GET /provenance/{entity_type}/{entity_id}` (Field-level provenance records)
  - `GET /sources` (External provider registry & compliance terms)
- Added 18 new automated Pytest test cases bringing test suite to 27 tests (100% pass rate).

#### 4. Interactive Financial UI Shell (`342d80f`)
- Built `FinancialDataEngineView.tsx` with institutional Bloomberg/FactSet-grade design.
- Implemented autocomplete ticker search and sector filtering.
- Implemented Three-Statement viewer (Income Statement, Balance Sheet, Cash Flow Statement).
- Added Consolidated vs. Standalone toggle and scale unit switcher (INR Crores, Lakhs, Millions).
- Implemented slide-over **Provenance Drawer ("Where did this number come from?")** revealing source PDF, page number, reported raw string, and confidence score.
- Implemented **Validation Discrepancy Drawer** displaying all accounting checks and discrepancy variances.
- Implemented Corporate Actions Timeline with adjustment multipliers.

#### 5. Documentation & Checkpoint (`fca8ed8`, `db38473`)
- Authored Source Registry & Compliance matrix (`docs/data-sources/source_registry_and_compliance.md`).
- Authored Phase 1 Engineering Journal (`docs/engineering-journal/phase_1_journal.md`).
- Authored Phase 1 Checkpoint Report (`docs/phase-checkpoints/phase_1_checkpoint.md`).
- Overhauled institutional `README.md` with Phase 1 capabilities, badges, and quickstart.

---

## [Phase 0 - Foundation & Architecture] — Tag: `phase-0-foundation` (2026-10-01)

### 📌 Milestone Overview
Established the foundational architecture, modular repository structure, FastAPI backend, SQLAlchemy 2.0 database migration environment, React 18 TypeScript frontend shell, cross-stack test suite, and comprehensive documentation suite.

### 📝 Commit Log
* **`3df2cfe`** - `docs(readme): overhaul README for high-impact recruiter & engineering portfolio presentation`
* **`ed657fa`** - `docs(changelog): add comprehensive commit history and changelog tracking`
* **`eca1d4a`** - `docs(readme): add badges, quickstart, and comprehensive repository overview`
* **`745f633`** - `docs(architecture): document system architecture, data strategy, methodology, and compliance`
* **`3c74cc1`** - `test(all): add backend test suite, database tests, and unified test runner`
* **`3ba86dd`** - `feat(web): initialize frontend application shell, layout, and health monitoring`
* **`e690d86`** - `feat(api): initialize backend and database foundation with FastAPI and SQLAlchemy`
* **`de23de9`** - `chore(repo): initialize project structure and git configuration`
