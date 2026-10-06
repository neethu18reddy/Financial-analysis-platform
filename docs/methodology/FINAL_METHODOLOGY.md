# Final Comprehensive Financial Methodology Reference

## 1. Accounting Framework & Normalization

- **Accounting Standards**: Mandates compliance with Ind AS (Indian Accounting Standards convergent with IFRS) under Companies Act 2013, with legacy support for Indian GAAP.
- **Unit Normalization**: Standardizes all monetary items to canonical Indian Crores (₹ 1 Crore = ₹ 10,000,000 INR).
- **Consolidated vs Standalone Separation**: Ensures strict boundary isolation between consolidated group numbers and standalone operating metrics.

---

## 2. Analytical Subsystems

### 2.1 Fundamental Engine
- **Profitability**: EBITDA Margin, EBIT Margin, PAT Margin, ROCE (EBIT / Capital Employed), ROIC.
- **DuPont 5-Step Decomposition**:
  $$\text{ROE} = \text{Tax Burden} \times \text{Interest Burden} \times \text{Operating Margin} \times \text{Asset Turnover} \times \text{Equity Multiplier}$$
- **Cash Flow Quality**: CFO / EBITDA ratio, CFO / PAT conversion, Free Cash Flow Yield.
- **Working Capital Cycles**: Days Sales Outstanding (DSO), Days Inventory Outstanding (DIO), Days Payable Outstanding (DPO), Cash Conversion Cycle (CCC).

### 2.2 Forensic Intelligence Engine
- **Beneish 8-Variable M-Score**:
  $$M = -4.84 + 0.920 \cdot \text{DSRI} + 0.528 \cdot \text{GMI} + 0.404 \cdot \text{AQI} + 0.892 \cdot \text{SGI} + 0.115 \cdot \text{DEPI} - 0.172 \cdot \text{SGAI} + 4.037 \cdot \text{TATA} + 0.0327 \cdot \text{LVGI}$$
- **Piotroski 9-Point F-Score**: Binary scoring across Profitability, Leverage/Liquidity, and Operating Efficiency.
- **Altman Z''-Score (Emerging Markets)**:
  $$Z'' = 6.56 X_1 + 3.26 X_2 + 6.72 X_3 + 1.05 X_4$$

### 2.3 Valuation & DCF Engine
- **Free Cash Flow to Firm (FCFF)**: 2-stage and 3-stage explicit forecasting.
- **WACC Formulation**: Capital Asset Pricing Model (CAPM) with India risk-free rate ($R_f \approx 7.0\%$) and equity risk premium ($ERP \approx 6.0\%$).
- **Reverse DCF**: Numerical root-finding determining market-implied revenue growth and operating margin hurdles embedded in Current Market Price (CMP).
- **Financial Institutions**: Specialised Dividend Discount Model (DDM) and Justified P/B framework.

### 2.4 Document Intelligence & Annual Report RAG
- **Structured Page Parsing**: SHA-256 document fingerprinting and page-boundary preservation.
- **Deterministic Embeddings**: 64-dimensional financial semantic vector projections with cosine similarity retrieval.

### 2.5 AI Analyst & Grounding Layer (Phase 7)
- **Zero-Hallucination Claim Validation**: Every analytical assertion is grounded against structured engine outputs or verified statutory PDF citations.
- **Accusation Sanitization**: Intercepts unverified claims and frames statistical anomalies as screening flags.
- **Management "Said vs Did"**: Quantitative tracking of management commitments vs subsequent audited delivery.
- **Point-in-Time Temporal Guardrails**: Guarantees zero lookahead bias during historical simulations.
