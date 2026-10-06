"""Multi-Scenario Valuation Engine (Bear, Base, Bull).

Implements explicit, reproducible valuation cases:
- Bear Case (Conservative demand, margin pressure, elevated cost of capital)
- Base Case (Normalized compounding, steady margins, baseline WACC)
- Bull Case (Market share gains, margin expansion, optimized capital structure)

Produces probability-weighted fair value and risk/reward asymmetry assessments.
"""

from typing import Dict, Any, List, Optional
try:
    from app.models.valuation import (
        ScenarioType,
        ScenarioCase,
        ScenarioAnalysisResult,
        DCFValuationInputs,
    )
    from app.engine.valuation.base import BaseValuationEngine, VALUATION_METHODOLOGY_VERSION
    from app.engine.valuation.dcf import DCFValuationEngine
except ImportError:
    from backend.app.models.valuation import (
        ScenarioType,
        ScenarioCase,
        ScenarioAnalysisResult,
        DCFValuationInputs,
    )
    from backend.app.engine.valuation.base import BaseValuationEngine, VALUATION_METHODOLOGY_VERSION
    from backend.app.engine.valuation.dcf import DCFValuationEngine


class ScenarioValuationEngine(BaseValuationEngine):
    """Executes multi-scenario DCF simulations."""

    def calculate(
        self,
        company_id: int,
        ticker: str,
        current_market_price: float,
        base_revenue: float,
        shares_outstanding_crores: float,
        total_debt_crores: float = 0.0,
        cash_and_investments_crores: float = 0.0,
        base_growth_pct: float = 12.0,
        base_margin_pct: float = 18.0,
        base_wacc_pct: float = 11.5,
        base_terminal_growth_pct: float = 5.0,
    ) -> ScenarioAnalysisResult:
        """Runs Bear (25%), Base (50%), and Bull (25%) scenarios."""
        
        dcf_engine = DCFValuationEngine()
        scenarios: List[ScenarioCase] = []
        
        # 1. BEAR SCENARIO (25% Weight)
        bear_growth = max(base_growth_pct * 0.6, 2.0)
        bear_margin = max(base_margin_pct - 3.5, 5.0)
        bear_wacc = base_wacc_pct + 1.25
        bear_tg = max(base_terminal_growth_pct - 1.5, 3.0)
        
        bear_dcf_in = DCFValuationInputs(
            forecast_years=5,
            base_revenue=base_revenue,
            constant_revenue_growth_pct=bear_growth,
            target_ebit_margin_pct=bear_margin,
            wacc_pct=bear_wacc,
            terminal_growth_rate_pct=bear_tg,
            shares_outstanding_crores=shares_outstanding_crores,
            total_debt_crores=total_debt_crores,
            cash_and_investments_crores=cash_and_investments_crores,
        )
        bear_res = dcf_engine.calculate(
            company_id=company_id,
            ticker=ticker,
            inputs=bear_dcf_in,
            current_market_price=current_market_price,
        )
        scenarios.append(
            ScenarioCase(
                scenario_type=ScenarioType.BEAR,
                probability_weight_pct=25.0,
                revenue_growth_pct=round(bear_growth, 2),
                ebit_margin_pct=round(bear_margin, 2),
                wacc_pct=round(bear_wacc, 2),
                terminal_growth_pct=round(bear_tg, 2),
                estimated_fair_value_per_share=bear_res.estimated_fair_value_per_share,
                upside_downside_pct=bear_res.upside_downside_pct,
                key_assumptions=[
                    f"Growth decelerates to {bear_growth:.1f}% due to macro headwinds or competitive friction.",
                    f"Operating margin contracts by 350 bps to {bear_margin:.1f}%.",
                    f"Discount rate elevated to {bear_wacc:.2f}% reflecting higher risk premium.",
                ],
            )
        )

        # 2. BASE SCENARIO (50% Weight)
        base_dcf_in = DCFValuationInputs(
            forecast_years=5,
            base_revenue=base_revenue,
            constant_revenue_growth_pct=base_growth_pct,
            target_ebit_margin_pct=base_margin_pct,
            wacc_pct=base_wacc_pct,
            terminal_growth_rate_pct=base_terminal_growth_pct,
            shares_outstanding_crores=shares_outstanding_crores,
            total_debt_crores=total_debt_crores,
            cash_and_investments_crores=cash_and_investments_crores,
        )
        base_res = dcf_engine.calculate(
            company_id=company_id,
            ticker=ticker,
            inputs=base_dcf_in,
            current_market_price=current_market_price,
        )
        scenarios.append(
            ScenarioCase(
                scenario_type=ScenarioType.BASE,
                probability_weight_pct=50.0,
                revenue_growth_pct=round(base_growth_pct, 2),
                ebit_margin_pct=round(base_margin_pct, 2),
                wacc_pct=round(base_wacc_pct, 2),
                terminal_growth_pct=round(base_terminal_growth_pct, 2),
                estimated_fair_value_per_share=base_res.estimated_fair_value_per_share,
                upside_downside_pct=base_res.upside_downside_pct,
                key_assumptions=[
                    f"Consensus steady growth of {base_growth_pct:.1f}% CAGR.",
                    f"Normalized operating margin sustained at {base_margin_pct:.1f}%.",
                    f"Baseline WACC of {base_wacc_pct:.2f}% and perpetual terminal growth of {base_terminal_growth_pct:.1f}%.",
                ],
            )
        )

        # 3. BULL SCENARIO (25% Weight)
        bull_growth = base_growth_pct * 1.35
        bull_margin = min(base_margin_pct + 2.5, 45.0)
        bull_wacc = max(base_wacc_pct - 0.75, 9.0)
        bull_tg = min(base_terminal_growth_pct + 1.0, 6.0)
        
        bull_dcf_in = DCFValuationInputs(
            forecast_years=5,
            base_revenue=base_revenue,
            constant_revenue_growth_pct=bull_growth,
            target_ebit_margin_pct=bull_margin,
            wacc_pct=bull_wacc,
            terminal_growth_rate_pct=bull_tg,
            shares_outstanding_crores=shares_outstanding_crores,
            total_debt_crores=total_debt_crores,
            cash_and_investments_crores=cash_and_investments_crores,
        )
        bull_res = dcf_engine.calculate(
            company_id=company_id,
            ticker=ticker,
            inputs=bull_dcf_in,
            current_market_price=current_market_price,
        )
        scenarios.append(
            ScenarioCase(
                scenario_type=ScenarioType.BULL,
                probability_weight_pct=25.0,
                revenue_growth_pct=round(bull_growth, 2),
                ebit_margin_pct=round(bull_margin, 2),
                wacc_pct=round(bull_wacc, 2),
                terminal_growth_pct=round(bull_tg, 2),
                estimated_fair_value_per_share=bull_res.estimated_fair_value_per_share,
                upside_downside_pct=bull_res.upside_downside_pct,
                key_assumptions=[
                    f"Accelerated market share gains pushing growth to {bull_growth:.1f}%.",
                    f"Operating leverage expands margin by +250 bps to {bull_margin:.1f}%.",
                    f"WACC contracts to {bull_wacc:.2f}% due to lower beta and balance sheet deleveraging.",
                ],
            )
        )

        # 4. Probability-Weighted Fair Value
        weighted_fair_val = (
            (bear_res.estimated_fair_value_per_share * 0.25)
            + (base_res.estimated_fair_value_per_share * 0.50)
            + (bull_res.estimated_fair_value_per_share * 0.25)
        )
        expected_upside = round(((weighted_fair_val - current_market_price) / current_market_price) * 100.0, 2) if current_market_price > 0 else 0.0
        
        # Risk / Reward Skew
        bear_drawdown = abs(min(bear_res.upside_downside_pct or 0.0, 0.0))
        bull_upside = max(bull_res.upside_downside_pct or 0.0, 0.0)
        
        if bull_upside > (bear_drawdown * 1.5):
            skew = "FAVORABLE"
        elif bear_drawdown > (bull_upside * 1.5):
            skew = "UNFAVORABLE"
        else:
            skew = "SYMMETRIC"

        return ScenarioAnalysisResult(
            company_id=company_id,
            ticker=ticker,
            current_market_price=round(current_market_price, 2),
            scenarios=scenarios,
            probability_weighted_fair_value=round(weighted_fair_val, 2),
            expected_upside_downside_pct=expected_upside,
            risk_reward_skew=skew,
            methodology_version=self.methodology_version,
        )


def calculate_scenario_analysis(
    company_id: int,
    ticker: str,
    current_market_price: float,
    base_revenue: float,
    shares_outstanding_crores: float,
    total_debt_crores: float = 0.0,
    cash_and_investments_crores: float = 0.0,
    base_growth_pct: float = 12.0,
    base_margin_pct: float = 18.0,
    base_wacc_pct: float = 11.5,
    base_terminal_growth_pct: float = 5.0,
) -> ScenarioAnalysisResult:
    """Convenience helper for scenario analysis."""
    engine = ScenarioValuationEngine()
    return engine.calculate(
        company_id=company_id,
        ticker=ticker,
        current_market_price=current_market_price,
        base_revenue=base_revenue,
        shares_outstanding_crores=shares_outstanding_crores,
        total_debt_crores=total_debt_crores,
        cash_and_investments_crores=cash_and_investments_crores,
        base_growth_pct=base_growth_pct,
        base_margin_pct=base_margin_pct,
        base_wacc_pct=base_wacc_pct,
        base_terminal_growth_pct=base_terminal_growth_pct,
    )
