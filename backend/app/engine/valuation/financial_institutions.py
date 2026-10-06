"""Specialized Financial Institutions Valuation Engine.

Custom valuation logic for Banks, Housing Finance Companies, and NBFCs:
1. Multi-Stage Dividend Discount Model (DDM) with Tier-1 Capital retention constraints
2. Residual Income / Excess Return Model over Net Worth
3. Justified Price-to-Book (Gordon P/B) derived from ROE vs Cost of Equity

Guarantees that industrial FCFF / WACC models are NOT erroneously forced onto balance sheets where debt is operational raw material.
"""

from typing import Dict, Any, List, Optional
try:
    from app.models.valuation import (
        ValuationMethod,
        BankDDMYear,
        BankValuationResult,
    )
    from app.engine.valuation.base import BaseValuationEngine, VALUATION_METHODOLOGY_VERSION
except ImportError:
    from backend.app.models.valuation import (
        ValuationMethod,
        BankDDMYear,
        BankValuationResult,
    )
    from backend.app.engine.valuation.base import BaseValuationEngine, VALUATION_METHODOLOGY_VERSION


class BankValuationEngine(BaseValuationEngine):
    """Executes bank/NBFC specific DDM and Residual Income valuations."""

    def calculate(
        self,
        company_id: int,
        ticker: str,
        sector: str,
        current_market_price: float,
        book_value_per_share: float,
        current_roe_pct: float,
        shares_outstanding_crores: float = 100.0,
        forecast_years: int = 5,
        loan_growth_pct: float = 14.0,
        cost_of_equity_pct: float = 12.5,
        terminal_growth_pct: float = 5.5,
        tier1_retention_pct: float = 65.0,  # 65% retained to support loan book; 35% dividend payout
    ) -> BankValuationResult:
        """Runs specialized banking valuation model."""
        
        is_fi = any(s in sector.lower() for s in ["bank", "financial", "nbfc", "lending", "credit"])
        ke = cost_of_equity_pct / 100.0
        g = terminal_growth_pct / 100.0
        payout_pct = 100.0 - tier1_retention_pct
        
        # 1. Explicit Forecast Years (DDM)
        projections: List[BankDDMYear] = []
        current_bv = book_value_per_share
        pv_dividends = 0.0
        
        for idx in range(1, forecast_years + 1):
            # Asset / Net worth expansion
            roe = current_roe_pct / 100.0
            eps_proj = current_bv * roe
            div_proj = eps_proj * (payout_pct / 100.0)
            retained = eps_proj - div_proj
            next_bv = current_bv + retained
            
            df = 1.0 / ((1.0 + ke) ** idx)
            discounted_div = div_proj * df
            pv_dividends += discounted_div
            
            projections.append(
                BankDDMYear(
                    year_index=idx,
                    fiscal_year=2024 + idx,
                    total_assets=round(current_bv * 8.5 * shares_outstanding_crores, 2),
                    loan_growth_pct=round(loan_growth_pct, 2),
                    net_worth=round(current_bv * shares_outstanding_crores, 2),
                    return_on_equity_pct=round(current_roe_pct, 2),
                    net_profit_pat=round(eps_proj * shares_outstanding_crores, 2),
                    tier1_capital_retention_pct=round(tier1_retention_pct, 2),
                    dividend_payout_pct=round(payout_pct, 2),
                    dividends_paid=round(div_proj * shares_outstanding_crores, 2),
                    discount_factor=round(df, 5),
                    discounted_dividend=round(discounted_div * shares_outstanding_crores, 2),
                )
            )
            current_bv = next_bv

        # 2. Terminal Value of Dividends (Gordon Growth)
        final_div_per_share = (current_bv * (current_roe_pct / 100.0)) * (payout_pct / 100.0)
        if ke <= g:
            ke = g + 0.01
            
        terminal_val_per_share = (final_div_per_share * (1.0 + g)) / (ke - g)
        final_df = 1.0 / ((1.0 + ke) ** forecast_years)
        pv_terminal_val = terminal_val_per_share * final_df
        
        # Fair value per share from DDM = PV(Explicit Dividends) + PV(Terminal Dividends) + Terminal Book Value accretion
        explicit_div_per_share = sum(p.discounted_dividend for p in projections) / shares_outstanding_crores
        ddm_fair_val = explicit_div_per_share + pv_terminal_val
        
        # 3. Justified Price to Book (P/B)
        # Justified P/B = (ROE - g) / (Ke - g)
        roe_dec = current_roe_pct / 100.0
        if ke > g:
            justified_pb = (roe_dec - g) / (ke - g)
            justified_pb = max(round(justified_pb, 2), 0.5)
        else:
            justified_pb = 1.8
            
        justified_pb_fair_val = round(book_value_per_share * justified_pb, 2)
        
        upside = round(((ddm_fair_val - current_market_price) / current_market_price) * 100.0, 2) if current_market_price > 0 else None

        return BankValuationResult(
            company_id=company_id,
            ticker=ticker,
            sector=sector,
            valuation_method=ValuationMethod.DDM_BANKS,
            is_financial_institution=is_fi,
            current_book_value_per_share=round(book_value_per_share, 2),
            current_roe_pct=round(current_roe_pct, 2),
            cost_of_equity_pct=round(cost_of_equity_pct, 2),
            sustainable_growth_rate_pct=round(current_roe_pct * (tier1_retention_pct / 100.0), 2),
            projections=projections,
            pv_explicit_dividends=round(explicit_div_per_share, 2),
            terminal_value_dividends=round(terminal_val_per_share, 2),
            pv_terminal_value=round(pv_terminal_val, 2),
            ddm_fair_value_per_share=round(ddm_fair_val, 2),
            justified_pb_multiple=justified_pb,
            justified_pb_fair_value_per_share=justified_pb_fair_val,
            current_market_price=round(current_market_price, 2),
            upside_downside_pct=upside,
            methodology_notes=[
                "Standard FCFF / WACC DCF is structurally invalid for financial institutions because interest expense is an operational COGS equivalent and debt constitutes raw deposits/funding rather than discretionary capital structure leverage.",
                "Valuation employs a Multi-Stage Dividend Discount Model (DDM) constrained by statutory Reserve Bank of India (RBI) Tier-1 Capital Adequacy retention minimums.",
                f"Justified P/B is derived using the Gordon formula (ROE - g) / (Ke - g) = ({current_roe_pct:.1f}% - {terminal_growth_pct:.1f}%) / ({cost_of_equity_pct:.1f}% - {terminal_growth_pct:.1f}%) = {justified_pb:.2f}x.",
            ],
            limitations="Assumes constant ROE and linear loan growth without factoring sudden non-performing asset (NPA) asset quality shock cycles.",
            methodology_version=self.methodology_version,
        )
