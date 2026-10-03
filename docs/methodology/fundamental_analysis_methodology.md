# Fundamental Analysis Engine Methodology (Phase 2)

**System**: AI-Powered Fundamental Analysis & Financial Decision Intelligence Platform  
**Target Market**: Indian Equities (NSE / BSE Listed Companies)  
**Standard**: Ind AS Compliant / MCA Filings  
**Methodology Version**: `v1.0.0`

---

## 1. Architectural Philosophy: Zero-Math LLM Principle

All analytical metrics, financial ratios, compound growth figures, and multiplicative decompositions in this platform are computed **deterministically** by dedicated backend calculation engines written in Python. 

- **No Hallucinated Ratios**: The LLM is never tasked with dividing numbers, multiplying growth rates, or guessing margins.
- **Traceable Lineage**: Every computed metric produces a `CalculatedMetric` data contract containing the formula expression, resolved numerical inputs, methodology version, unit, and validation state.
- **Single Source of Truth**: The frontend UI and any downstream decision systems retrieve deterministic analytical results exclusively from the backend REST API.

---

## 2. Profitability & Capital Efficiency Engine

### 2.1 Margins
1. **Gross Profit Margin (%)**
   $$\text{Gross Margin} = \frac{\text{Revenue from Operations} - \text{Cost of Goods Sold}}{\text{Revenue from Operations}} \times 100$$
   *COGS Definition*: Cost of Materials Consumed + Purchases of Stock-in-Trade + Changes in Inventories.

2. **EBITDA Margin (%)**
   $$\text{EBITDA Margin} = \frac{\text{Operating Profit} + \text{Depreciation \& Amortization}}{\text{Total Revenue}} \times 100$$

3. **EBIT Margin (%)**
   $$\text{EBIT Margin} = \frac{\text{Operating Profit}}{\text{Total Revenue}} \times 100$$

4. **PAT (Net Profit) Margin (%)**
   $$\text{PAT Margin} = \frac{\text{Profit After Tax}}{\text{Total Revenue}} \times 100$$

### 2.2 Return Ratios
5. **Return on Equity (ROE %)**
   $$\text{ROE} = \frac{\text{Profit After Tax}}{\text{Total Equity}} \times 100$$

6. **Return on Capital Employed (ROCE %)**
   $$\text{ROCE} = \frac{\text{EBIT}}{\text{Total Assets} - \text{Total Current Liabilities}} \times 100$$

7. **Return on Invested Capital (ROIC %)**
   $$\text{NOPAT} = \text{EBIT} \times (1 - t), \quad \text{Invested Capital} = \text{Total Equity} + \text{Total Debt} - \text{Cash \& Equiv}$$
   $$\text{ROIC} = \frac{\text{NOPAT}}{\text{Invested Capital}} \times 100$$
   *Effective Tax Rate $t$*: Computed as $\frac{\text{Tax Expense}}{\text{Profit Before Tax}}$, bound safely in $[0.0, 0.35]$.

8. **Return on Assets (ROA %)**
   $$\text{ROA} = \frac{\text{Profit After Tax}}{\text{Total Assets}} \times 100$$

---

## 3. Growth & Trajectory Engine

### 3.1 Year-over-Year (YoY) Growth
$$\text{YoY Growth (\%)} = \frac{\text{Metric}_{t} - \text{Metric}_{t-1}}{|\text{Metric}_{t-1}|} \times 100$$
- Evaluated for: Total Revenue, EBITDA, EBIT, PAT, Operating Cash Flow (CFO), and Free Cash Flow (FCF).

### 3.2 Compound Annual Growth Rate (CAGR)
$$\text{CAGR (\%)} = \left(\left(\frac{\text{End Value}}{\text{Start Value}}\right)^{\frac{1}{N}} - 1\right) \times 100$$

#### Strict CAGR Boundary Guardrails:
- If $\text{Start Value} \le 0$ or $\text{End Value} \le 0$, CAGR is mathematically non-real/distorted. The engine safely flags `value = null` with an explanatory note: *"CAGR undefined for non-positive start or end values"*.
- If historical periods $N < \text{Target Years}$, the calculation is rejected rather than interpolating or hallucinating missing periods.

---

## 4. Working Capital & Efficiency Engine

