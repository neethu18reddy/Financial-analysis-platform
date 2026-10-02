# Indian Listed Company Financial Data Sourcing & Compliance Registry

## 1. Statutory Regulatory Framework

In India, corporate financial disclosures for listed entities are governed by:
- **SEBI (Listing Obligations and Disclosure Requirements) Regulations, 2015 (LODR)**
- **Companies Act, 2013 (Schedule III & Ind AS Accounting Standards)**
- **MCA XBRL Taxonomy Rules (Ministry of Corporate Affairs)**
- **RBI DBIE Open Access Guidelines (Reserve Bank of India)**

---

## 2. Source Provider Registry Matrix

| Provider Name | Source Type | Access Method | Terms & Licensing | Storage & Archival | Redistribution Rule | Rate Limits | Supported Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **National Stock Exchange of India (NSE)** | `NSE_FILING` | Statutory Disclosures & XBRL Filings | Public regulatory access under SEBI LODR | Historical caching permitted for internal audit & research | Raw dissemination prohibited without exchange data license; derived analytics allowed | Respectful queuing ($\le 2$ req/sec) | `REAL` |
| **Bombay Stock Exchange (BSE)** | `BSE_FILING` | Corporate Filings Portal | Statutory investor disclosures | Audit log preservation compliant with regulatory archival norms | Proprietary redistribution restricted; analytical processing allowed | $\le 2$ req/sec with backoff | `REAL` |
| **Ministry of Corporate Affairs (MCA)** | `MCA_XBRL` | MCA21 / XBRL Taxonomy | Government Open Data / Statutory Corporate Repository | Permanent storage permitted for enterprise compliance | Public record disclosures permitted for analytical dissemination | Batch retrieval off-peak | `REAL` |
| **Reserve Bank of India (RBI)** | `RBI_DBIE` | Database on Indian Economy Open API | RBI Open Data Policy (Open Access) | Full retention allowed | Permitted with mandatory attribution to RBI | 50 req/min | `REAL`, `DERIVED` |
| **Audited Annual Reports** | `ANNUAL_REPORT_PDF` | Official Investor Relations PDFs | Statutory audited shareholder disclosures | Local archival permitted for audit verification & field lineage | Extracts permitted with source reference | N/A (CDN / Local) | `REAL` |
| **Antigravity Fixture Registry** | `AUDITED_FINANCIALS_FIXTURE` | Pre-validated JSON Golden Fixtures | Internal testing & golden dataset verification (MIT) | Committed to test harness | Open source fixture | Unrestricted | `REAL`, `SYNTHETIC`, `MOCK`, `DERIVED` |

---

## 3. Strict Dataset Origin Labeling Rules

Every dataset and source document in the platform is strictly labeled with one of four explicit metadata flags:

1. **`REAL`**: Sourced directly from audited financial statements, annual reports, or official exchange statutory filings without modification.
2. **`SYNTHETIC`**: Programmatically generated datasets designed to test mathematical boundaries and failure modes (e.g., intentionally broken balance sheets).
3. **`MOCK`**: Test fixtures used for frontend layout and unit testing when network connectivity is isolated.
4. **`DERIVED`**: Computed analytical indicators (e.g., Free Cash Flow, Debt/Equity ratios, Split adjustment multipliers) calculated deterministically from raw audited figures.

---

## 4. Lineage & "Where Did This Number Come From?"

The platform implements field-level data provenance stored in `data_provenance`. Every balance sheet, income statement, and cash flow number records:
- `source_document_id`: Foreign key to registered statutory filing.
- `reported_label`: Original line-item title as printed in report (e.g., "Revenue from Sale of Products & Services").
- `reported_value_raw`: Exact string before parsing.
- `reported_unit`: Crores, Lakhs, Millions, or Units.
- `page_number`: Exact PDF page in audited report.
- `table_reference`: Table heading in statutory filing.
- `confidence_score`: Extraction certainty (1.0 for audited filings).
