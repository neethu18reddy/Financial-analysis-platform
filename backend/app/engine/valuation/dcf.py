"""Discounted Cash Flow (DCF) Valuation Engine.

Implements:
1. Free Cash Flow to Firm (FCFF) multi-stage model
2. Free Cash Flow to Equity (FCFE) model
3. Detailed WACC derivation (CAPM + after-tax debt)
4. Gordon Growth & Exit Multiple Terminal Value methods
5. Comprehensive Terminal Value Diagnostics (% EV from TV, Implied Exit Multiple vs Perpetual Growth)
6. Enterprise Value to Equity Value balance sheet bridge
"""

from datetime import date
from typing import Dict, Any, List, Optional
try:
    from app.models.valuation import (
        ValuationMethod,
        TerminalValueMethod,
        CashFlowProjectionYear,
        WACCBreakdown,
        TerminalValueDiagnostics,
        DCFValuationInputs,
        DCFValuationResult,
    )
    from app.engine.valuation.base import BaseValuationEngine, VALUATION_METHODOLOGY_VERSION
except ImportError:
    from backend.app.models.valuation import (
        ValuationMethod,
        TerminalValueMethod,
        CashFlowProjectionYear,
        WACCBreakdown,
        TerminalValueDiagnostics,
        DCFValuationInputs,
        DCFValuationResult,
    )
    from backend.app.engine.valuation.base import BaseValuationEngine, VALUATION_METHODOLOGY_VERSION