### 4.1 Operating Cycles
1. **Days Sales Outstanding (DSO)**
   $$\text{DSO} = \frac{\text{Trade Receivables}}{\text{Revenue from Operations}} \times 365$$
2. **Days Inventory Outstanding (DIO)**
   $$\text{DIO} = \frac{\text{Inventories}}{\text{Cost of Goods Sold}} \times 365$$
3. **Days Payables Outstanding (DPO)**
   $$\text{DPO} = \frac{\text{Trade Payables}}{\text{Cost of Goods Sold}} \times 365$$
4. **Cash Conversion Cycle (CCC)**
   $$\text{CCC} = \text{DSO} + \text{DIO} - \text{DPO} \quad (\text{in days})$$

### 4.2 Liquidity & Turnover
- **Asset Turnover**: $\frac{\text{Total Revenue}}{\text{Total Assets}} \times$
- **Current Ratio**: $\frac{\text{Total Current Assets}}{\text{Total Current Liabilities}} \times$
- **Quick Ratio**: $\frac{\text{Total Current Assets} - \text{Inventories}}{\text{Total Current Liabilities}} \times$

---

## 5. Cash Quality & Earnings Integrity Engine

Financial statements can show robust accounting profits while underlying cash generation deteriorates.

1. **CFO / PAT Ratio**:
   $$\text{CFO to PAT} = \frac{\text{Cash from Operating Activities}}{\text{Profit After Tax}}$$
   - $\ge 1.0$: High quality, cash-backed earnings.
   - $< 0.8$: Potential earnings quality deterioration / working capital blockage.
2. **FCF / PAT Ratio**: $\frac{\text{Free Cash Flow}}{\text{Profit After Tax}}$
3. **Sloan Balance Sheet Accrual Ratio**:
   $$\text{Accruals} = (\Delta \text{Current Assets} - \Delta \text{Cash}) - (\Delta \text{Current Liabilities} - \Delta \text{Short Term Debt}) - \text{Depreciation}$$
   $$\text{Sloan Ratio (\%)} = \frac{\text{Accruals}}{\text{Average Total Assets}} \times 100$$
4. **CFO to Total Debt Coverage**: $\frac{\text{Cash from Operating Activities}}{\text{Total Debt}}$

---

## 6. DuPont Multiplicative Decomposition Engine

### 6.1 3-Step DuPont Identity
$$\text{ROE} = \underbrace{\left(\frac{\text{PAT}}{\text{Revenue}}\right)}_{\text{Net Profit Margin}} \times \underbrace{\left(\frac{\text{Revenue}}{\text{Total Assets}}\right)}_{\text{Asset Turnover}} \times \underbrace{\left(\frac{\text{Total Assets}}{\text{Total Equity}}\right)}_{\text{Equity Multiplier}}$$

### 6.2 5-Step Extended DuPont Identity
$$\text{ROE} = \underbrace{\left(\frac{\text{PAT}}{\text{EBT}}\right)}_{\text{Tax Burden}} \times \underbrace{\left(\frac{\text{EBT}}{\text{EBIT}}\right)}_{\text{Interest Burden}} \times \underbrace{\left(\frac{\text{EBIT}}{\text{Revenue}}\right)}_{\text{Operating Margin}} \times \underbrace{\left(\frac{\text{Revenue}}{\text{Total Assets}}\right)}_{\text{Asset Turnover}} \times \underbrace{\left(\frac{\text{Total Assets}}{\text{Total Equity}}\right)}_{\text{Equity Multiplier}}$$

Both models guarantee strict mathematical consistency and allow investors to pinpoint whether return expansion stems from pricing power, operational efficiency, or financial leverage.

---

## 7. Vertical Common-Size Financial Statements

- **Income Statement**: All revenue and expense line items expressed as a percentage of Total Revenue ($\text{Base} = 100.0\%$).
- **Balance Sheet**: All non-current assets, current assets, equity items, and liabilities expressed as a percentage of Total Assets ($\text{Base} = 100.0\%$).

---

## 8. Versioning & Lineage Contracts

Every API response embeds `methodology_version: "v1.0.0"`. When formulas or accounting treatments evolve, version tags prevent historical recalculation discrepancies.
