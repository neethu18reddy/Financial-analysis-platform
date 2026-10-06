# AI Grounding, Claim Verification & Accusation Interception Methodology

## 1. Grounding Taxonomy

Every analytical claim synthesized by the AI Analyst pipeline is classified into one of four deterministic states:

1. **`VERIFIED_CITATION`**: The claim directly quotes or references an exact paragraph, table, or disclosure from a statutory Annual Report PDF with validated page number, section, and SHA-256 provenance hash.
2. **`DERIVED_METRIC`**: The claim represents a quantitative relationship computed directly by the deterministic fundamental, forensic, or valuation engines (e.g., ROCE, Beneish M-Score, DCF fair value).
3. **`QUALITATIVE_SYNTHESIS`**: High-level contextual synthesis linking industry backdrop with verified data.
4. **`UNSUPPORTED_REJECTED`**: Any claim asserting factual specifics that cannot be tied to a database metric or statutory citation is rejected or sanitized.

---

## 2. Accusation Sanitizer & Defamation Guardrail

In financial analysis, statistical anomaly models (like Beneish M-Score > -1.78 or Piotroski F-Score <= 3) indicate **screening flags** and **potential areas for investigation**, not definitive evidence of fraud or criminal malfeasance.

The `CitationAndClaimValidator` automatically scans generated text for inflammatory or unsubstantiated accusations:
- **Forbidden Phrases**: "committed fraud", "guilty of accounting manipulation", "cooked the books", "illegal transactions", "defrauded investors".
- **Sanitization Transformation**: Replaces inflammatory language with regulatory-compliant phrasing:
  > *"Statistical forensic screening indicators (such as Beneish M-score or accrual divergence) reflect accounting anomalies that warrant deeper audit investigation rather than conclusive findings."*

---

## 3. Point-in-Time (PIT) Temporal Guardrails

To ensure authentic historical backtesting:
- All financial statements, corporate actions, and annual report chunks indexed after the specified `as_of_year` are strictly excluded from the query context.
- The pipeline verifies that `max(period.fiscal_year) <= as_of_year` before passing context to the reasoner.
- The response explicitly enumerates excluded future periods to confirm zero lookahead leakage.
