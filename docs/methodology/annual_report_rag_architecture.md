# Annual Report Intelligence & Retrieval-Augmented Generation (RAG) Subsystem

**Subsystem Version**: `v1.0.0-phase6`  
**Target Market**: Indian Equities (NSE / BSE)  
**Governing Regulations**: SEBI (LODR) Regulations, 2015 (Reg 34), Companies Act, 2013 (Section 134, 143), ICAI Ind AS Standards

---

## 1. Executive Summary & Zero-Hallucination Mandate

In institutional equity research, hallucinated metrics, fabricated management statements, or inaccurate page citations are catastrophic. General-purpose LLM chatbots routinely generate confident assertions without grounded citations.

The **Antigravity Annual Report Intelligence Engine** solves this with a deterministic, multi-stage RAG pipeline where:
1. Every extracted statement is permanently bound to its **exact 1-indexed physical PDF page number**.
2. Documents and chunks carry cryptographic **SHA-256 fingerprints** for tamper-proof provenance.
3. Chunks are categorized into statutory Indian annual report sections (e.g., MD&A, Board's Report, Independent Auditor's Report, Notes to Accounts).
4. Embeddings and similarity search operate deterministically, scoring financial domain semantics with keyword boosts.
5. All retrieval outputs generate structured `EvidenceCitation` objects with exact verbatim quotes and relevance scores.

---

## 2. Ingestion & Retrieval Pipeline Architecture

```
STATUTORY ANNUAL REPORT (PDF)
           │
           ▼
[1. Cryptographic SHA-256 Hashing] ──► Unique Document Identity
           │
           ▼
[2. PDF Text & Table Extraction] ──► Exact 1-Indexed Physical Pages
           │
           ▼
[3. Statutory Section Detector] ──► LODR Reg 34 / Companies Act 2013 Taxonomy
           │
           ▼
[4. Financial Semantic Chunker] ──► 250-Word Windows, 40-Word Overlap, Provenance Hash
           │
           ▼
[5. Dense Embedding Vectorizer] ──► Normalized 384-Dim Financial Feature Hasher
           │
           ▼
[6. In-Memory / DB Vector Store] ──► Cosine Similarity + Multi-Field Metadata Filtering
           │
           ▼
[7. Retrieval & Evidence Service] ──► Verifiable Page-Level EvidenceCitation Objects
```

---

## 3. Statutory Indian Annual Report Section Taxonomy

Under Indian corporate law and SEBI regulations, annual reports adhere to a standardized structure. The parser automatically detects and tags pages into:

| Canonical Section Name | Statutory Mandate / Purpose |
|---|---|
| `DIRECTORS_REPORT` | Section 134 of Companies Act, 2013; capex plans, dividends, operations summary. |
| `MANAGEMENT_DISCUSSION_AND_ANALYSIS` | Schedule V, Regulation 34(3) of SEBI LODR; segment performance, risks, outlook. |
| `CORPORATE_GOVERNANCE_REPORT` | Regulation 34(3) and Schedule V of SEBI LODR; board composition, committees. |
| `BUSINESS_RESPONSIBILITY_AND_SUSTAINABILITY` | SEBI BRSR mandate for top 1,000 listed entities. |
| `INDEPENDENT_AUDITORS_REPORT` | Section 143 of Companies Act, 2013 & CARO 2020; Key Audit Matters (KAMs), IFCoFR opinion. |
| `CONSOLIDATED_FINANCIAL_STATEMENTS` | Balance Sheet, Profit & Loss, Cash Flow Statements under Ind AS. |
| `NOTES_TO_CONSOLIDATED_FINANCIAL_STATEMENTS` | Detailed accounting policies, segment reporting (Ind AS 108). |
| `RELATED_PARTY_DISCLOSURES` | Ind AS 24 & Regulation 23 of SEBI LODR; transactions with KMP and group entities. |
| `RISK_MANAGEMENT_AND_INTERNAL_CONTROLS` | Enterprise risk governance and internal financial controls over financial reporting. |

---

## 4. Financial Semantic Chunking & Overlap Calibration

Traditional fixed-character chunkers split words mid-sentence or tear financial statement rows apart. Our `FinancialChunkerEngine`:
- Targets **250 words per chunk** with **40 words of semantic overlap**.
- Preserves paragraph and sentence boundaries.
- Retains section headers and physical page numbers across boundaries.
- Generates a unique `provenance_hash = SHA256(document_hash + page_number + chunk_index)`.

---

## 5. Pluggable & Deterministic Embeddings

The platform features a clean `BaseEmbeddingProvider` abstraction with a default `DeterministicLocalEmbeddingProvider`:
- **Dimensionality**: 384 dimensions.
- **Normalization**: Unit $L_2$ norm ($\|v\|_2 = 1.0$).
- **Domain Weighting**: Boosts critical financial research keywords (`capex`, `ebitda`, `auditor`, `contingent`, `liability`, `npa`, `slippages`, `borrowings`, `guarantees`, `buyback`, `remuneration`).
- **Zero Third-Party Dependency**: Instantaneous execution in local and CI/CD environments without external network latency or API rate limits.
