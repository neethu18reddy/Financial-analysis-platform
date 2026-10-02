# Engineering Journal: Phase 1 — Financial Data Engine

- **Date**: 2026-10-02
- **Author**: Lead AI Platform Engineer (Antigravity)
- **Phase Target**: Phase 1 (Financial Data Engine)
- **Status**: COMPLETE & VERIFIED

---

## 1. Objectives & Architectural Requirements

Phase 1 establishes the foundational data engine for Indian listed equities, focusing on:
1. Normalized SQL models for Indian corporate entities, securities, reporting periods, and financial statements (Income Statement, Balance Sheet, Cash Flow Statement, Corporate Actions, Share Counts, Provenance, and Validation).
2. Clean separation of concerns across Ingestion:
   `Acquisition -> Normalization -> Deterministic Validation -> Provenance Lineage -> Storage -> Analytics`
3. Zero silent repair: mathematical imbalances in filings (such as broken balance sheets or broken cash flows) are surfaced transparently in `validation_results` rather than silently mutated.
4. Field-level provenance tracking: every individual financial metric is traced to its original document, page number, reported scale unit, and confidence rating.
5. Multi-scale normalization into canonical INR Crores (`1 Cr = 10,000,000 INR`) with display conversion into Lakhs, Millions, and raw units.
6. Corporate action factor mathematics: stock splits, bonus shares, and dividend adjustments.

---

## 2. Key Modules Implemented

### A. Database Models (`backend/app/models/`)
- `company.py`: `Company` (CIN, Ticker, ISIN, Sector, Industry, Exchange) & `Security` (Symbol, Series, Currency).
- `source.py`: `SourceDocument` with `DataClassification` (`REAL`, `SYNTHETIC`, `MOCK`, `DERIVED`) and licensing constraints.
- `financial_period.py`: `FinancialPeriod` with explicit period types (`ANNUAL`, `QUARTERLY`, `TTM`), reporting standards (`IND_AS`, `IFRS`), and canonical scale units.
- `financial_statements.py`: `IncomeStatement`, `BalanceSheet`, and `CashFlowStatement` supporting both `CONSOLIDATED` and `STANDALONE` reporting formats.
- `corporate_actions.py`: `CorporateAction` and `ShareCountHistory`.
- `provenance.py`: `DataProvenance` field-level origin mapper.
- `validation.py`: `ValidationResult` immutable audit logs.

### B. Ingestion & Validation Engine (`backend/app/engine/`)
- `source_registry.py`: Registry for NSE, BSE, MCA XBRL, RBI DBIE, and Golden Fixture repositories.
- `normalizer.py`: Scale transformation and string sanitization.
- `validator.py`: Deterministic validation rules:
  - Balance Sheet Fundamental Equation: $\text{Total Assets} \equiv \text{Total Liabilities} + \text{Total Equity}$
  - Asset Sub-components Sum: $\text{Total Assets} \equiv \text{Non-Current Assets} + \text{Current Assets}$
  - Liability Sub-components Sum: $\text{Total Equity \& Liab} \equiv \text{Equity} + \text{Non-Current Liab} + \text{Current Liab}$
  - Cash Flow Continuity: $\text{Ending Cash} \equiv \text{Beginning Cash} + \text{Net Change} + \text{FX Effect}$
  - Cash Flow Activities Sum: $\text{Net Change} \equiv \text{CFO} + \text{CFI} + \text{CFF}$
  - Revenue & Profit Arithmetic: $\text{Total Rev} \equiv \text{Ops} + \text{Other}$, $\text{PAT} \equiv \text{PBT} - \text{Tax} + \text{Associates}$
  - Period Chronology ordering.
- `corporate_actions_calculator.py`: Split multiplier ($N/D$) and bonus multiplier ($1 + N/D$) calculations.
- `provenance_tracker.py`: Records field mappings into database.
- `ingestion_service.py`: Pipeline orchestrator.

### C. Golden Fixtures & API (`backend/app/fixtures/`, `backend/app/api/`)
- Real Indian equities audited datasets (Reliance Industries, TCS) across FY22-23 and FY23-24.
- Synthetic intentionally broken fixtures (`SYNTH_BROKEN_BS`, `SYNTH_BROKEN_CF`) verifying that validation failure detection works accurately.
- FastAPI endpoints for companies, multi-period statements, validation audit reports, corporate actions, and provenance inspection.

### D. Institutional Frontend UI (`frontend/src/views/FinancialDataEngineView.tsx`)
- Interactive company search, sector pills, and quick dropdown.
- Consolidated vs Standalone toggle.
- Unit switcher (INR Crores, INR Lakhs, INR Millions).
- Three-statement financial viewer (Income Statement, Schedule III Balance Sheet, Ind AS 7 Cash Flows).
- Interactive Provenance Drawer ("Where did this number come from?") displaying statutory source filing, page number, raw string, and confidence score.
- Validation Discrepancy Drawer showing passed/failed rules and discrepancy variances.
- Corporate actions timeline with adjustment multipliers.

---

## 3. Test Verification & Results

- Backend tests: `27 / 27 passed` (100%).
- Frontend TypeScript compile & Vite production build: `0 errors`.
- Master runner: `scripts/run_all_tests.py` passed cleanly.
- Git tag: `phase-1-data-engine`.