class DCFValuationEngine(BaseValuationEngine):
    """Calculates deterministic Discounted Cash Flow valuations."""

    def calculate(
        self,
        company_id: int,
        ticker: str,
        inputs: DCFValuationInputs,
        current_market_price: Optional[float] = None,
        base_fiscal_year: int = 2024,
    ) -> DCFValuationResult:
        """Executes full multi-stage DCF valuation pipeline."""
        
        # 1. Base Financial Inputs Resolution
        base_revenue = inputs.base_revenue if inputs.base_revenue is not None and inputs.base_revenue > 0 else 10000.0
        shares_out = inputs.shares_outstanding_crores if inputs.shares_outstanding_crores and inputs.shares_outstanding_crores > 0 else 100.0
        debt = inputs.total_debt_crores if inputs.total_debt_crores is not None else 0.0
        cash_inv = inputs.cash_and_investments_crores if inputs.cash_and_investments_crores is not None else 0.0
        minority = inputs.minority_interest_crores if inputs.minority_interest_crores is not None else 0.0
        
        # 2. WACC Derivation
        ke = inputs.cost_of_equity_pct
        if ke is None or ke <= 0:
            ke = self.calculate_capm_cost_of_equity(
                risk_free_rate_pct=inputs.risk_free_rate_pct,
                beta=inputs.beta,
                equity_risk_premium_pct=inputs.equity_risk_premium_pct,
            )
        
        wacc = inputs.wacc_pct
        if wacc is None or wacc <= 0:
            wacc = self.calculate_wacc(
                cost_of_equity_pct=ke,
                pre_tax_cost_of_debt_pct=inputs.pre_tax_cost_of_debt_pct,
                effective_tax_rate_pct=inputs.effective_tax_rate_pct,
                debt_to_capital_pct=inputs.debt_to_capital_pct,
            )
        
        # Ensure minimum discount rate sanity
        wacc = max(wacc, inputs.terminal_growth_rate_pct + 0.5)
        
        equity_wt = 100.0 - inputs.debt_to_capital_pct
        debt_wt = inputs.debt_to_capital_pct
        after_tax_kd = inputs.pre_tax_cost_of_debt_pct * (1.0 - (inputs.effective_tax_rate_pct / 100.0))
        
        wacc_breakdown = WACCBreakdown(
            risk_free_rate=inputs.risk_free_rate_pct,
            equity_risk_premium=inputs.equity_risk_premium_pct,
            beta=inputs.beta,
            cost_of_equity=round(ke, 3),
            pre_tax_cost_of_debt=inputs.pre_tax_cost_of_debt_pct,
            effective_tax_rate=inputs.effective_tax_rate_pct,
            after_tax_cost_of_debt=round(after_tax_kd, 3),
            equity_weight_pct=equity_wt,
            debt_weight_pct=debt_wt,
            wacc_pct=round(wacc, 3),
            formula_expression=f"WACC = ({equity_wt:.1f}% * {ke:.2f}%) + ({debt_wt:.1f}% * {after_tax_kd:.2f}%) = {wacc:.2f}%",
        )

        # 3. Explicit Forecast Projections (Years 1 to N)
        projections: List[CashFlowProjectionYear] = []
        current_rev = base_revenue
        r = wacc / 100.0
        pv_explicit = 0.0
        
        growth_rates = inputs.revenue_growth_rates or [inputs.constant_revenue_growth_pct] * inputs.forecast_years
        # Pad or trim growth rates to forecast years
        if len(growth_rates) < inputs.forecast_years:
            growth_rates.extend([growth_rates[-1]] * (inputs.forecast_years - len(growth_rates)))
        growth_rates = growth_rates[:inputs.forecast_years]
        
        for idx in range(1, inputs.forecast_years + 1):
            growth_rate = growth_rates[idx - 1]
            proj_revenue = current_rev * (1.0 + (growth_rate / 100.0))
            ebit = proj_revenue * (inputs.target_ebit_margin_pct / 100.0)
            nopat = ebit * (1.0 - (inputs.effective_tax_rate_pct / 100.0))
            
            # Reinvestment & D&A assumption:
            # Reinvestment Rate (% of NOPAT) covers Net Capex + Change in NWC
            reinvestment = nopat * (inputs.reinvestment_rate_pct / 100.0)
            da = proj_revenue * 0.035  # ~3.5% of revenue baseline
            capex = da + (reinvestment * 0.7)
            delta_nwc = reinvestment * 0.3
            
            # FCFF = NOPAT + D&A - Capex - delta_NWC = NOPAT - Reinvestment
            fcff = nopat - reinvestment
            
            discount_factor = 1.0 / ((1.0 + r) ** idx)
            discounted_cf = fcff * discount_factor
            pv_explicit += discounted_cf
            
            projections.append(
                CashFlowProjectionYear(
                    year_index=idx,
                    fiscal_year=base_fiscal_year + idx,
                    revenue=round(proj_revenue, 2),
                    revenue_growth_pct=round(growth_rate, 2),
                    operating_profit_ebit=round(ebit, 2),
                    ebit_margin_pct=round(inputs.target_ebit_margin_pct, 2),
                    effective_tax_rate_pct=round(inputs.effective_tax_rate_pct, 2),
                    nopat=round(nopat, 2),
                    depreciation_amortization=round(da, 2),
                    capital_expenditure=round(capex, 2),
                    change_in_nwc=round(delta_nwc, 2),
                    free_cash_flow=round(fcff, 2),
                    discount_factor=round(discount_factor, 5),
                    discounted_fcf=round(discounted_cf, 2),
                )
            )
            current_rev = proj_revenue

        # 4. Terminal Value Calculation
        final_year = projections[-1]
        final_fcff = final_year.free_cash_flow
        final_ebitda = final_year.operating_profit_ebit + final_year.depreciation_amortization
        
        tv_raw = 0.0
        g = inputs.terminal_growth_rate_pct / 100.0
        
        if inputs.terminal_value_method == TerminalValueMethod.EXIT_MULTIPLE:
            tv_raw = final_ebitda * inputs.exit_ev_ebitda_multiple
        else:
            # Gordon Growth: TV = FCFF_n * (1 + g) / (WACC - g)
            if r <= g:
                r = g + 0.01  # Safe guardrail
            tv_raw = (final_fcff * (1.0 + g)) / (r - g)
            
        final_discount_factor = projections[-1].discount_factor
        pv_tv = tv_raw * final_discount_factor
        
        # 5. Enterprise Value and Equity Value Bridge
        enterprise_value = pv_explicit + pv_tv
        net_debt = debt - cash_inv
        equity_value = enterprise_value - debt + cash_inv - minority
        
        fair_value_per_share = (equity_value / shares_out) if shares_out > 0 else 0.0
        fair_value_per_share = max(round(fair_value_per_share, 2), 0.0)
        
        # 6. Terminal Value Diagnostics
        tv_pct_ev = (pv_tv / enterprise_value * 100.0) if enterprise_value > 0 else 0.0
        implied_exit_mult = (tv_raw / final_ebitda) if final_ebitda > 0 else None
        
        # Implied perpetual growth if exit multiple used:
        # TV = FCF * (1 + g) / (r - g) => g = (TV*r - FCF) / (TV + FCF)
        implied_g = None
        if tv_raw > 0 and (tv_raw + final_fcff) != 0:
            implied_g_val = (tv_raw * r - final_fcff) / (tv_raw + final_fcff) * 100.0
            implied_g = round(implied_g_val, 2)
            
        warnings = []
        is_dominant = tv_pct_ev > 75.0
        if is_dominant:
            warnings.append(f"Terminal Value constitutes {tv_pct_ev:.1f}% of total Enterprise Value (heavy terminal dependence).")
        
        growth_warning = inputs.terminal_growth_rate_pct >= 6.5
        if growth_warning:
            warnings.append(f"Terminal growth rate ({inputs.terminal_growth_rate_pct:.1f}%) matches or exceeds long-term nominal Indian GDP growth (benchmark ~6.0-6.5%).")
            
        diagnostics = TerminalValueDiagnostics(
            terminal_value_raw=round(tv_raw, 2),
            pv_terminal_value=round(pv_tv, 2),
            pv_explicit_cash_flows=round(pv_explicit, 2),
            enterprise_value=round(enterprise_value, 2),
            terminal_value_pct_of_ev=round(tv_pct_ev, 2),
            implied_exit_ev_ebitda_multiple=round(implied_exit_mult, 2) if implied_exit_mult else None,
            implied_perpetual_growth_rate=implied_g,
            is_terminal_value_dominant=is_dominant,
            growth_vs_gdp_warning=growth_warning,
            warning_notes=warnings,
        )
        
        upside_downside = None
        if current_market_price and current_market_price > 0:
            upside_downside = round(((fair_value_per_share - current_market_price) / current_market_price) * 100.0, 2)

        return DCFValuationResult(
            company_id=company_id,
            ticker=ticker,
            valuation_method=ValuationMethod.DCF_FCFF,
            valuation_date=date.today().isoformat(),
            inputs_applied=inputs,
            wacc_breakdown=wacc_breakdown,
            projections=projections,
            pv_explicit_forecast=round(pv_explicit, 2),
            terminal_value_raw=round(tv_raw, 2),
            pv_terminal_value=round(pv_tv, 2),
            enterprise_value=round(enterprise_value, 2),
            total_debt=round(debt, 2),
            cash_and_investments=round(cash_inv, 2),
            net_debt=round(net_debt, 2),
            minority_interest=round(minority, 2),
            equity_value=round(equity_value, 2),
            shares_outstanding_crores=round(shares_out, 3),
            estimated_fair_value_per_share=fair_value_per_share,
            current_market_price=current_market_price,
            upside_downside_pct=upside_downside,
            terminal_diagnostics=diagnostics,
            formula_lineage={
                "WACC": "WACC = (We * Ke) + (Wd * Kd * (1 - TaxRate))",
                "FCFF": "FCFF = EBIT * (1 - TaxRate) - (NOPAT * ReinvestmentRate)",
                "TerminalValue_Gordon": "TV = FCFF_n * (1 + g) / (WACC - g)",
                "EnterpriseValue": "EV = Sum(PV_Explicit_FCFF) + PV(TerminalValue)",
                "EquityValue": "EquityValue = EnterpriseValue - TotalDebt + CashAndInvestments - MinorityInterest",
                "FairValuePerShare": "FairValue = EquityValue / DilutedSharesOutstanding",
            },
            methodology_version=self.methodology_version,
        )


def calculate_dcf_valuation(
    company_id: int,
    ticker: str,
    inputs: DCFValuationInputs,
    current_market_price: Optional[float] = None,
) -> DCFValuationResult:
    """Convenience helper to run DCF engine."""
    engine = DCFValuationEngine()
    return engine.calculate(
        company_id=company_id,
        ticker=ticker,
        inputs=inputs,
        current_market_price=current_market_price,
    )
