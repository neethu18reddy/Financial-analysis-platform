# Deterministic Financial Methodology & Forensic Calculations

## Core Philosophy
Every formula is explicitly defined in immutable Python algorithms. Under no circumstances does the LLM infer, interpolate, or compute mathematical indicators.

## Key Financial Formulae Specifications

### 1. Capital Efficiency & Returns
- **Return on Capital Employed (ROCE)**:
  $$\text{ROCE} = \frac{\text{EBIT}}{\text{Total Assets} - \text{Current Liabilities}}$$
- **Return on Equity (ROE)**:
  $$\text{ROE} = \frac{\text{Net Income}}{\text{Shareholders' Equity}}$$
- **Return on Invested Capital (ROIC)**:
  $$\text{ROIC} = \frac{\text{NOPAT}}{\text{Total Debt} + \text{Total Equity} - \text{Cash \& Equivalents}}$$

### 2. DuPont 3-Step and 5-Step Breakdown
- **3-Step DuPont**:
  $$\text{ROE} = \left(\frac{\text{Net Profit}}{\text{Revenue}}\right) \times \left(\frac{\text{Revenue}}{\text{Total Assets}}\right) \times \left(\frac{\text{Total Assets}}{\text{Equity}}\right)$$
  - Net Profit Margin $\times$ Asset Turnover $\times$ Equity Multiplier.

### 3. Forensic & Solvency Scoring
- **Piotroski F-Score (9-Point Scale)**:
  - Profitability: Positive ROA, Positive CFO, CFO > Net Income, Change in ROA > 0.
  - Leverage & Liquidity: Change in Leverage < 0, Change in Current Ratio > 0, No new shares issued.
  - Operating Efficiency: Change in Gross Margin > 0, Change in Asset Turnover > 0.
- **Altman Z''-Score for Emerging Markets (Indian Manufacturing & Services)**:
  $$Z'' = 6.56X_1 + 3.26X_2 + 6.72X_3 + 1.05X_4$$
  - $X_1$: Working Capital / Total Assets
  - $X_2$: Retained Earnings / Total Assets
  - $X_3$: EBIT / Total Assets
  - $X_4$: Book Value of Equity / Total Liabilities

### 4. Working Capital & Cash Conversion Cycle (CCC)
- $\text{DIO} = \frac{\text{Average Inventory}}{\text{COGS}} \times 365$
- $\text{DSO} = \frac{\text{Average Receivables}}{\text{Revenue}} \times 365$
- $\text{DPO} = \frac{\text{Average Payables}}{\text{Cost of Goods Sold}} \times 365$
- $\text{CCC} = \text{DIO} + \text{DSO} - \text{DPO}$
