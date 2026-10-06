# Phase 4 Valuation Engine Methodology & Mathematical Formulations

**Version**: `v1.0.0-phase4`  
**Engine Package**: `backend.app.engine.valuation`  
**Standard**: Pure Deterministic Calculations, Zero LLM Math Delegation, Explicit Assumption Auditability.

---

## 1. Valuation Architecture & Modular Design

The platform establishes an extensible `BaseValuationEngine` abstraction to support diverse corporate structures without architectural refactoring:
- **Industrial & Commercial Corporates**: Multi-Stage Free Cash Flow to Firm (FCFF) Discounted Cash Flow (DCF).
- **Market Expectations Modeling**: Root-finding Reverse DCF Expectation Solver.
- **Relative Pricing Benchmarks**: Multi-Metric Relative Multiples (P/E, EV/EBITDA, P/B, EV/Sales) with historical percentiles.
- **Scenario Risk Modeling**: Explicit Bear, Base, Bull probabilistic simulations.
- **Fragility Diagnostics**: 2D Sensitivity Matrices & Terminal Value Diagnostics.
- **Financial Institutions (Banks / NBFCs)**: Multi-Stage Dividend Discount Model (DDM) with Tier-1 Capital Adequacy retention & Gordon Justified Price-to-Book.
- **Conglomerates**: Multi-Segment Sum-of-the-Parts (SOTP) foundation.

---

## 2. Multi-Stage Free Cash Flow to Firm (FCFF) DCF

### 2.1 Cash Flow Construction
$$\text{NOPAT}_t = \text{EBIT}_t \times (1 - \tau)$$
$$\text{FCFF}_t = \text{NOPAT}_t + \text{D\&A}_t - \text{Capex}_t - \Delta\text{NWC}_t$$
$$\text{Reinvestment Rate} = \frac{\text{Capex}_t + \Delta\text{NWC}_t - \text{D\&A}_t}{\text{NOPAT}_t}$$
$$\text{FCFF}_t = \text{NOPAT}_t \times (1 - \text{Reinvestment Rate})$$

Where:
- $\text{EBIT}_t = \text{Revenue}_t \times \text{Operating Margin}_t$
- $\tau = \text{Effective Corporate Tax Rate (Benchmark: 25.17\% under Indian Sec 115BAA)}$

### 2.2 Weighted Average Cost of Capital (WACC)
$$\text{Cost of Equity } (K_e) = R_f + \beta \times \text{ERP}$$
$$\text{After-Tax Cost of Debt } (K_{d,\text{after}}) = K_d \times (1 - \tau)$$
$$\text{WACC} = \left(\frac{E}{E + D} \times K_e\right) + \left(\frac{D}{E + D} \times K_{d,\text{after}}\right)$$

*Default Indian Benchmarks*:
- $R_f = 7.10\%$ (10-Year Indian Sovereign G-Sec Benchmark Yield)
- $\text{ERP} = 6.00\%$ (Equity Risk Premium for Indian Equities)
- $\beta = \text{Target / Sector Unlevered Beta adjusted for Capital Structure}$

### 2.3 Terminal Value Methods
1. **Gordon Growth Model**:
   $$\text{Terminal Value} = \frac{\text{FCFF}_n \times (1 + g)}{\text{WACC} - g}$$
   *Singularity Guardrail*: Engine strictly rejects $g \ge \text{WACC}$.
2. **Exit Multiple Model**:
   $$\text{Terminal Value} = \text{EBITDA}_n \times \text{Target EV/EBITDA Multiple}$$

### 2.4 Enterprise Value to Equity Value Bridge
$$\text{Enterprise Value } (\text{EV}) = \sum_{t=1}^n \frac{\text{FCFF}_t}{(1 + \text{WACC})^t} + \frac{\text{Terminal Value}}{(1 + \text{WACC})^n}$$
$$\text{Net Debt} = \text{Total Borrowings} - (\text{Cash} + \text{Bank Balances} + \text{Current Investments})$$
$$\text{Equity Value} = \text{EV} - \text{Total Debt} + \text{Cash \& Liquid Investments} - \text{Minority Interest}$$
$$\text{Fair Value Per Share} = \frac{\text{Equity Value}}{\text{Diluted Shares Outstanding}}$$

---

## 3. Reverse DCF (Market Expectation Solver)

### Objective Formulation
Given current market price $P_{\text{market}}$, solve for implied 5-year revenue CAGR ($g_{\text{implied}}$) such that:
$$f(g_{\text{implied}}) = \text{FairValue}(g_{\text{implied}}) - P_{\text{market}} \equiv 0$$

### Solver Algorithm
Employs a deterministic bisection root-finding algorithm over search space $g \in [-20.0\%, +80.0\%]$ with numerical convergence tolerance $\epsilon = \text{₹}0.05$.

### Plausibility Classification Taxonomy
- **$g > 30.0\%$**: `EXTREME` (Market demands top-decile industry velocity).
- **$20.0\% < g \le 30.0\%$**: `AGGRESSIVE` (High execution premium embedded).
- **$8.0\% \le g \le 20.0\%$**: `REALISTIC` (Attainable long-term Indian corporate compounding).
- **$g < 8.0\%$**: `CONSERVATIVE` (Pessimistic pricing offering margin of safety).

---

## 4. Multi-Scenario Analysis (Bear, Base, Bull)

| Scenario | Weight | Growth Assumption | Margin Assumption | WACC Adjustment | Terminal Growth |
|---|---|---|---|---|---|
| **BEAR** | 25% | $0.6 \times \text{Base Growth}$ | $\text{Base Margin} - 350\text{ bps}$ | $\text{Base WACC} + 125\text{ bps}$ | $\text{Base } g - 150\text{ bps}$ |
| **BASE** | 50% | Consensus Baseline | Normalized Historical | Baseline WACC | Baseline $g$ |
| **BULL** | 25% | $1.35 \times \text{Base Growth}$ | $\text{Base Margin} + 250\text{ bps}$ | $\text{Base WACC} - 75\text{ bps}$ | $\text{Base } g + 100\text{ bps}$ |

$$\text{Probability-Weighted Fair Value} = (0.25 \times \text{FV}_{\text{Bear}}) + (0.50 \times \text{FV}_{\text{Base}}) + (0.25 \times \text{FV}_{\text{Bull}})$$

---

## 5. Financial Institutions (Banks / NBFCs) Valuation

### Fundamental Exclusion Rule
Industrial FCFF is **strictly prohibited** for banking institutions because deposits/borrowings constitute raw material inventory and interest expense is cost of goods sold.

### Multi-Stage Dividend Discount Model (DDM)
$$\text{EPS}_t = \text{Book Value}_{t-1} \times \text{ROE}_t$$
$$\text{Dividends}_t = \text{EPS}_t \times (1 - \text{Tier-1 Retention Rate})$$
$$\text{Book Value}_t = \text{Book Value}_{t-1} + (\text{EPS}_t - \text{Dividends}_t)$$
$$\text{DDM Fair Value} = \sum_{t=1}^n \frac{\text{Dividends}_t}{(1 + K_e)^t} + \frac{\text{Dividends}_n \times (1 + g)}{(K_e - g) \times (1 + K_e)^n}$$

### Gordon Justified Price-to-Book (P/B)
$$\text{Justified P/B} = \frac{\text{ROE} - g}{K_e - g}$$
$$\text{Justified Fair Value} = \text{Current Book Value Per Share} \times \text{Justified P/B}$$
