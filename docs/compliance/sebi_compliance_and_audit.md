# Financial Compliance, SEBI Regulations, and Audit Lineage

## Regulatory Disclaimers & Compliance Context

### 1. SEBI (Research Analysts) Regulations, 2014
- The platform provides quantitative analytics, financial ratio computation, and factual synthesis of public disclosures.
- It **DOES NOT** provide investment advice, buy/sell/hold recommendations, or target stock price forecasts.
- The platform is designed for research analysts, quantitative researchers, and educational purposes.

### 2. Audit Trail and Data Provenance
To ensure institutional compliance and forensic auditability:
- Every calculated data point must maintain a direct lineage back to:
  1. Source exchange / filing URL.
  2. Document hash (SHA-256).
  3. Precise statement and line item row key.
  4. Ingestion timestamp and filing date.

### 3. Model Explainability and Guardrails
- LLM outputs must never make unsourced assertions regarding corporate solvency, fraud, or performance.
- Any forensic anomaly or flag raised must cite the specific CARO clause, auditor qualification, or ratio threshold breach.
