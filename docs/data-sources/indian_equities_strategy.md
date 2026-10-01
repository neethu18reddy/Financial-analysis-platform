# Indian Equities Data Ingestion Strategy (Phase 1 Target)

## Overview
Analyzing companies listed on the National Stock Exchange of India (NSE) and Bombay Stock Exchange (BSE) requires structured ingestion across primary regulatory and market data channels.

## Primary Ingestion Channels

### 1. NSE & BSE Corporate Disclosures
- **Quarterly Financial Results**: Clause 41 / Regulation 33 SEBI (LODR) filings.
- **Annual Reports & Accounts**: Complete balance sheets, P&L statements, cash flows, and notes to accounts.
- **Shareholding Patterns**: Regulation 31 disclosures detailing promoter holdings, pledged shares, FII/DII institutional holdings, and retail participation.
- **Corporate Actions & Announcements**: Mergers, acquisitions, insider trades, and board meetings.

### 2. MCA (Ministry of Corporate Affairs) XBRL Filings
- Standardized taxonomy instances under Ind AS (Indian Accounting Standards).
- Eliminates OCR/PDF parsing hallucination risks for core balance sheets and P&L statements.

### 3. Forensic & Qualitative Disclosures
- **Auditor Report & CARO (Companies Auditor's Report Order)**:
  - Inventory physical verification remarks.
  - Statutory dues default disclosures.
  - Loans to related parties under Section 189.
  - Fraud reported by or on the company.
- **Related Party Transactions (RPT)**: Disclosures under Ind AS 24.
- **Credit Rating Agency Disclosures**: CRISIL, ICRA, CARE, India Ratings rating rationale and migration reports.

## Invariant Data Validation Checks
1. Mathematical integrity of Balance Sheet equality.
2. Reconciled cash flow sums against beginning and ending bank balances.
3. Cross-verification between standalone and consolidated statements.
4. Anomaly detection on restated prior-year figures.
