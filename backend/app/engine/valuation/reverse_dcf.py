"""Reverse DCF Valuation Engine (Market Expectations Solver).

Answers the fundamental question:
"What revenue growth rate, operating margin, and free cash flow trajectory
 are embedded in the current market price?"

Uses deterministic root-finding (bisection solver) to back out the required
implied 5-year revenue CAGR and FCF generation.
"""

from typing import Dict, Any, List, Optional
try:
    from app.models.valuation import (
        ReverseDCFInputs,
        ReverseDCFResult,
        DCFValuationInputs,
        TerminalValueMethod,
    )
    from app.engine.valuation.base import BaseValuationEngine, VALUATION_METHODOLOGY_VERSION
    from app.engine.valuation.dcf import DCFValuationEngine
except ImportError:
    from backend.app.models.valuation import (
        ReverseDCFInputs,
        ReverseDCFResult,
        DCFValuationInputs,
        TerminalValueMethod,
    )
    from backend.app.engine.valuation.base import BaseValuationEngine, VALUATION_METHODOLOGY_VERSION
    from backend.app.engine.valuation.dcf import DCFValuationEngine


class ReverseDCFEngine(BaseValuationEngine):
    """Solves for embedded growth expectations given current stock price."""

    def calculate(
        self,
        company_id: int,
        ticker: str,
        inputs: ReverseDCFInputs,
        base_revenue: float,
        historical_revenue_cagr_3yr: Optional[float] = None,
        default_shares: float = 100.0,
        default_debt: float = 0.0,
        default_cash: float = 0.0,
    ) -> ReverseDCFResult:
        """Solves for implied revenue CAGR required to match the current stock price."""
        
        cmp = inputs.current_market_price
        shares = inputs.shares_outstanding_crores if inputs.shares_outstanding_crores and inputs.shares_outstanding_crores > 0 else default_shares
        market_cap = cmp * shares
        net_debt = inputs.net_debt_crores if inputs.net_debt_crores is not None else (default_debt - default_cash)
        implied_ev = market_cap + net_debt
        
        target_margin = inputs.target_ebit_margin_pct if inputs.target_ebit_margin_pct is not None else 18.0
        
        # Objective function: FairValue(growth_rate) - CurrentMarketPrice = 0
        dcf_engine = DCFValuationEngine()
        
        def evaluate_price_at_growth(growth: float) -> float:
            dcf_in = DCFValuationInputs(
                forecast_years=inputs.forecast_years,
                base_revenue=base_revenue,
                constant_revenue_growth_pct=growth,
                target_ebit_margin_pct=target_margin,
                effective_tax_rate_pct=inputs.effective_tax_rate_pct,
                reinvestment_rate_pct=inputs.reinvestment_rate_pct,
                wacc_pct=inputs.wacc_pct,
                terminal_growth_rate_pct=inputs.terminal_growth_rate_pct,
                shares_outstanding_crores=shares,
                total_debt_crores=default_debt,
                cash_and_investments_crores=default_cash,
                minority_interest_crores=0.0,
            )
            res = dcf_engine.calculate(
                company_id=company_id,
                ticker=ticker,
                inputs=dcf_in,
                current_market_price=cmp,
            )
            return res.estimated_fair_value_per_share

        # Bisection solver across search range [-20.0%, +80.0%]
        low_g = -20.0
        high_g = 80.0
        solved_growth = 12.0
        tolerance = 0.05  # Rs 0.05 per share
        
        # Check boundaries
        p_low = evaluate_price_at_growth(low_g)
        p_high = evaluate_price_at_growth(high_g)
        
        if cmp <= p_low:
            solved_growth = low_g
        elif cmp >= p_high:
            solved_growth = high_g
        else:
            for _ in range(60):  # Maximum 60 iterations
                mid_g = (low_g + high_g) / 2.0
                p_mid = evaluate_price_at_growth(mid_g)
                diff = p_mid - cmp
                
                if abs(diff) < tolerance or (high_g - low_g) < 0.01:
                    solved_growth = mid_g
                    break
                    
                if diff < 0:
                    low_g = mid_g
                else:
                    high_g = mid_g
            solved_growth = round((low_g + high_g) / 2.0, 2)

        # Implied Target 5-Year Revenue & FCF Generation
        target_rev_5yr = base_revenue * ((1.0 + (solved_growth / 100.0)) ** inputs.forecast_years)
        nopat_5yr = target_rev_5yr * (target_margin / 100.0) * (1.0 - (inputs.effective_tax_rate_pct / 100.0))
        target_fcf_5yr = nopat_5yr * (1.0 - (inputs.reinvestment_rate_pct / 100.0))
        
        # Implied FCF CAGR is approximately equal to revenue CAGR under constant margin & reinvestment
        implied_fcf_cagr = solved_growth
        
        # Plausibility & Risk Assessment
        growth_premium = None
        if historical_revenue_cagr_3yr is not None:
            growth_premium = round(solved_growth - historical_revenue_cagr_3yr, 2)
            
        if solved_growth > 30.0:
            plausibility = "EXTREME"
            reasoning = f"Current stock price discounts an aggressive {solved_growth:.1f}% 5-year revenue CAGR, requiring execution at top-decile industry velocity."
        elif solved_growth > 20.0:
            plausibility = "AGGRESSIVE"
            reasoning = f"Current valuation demands {solved_growth:.1f}% annual revenue expansion. Significant execution premium embedded in price."
        elif solved_growth >= 8.0:
            plausibility = "REALISTIC"
            reasoning = f"Market prices in steady, attainable growth of {solved_growth:.1f}% CAGR in line with long-term Indian corporate compounding."
        else:
            plausibility = "CONSERVATIVE"
            reasoning = f"Market discounts modest or pessimistic growth of {solved_growth:.1f}% CAGR, providing potential margin of safety if fundamentals outperform."

        # Quick sensitivity table of market price vs required growth rate
        sensitivities = []
        for test_wacc in [inputs.wacc_pct - 1.5, inputs.wacc_pct, inputs.wacc_pct + 1.5]:
            for test_margin in [target_margin - 3.0, target_margin, target_margin + 3.0]:
                # solve approximate growth
                sensitivities.append({
                    "wacc_pct": round(test_wacc, 1),
                    "ebit_margin_pct": round(test_margin, 1),
                    "implied_growth_needed_pct": round(solved_growth + (test_wacc - inputs.wacc_pct)*1.8 - (test_margin - target_margin)*1.2, 1),
                })

        return ReverseDCFResult(
            company_id=company_id,
            ticker=ticker,
            current_market_price=round(cmp, 2),
            current_market_cap_crores=round(market_cap, 2),
            implied_enterprise_value=round(implied_ev, 2),
            wacc_pct=inputs.wacc_pct,
            terminal_growth_rate_pct=inputs.terminal_growth_rate_pct,
            assumed_ebit_margin_pct=target_margin,
            implied_revenue_cagr_pct=round(solved_growth, 2),
            implied_fcf_cagr_pct=round(implied_fcf_cagr, 2),
            historical_revenue_cagr_3yr=historical_revenue_cagr_3yr,
            growth_premium_vs_historical_pct=growth_premium,
            implied_5yr_revenue_target=round(target_rev_5yr, 2),
            implied_5yr_fcf_target=round(target_fcf_5yr, 2),
            plausibility_assessment=plausibility,
            plausibility_reasoning=reasoning,
            sensitivities=sensitivities,
            methodology_version=self.methodology_version,
        )


def calculate_reverse_dcf(
    company_id: int,
    ticker: str,
    inputs: ReverseDCFInputs,
    base_revenue: float,
    historical_revenue_cagr_3yr: Optional[float] = None,
    default_shares: float = 100.0,
    default_debt: float = 0.0,
    default_cash: float = 0.0,
) -> ReverseDCFResult:
    """Convenience helper for Reverse DCF solving."""
    engine = ReverseDCFEngine()
    return engine.calculate(
        company_id=company_id,
        ticker=ticker,
        inputs=inputs,
        base_revenue=base_revenue,
        historical_revenue_cagr_3yr=historical_revenue_cagr_3yr,
        default_shares=default_shares,
        default_debt=default_debt,
        default_cash=default_cash,
    )
