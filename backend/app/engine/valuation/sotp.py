"""Sum-of-the-Parts (SOTP) Valuation Engine.

Foundational valuation engine for multi-business conglomerates (e.g. Reliance Industries, L&T, Tata Sons):
- Evaluates individual business segments by appropriate sector EV/EBITDA multiples
- Applies holding company discount (e.g. 15-20%)
- Subtracts net debt to bridge to equity value per share
"""

from typing import Dict, Any, List, Optional
try:
    from app.models.valuation import (
        SOTPSegment,
        SOTPValuationResult,
    )
    from app.engine.valuation.base import BaseValuationEngine, VALUATION_METHODOLOGY_VERSION
except ImportError:
    from backend.app.models.valuation import (
        SOTPSegment,
        SOTPValuationResult,
    )
    from backend.app.engine.valuation.base import BaseValuationEngine, VALUATION_METHODOLOGY_VERSION


class SOTPValuationEngine(BaseValuationEngine):
    """Executes Sum-of-the-Parts valuation."""

    def calculate(
        self,
        company_id: int,
        ticker: str,
        segments: List[SOTPSegment],
        net_debt_crores: float,
        shares_outstanding_crores: float,
        holding_company_discount_pct: float = 15.0,
        current_market_price: Optional[float] = None,
    ) -> SOTPValuationResult:
        """Calculates aggregate SOTP Enterprise and Equity Value."""
        
        calculated_segments: List[SOTPSegment] = []
        gross_ev = 0.0
        
        for seg in segments:
            implied_ev = seg.ebitda * seg.benchmark_ev_ebitda_multiple
            effective_ev = implied_ev * (seg.ownership_stake_pct / 100.0)
            gross_ev += effective_ev
            
            calculated_segments.append(
                SOTPSegment(
                    segment_name=seg.segment_name,
                    segment_description=seg.segment_description,
                    revenue=round(seg.revenue, 2),
                    ebitda=round(seg.ebitda, 2),
                    benchmark_ev_ebitda_multiple=round(seg.benchmark_ev_ebitda_multiple, 2),
                    implied_enterprise_value=round(implied_ev, 2),
                    ownership_stake_pct=seg.ownership_stake_pct,
                    effective_enterprise_value=round(effective_ev, 2),
                )
            )
            
        discount_factor = 1.0 - (holding_company_discount_pct / 100.0)
        net_ev = gross_ev * discount_factor
        equity_val = net_ev - net_debt_crores
        
        fair_val_share = (equity_val / shares_outstanding_crores) if shares_outstanding_crores > 0 else 0.0
        fair_val_share = max(round(fair_val_share, 2), 0.0)
        
        upside = None
        if current_market_price and current_market_price > 0:
            upside = round(((fair_val_share - current_market_price) / current_market_price) * 100.0, 2)

        return SOTPValuationResult(
            company_id=company_id,
            ticker=ticker,
            segments=calculated_segments,
            gross_enterprise_value=round(gross_ev, 2),
            holding_company_discount_pct=holding_company_discount_pct,
            net_enterprise_value=round(net_ev, 2),
            net_debt=round(net_debt_crores, 2),
            equity_value=round(equity_val, 2),
            shares_outstanding_crores=round(shares_outstanding_crores, 3),
            fair_value_per_share=fair_val_share,
            current_market_price=current_market_price,
            upside_downside_pct=upside,
            methodology_version=self.methodology_version,
        )
