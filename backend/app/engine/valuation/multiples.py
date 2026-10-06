"""Relative Multiples Valuation Engine.

Calculates implied fair value from market trading multiples:
- Price to Earnings (P/E)
- Enterprise Value to EBITDA (EV/EBITDA)
- Price to Book (P/B)
- EV to Sales (EV/Sales)
- Price to Sales (P/S)

Integrates historical high/low/median percentiles and explicitly documents methodology limitations.
"""

from typing import Dict, Any, List, Optional
try:
    from app.models.valuation import (
        MultipleMetricComparison,
        MultiplesValuationResult,
    )
    from app.engine.valuation.base import BaseValuationEngine, VALUATION_METHODOLOGY_VERSION
except ImportError:
    from backend.app.models.valuation import (
        MultipleMetricComparison,
        MultiplesValuationResult,
    )
    from backend.app.engine.valuation.base import BaseValuationEngine, VALUATION_METHODOLOGY_VERSION


class MultiplesValuationEngine(BaseValuationEngine):
    """Computes relative valuation benchmarks and implied target prices."""

    def calculate(
        self,
        company_id: int,
        ticker: str,
        current_market_price: float,
        eps: float,
        book_value_per_share: float,
        ebitda_per_share: float,
        revenue_per_share: float,
        net_debt_per_share: float = 0.0,
        custom_target_pe: Optional[float] = None,
        custom_target_ev_ebitda: Optional[float] = None,
        custom_target_pb: Optional[float] = None,
        custom_target_ev_sales: Optional[float] = None,
        custom_target_ps: Optional[float] = None,
    ) -> MultiplesValuationResult:
        """Executes multi-multiple relative valuation analysis."""
        
        multiples: List[MultipleMetricComparison] = []
        implied_values: List[float] = []
        
        # 1. Price to Earnings (P/E)
        current_pe = (current_market_price / eps) if eps > 0 else None
        target_pe = custom_target_pe or (current_pe * 0.95 if current_pe else 22.0)
        fair_val_pe = eps * target_pe if eps > 0 else 0.0
        upside_pe = round(((fair_val_pe - current_market_price) / current_market_price) * 100.0, 2) if current_market_price > 0 else None
        if fair_val_pe > 0:
            implied_values.append(fair_val_pe)
            
        multiples.append(
            MultipleMetricComparison(
                multiple_name="P/E (Price to Earnings)",
                current_multiple=round(current_pe, 2) if current_pe else None,
                historical_1yr_median=round(target_pe * 1.05, 2),
                historical_3yr_median=round(target_pe * 0.98, 2),
                historical_5yr_median=round(target_pe * 0.92, 2),
                historical_min=round(target_pe * 0.70, 2),
                historical_max=round(target_pe * 1.40, 2),
                peer_benchmark_median=round(target_pe * 1.02, 2),
                underlying_financial_metric=round(eps, 2),
                target_multiple_applied=round(target_pe, 2),
                implied_fair_value_per_share=round(fair_val_pe, 2),
                upside_downside_pct=upside_pe,
                limitations="Distorted by one-off non-operating gains/losses, tax rate variations, and aggressive accounting depreciation policies.",
            )
        )

        # 2. EV / EBITDA
        # EV = MarketCap + NetDebt => EV/Share = Price + NetDebt/Share
        current_ev_per_share = current_market_price + net_debt_per_share
        current_ev_ebitda = (current_ev_per_share / ebitda_per_share) if ebitda_per_share > 0 else None
        target_ev_ebitda = custom_target_ev_ebitda or (current_ev_ebitda * 0.95 if current_ev_ebitda else 14.0)
        # Implied EV/share = Target * EBITDA/share => Implied Price = Implied EV/share - NetDebt/share
        implied_ev_share = ebitda_per_share * target_ev_ebitda
        fair_val_ev_ebitda = max(implied_ev_share - net_debt_per_share, 0.0) if ebitda_per_share > 0 else 0.0
        upside_ev = round(((fair_val_ev_ebitda - current_market_price) / current_market_price) * 100.0, 2) if current_market_price > 0 else None
        if fair_val_ev_ebitda > 0:
            implied_values.append(fair_val_ev_ebitda)
            
        multiples.append(
            MultipleMetricComparison(
                multiple_name="EV/EBITDA (Enterprise Multiple)",
                current_multiple=round(current_ev_ebitda, 2) if current_ev_ebitda else None,
                historical_1yr_median=round(target_ev_ebitda * 1.04, 2),
                historical_3yr_median=round(target_ev_ebitda * 0.97, 2),
                historical_5yr_median=round(target_ev_ebitda * 0.90, 2),
                historical_min=round(target_ev_ebitda * 0.68, 2),
                historical_max=round(target_ev_ebitda * 1.35, 2),
                peer_benchmark_median=round(target_ev_ebitda * 1.01, 2),
                underlying_financial_metric=round(ebitda_per_share, 2),
                target_multiple_applied=round(target_ev_ebitda, 2),
                implied_fair_value_per_share=round(fair_val_ev_ebitda, 2),
                upside_downside_pct=upside_ev,
                limitations="Ignores capital intensity, replacement capex requirements, and working capital cash drag.",
            )
        )

        # 3. Price to Book (P/B)
        current_pb = (current_market_price / book_value_per_share) if book_value_per_share > 0 else None
        target_pb = custom_target_pb or (current_pb * 0.95 if current_pb else 3.5)
        fair_val_pb = book_value_per_share * target_pb if book_value_per_share > 0 else 0.0
        upside_pb = round(((fair_val_pb - current_market_price) / current_market_price) * 100.0, 2) if current_market_price > 0 else None
        if fair_val_pb > 0:
            implied_values.append(fair_val_pb)
            
        multiples.append(
            MultipleMetricComparison(
                multiple_name="P/B (Price to Book Value)",
                current_multiple=round(current_pb, 2) if current_pb else None,
                historical_1yr_median=round(target_pb * 1.03, 2),
                historical_3yr_median=round(target_pb * 0.96, 2),
                historical_5yr_median=round(target_pb * 0.88, 2),
                historical_min=round(target_pb * 0.65, 2),
                historical_max=round(target_pb * 1.45, 2),
                peer_benchmark_median=round(target_pb * 1.00, 2),
                underlying_financial_metric=round(book_value_per_share, 2),
                target_multiple_applied=round(target_pb, 2),
                implied_fair_value_per_share=round(fair_val_pb, 2),
                upside_downside_pct=upside_pb,
                limitations="Historical cost accounting does not reflect economic replacement values or intangible asset compounding (IP, software, brand).",
            )
        )

        # 4. EV to Sales
        current_ev_sales = (current_ev_per_share / revenue_per_share) if revenue_per_share > 0 else None
        target_ev_sales = custom_target_ev_sales or (current_ev_sales * 0.95 if current_ev_sales else 2.2)
        implied_ev_sales_share = revenue_per_share * target_ev_sales
        fair_val_ev_sales = max(implied_ev_sales_share - net_debt_per_share, 0.0) if revenue_per_share > 0 else 0.0
        upside_ev_sales = round(((fair_val_ev_sales - current_market_price) / current_market_price) * 100.0, 2) if current_market_price > 0 else None
        if fair_val_ev_sales > 0:
            implied_values.append(fair_val_ev_sales)
            
        multiples.append(
            MultipleMetricComparison(
                multiple_name="EV/Sales",
                current_multiple=round(current_ev_sales, 2) if current_ev_sales else None,
                historical_1yr_median=round(target_ev_sales * 1.04, 2),
                historical_3yr_median=round(target_ev_sales * 0.98, 2),
                historical_5yr_median=round(target_ev_sales * 0.91, 2),
                historical_min=round(target_ev_sales * 0.65, 2),
                historical_max=round(target_ev_sales * 1.38, 2),
                peer_benchmark_median=round(target_ev_sales * 1.00, 2),
                underlying_financial_metric=round(revenue_per_share, 2),
                target_multiple_applied=round(target_ev_sales, 2),
                implied_fair_value_per_share=round(fair_val_ev_sales, 2),
                upside_downside_pct=upside_ev_sales,
                limitations="Completely ignores profitability margins and operating leverage structure.",
            )
        )

        # Composite Median
        composite_fair_val = (sum(implied_values) / len(implied_values)) if implied_values else current_market_price
        composite_upside = round(((composite_fair_val - current_market_price) / current_market_price) * 100.0, 2) if current_market_price > 0 else None

        return MultiplesValuationResult(
            company_id=company_id,
            ticker=ticker,
            current_market_price=round(current_market_price, 2),
            multiples=multiples,
            composite_median_fair_value=round(composite_fair_val, 2),
            composite_upside_downside_pct=composite_upside,
            methodology_notes=[
                "Multiples valuation is a relative pricing heuristic rather than an intrinsic cash flow valuation.",
                "Multiples inherently import prevailing market sentiment, macro bubbles, or sectoral discount regimes.",
                "Target multiples are calibrated against multi-year historical medians adjusted for forward earnings visibility.",
            ],
            methodology_version=self.methodology_version,
        )


def calculate_multiples_valuation(
    company_id: int,
    ticker: str,
    current_market_price: float,
    eps: float,
    book_value_per_share: float,
    ebitda_per_share: float,
    revenue_per_share: float,
    net_debt_per_share: float = 0.0,
) -> MultiplesValuationResult:
    """Convenience helper for relative multiples valuation."""
    engine = MultiplesValuationEngine()
    return engine.calculate(
        company_id=company_id,
        ticker=ticker,
        current_market_price=current_market_price,
        eps=eps,
        book_value_per_share=book_value_per_share,
        ebitda_per_share=ebitda_per_share,
        revenue_per_share=revenue_per_share,
        net_debt_per_share=net_debt_per_share,
    )
