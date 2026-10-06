"""2D Valuation Sensitivity Engine.

Builds multi-dimensional sensitivity matrices:
1. WACC (%) vs Terminal Growth Rate (%)
2. Revenue Growth (%) vs Target Operating Margin (%)
3. Exit Multiple vs Discount Rate (WACC)

Allows investors to evaluate valuation fragility across assumption ranges.
"""

from typing import Dict, Any, List, Optional
try:
    from app.models.valuation import (
        SensitivityCell,
        SensitivityMatrixResult,
        DCFValuationInputs,
        TerminalValueMethod,
    )
    from app.engine.valuation.base import BaseValuationEngine, VALUATION_METHODOLOGY_VERSION
    from app.engine.valuation.dcf import DCFValuationEngine
except ImportError:
    from backend.app.models.valuation import (
        SensitivityCell,
        SensitivityMatrixResult,
        DCFValuationInputs,
        TerminalValueMethod,
    )
    from backend.app.engine.valuation.base import BaseValuationEngine, VALUATION_METHODOLOGY_VERSION
    from backend.app.engine.valuation.dcf import DCFValuationEngine


class SensitivityValuationEngine(BaseValuationEngine):
    """Generates 2D sensitivity grids across key valuation levers."""

    def calculate(
        self,
        company_id: int,
        ticker: str,
        current_market_price: float,
        base_revenue: float,
        shares_outstanding_crores: float,
        total_debt_crores: float = 0.0,
        cash_and_investments_crores: float = 0.0,
        base_wacc_pct: float = 11.5,
        base_terminal_growth_pct: float = 5.0,
        base_growth_pct: float = 12.0,
        base_margin_pct: float = 18.0,
    ) -> SensitivityMatrixResult:
        """Executes default WACC vs Terminal Growth 2D sensitivity matrix."""
        return self.build_wacc_vs_terminal_growth_matrix(
            company_id=company_id,
            ticker=ticker,
            current_market_price=current_market_price,
            base_revenue=base_revenue,
            shares_outstanding_crores=shares_outstanding_crores,
            total_debt_crores=total_debt_crores,
            cash_and_investments_crores=cash_and_investments_crores,
            base_wacc_pct=base_wacc_pct,
            base_terminal_growth_pct=base_terminal_growth_pct,
            base_growth_pct=base_growth_pct,
            base_margin_pct=base_margin_pct,
        )

    def build_wacc_vs_terminal_growth_matrix(
        self,
        company_id: int,
        ticker: str,
        current_market_price: float,
        base_revenue: float,
        shares_outstanding_crores: float,
        total_debt_crores: float = 0.0,
        cash_and_investments_crores: float = 0.0,
        base_wacc_pct: float = 11.5,
        base_terminal_growth_pct: float = 5.0,
        base_growth_pct: float = 12.0,
        base_margin_pct: float = 18.0,
    ) -> SensitivityMatrixResult:
        """Matrix 1: Rows = WACC (e.g. 10.0% to 13.0%), Cols = Terminal Growth (3.5% to 6.0%)."""
        
        dcf_engine = DCFValuationEngine()
        
        # 5x5 Grid
        row_waccs = [
            round(base_wacc_pct - 1.5, 2),
            round(base_wacc_pct - 0.75, 2),
            round(base_wacc_pct, 2),
            round(base_wacc_pct + 0.75, 2),
            round(base_wacc_pct + 1.5, 2),
        ]
        
        col_tgs = [
            round(base_terminal_growth_pct - 1.5, 2),
            round(base_terminal_growth_pct - 0.75, 2),
            round(base_terminal_growth_pct, 2),
            round(base_terminal_growth_pct + 0.75, 2),
            round(base_terminal_growth_pct + 1.5, 2),
        ]
        
        grid: List[List[SensitivityCell]] = []
        base_fair_val = 0.0
        
        for w in row_waccs:
            row_cells: List[SensitivityCell] = []
            for g in col_tgs:
                # Ensure discount rate strictly exceeds terminal growth
                eff_w = max(w, g + 0.5)
                dcf_in = DCFValuationInputs(
                    forecast_years=5,
                    base_revenue=base_revenue,
                    constant_revenue_growth_pct=base_growth_pct,
                    target_ebit_margin_pct=base_margin_pct,
                    wacc_pct=eff_w,
                    terminal_growth_rate_pct=g,
                    shares_outstanding_crores=shares_outstanding_crores,
                    total_debt_crores=total_debt_crores,
                    cash_and_investments_crores=cash_and_investments_crores,
                )
                res = dcf_engine.calculate(
                    company_id=company_id,
                    ticker=ticker,
                    inputs=dcf_in,
                    current_market_price=current_market_price,
                )
                fv = res.estimated_fair_value_per_share
                upside = res.upside_downside_pct
                
                if w == base_wacc_pct and g == base_terminal_growth_pct:
                    base_fair_val = fv
                    
                row_cells.append(
                    SensitivityCell(
                        row_value=w,
                        col_value=g,
                        fair_value_per_share=fv,
                        upside_downside_pct=upside,
                    )
                )
            grid.append(row_cells)

        return SensitivityMatrixResult(
            matrix_name="WACC vs Terminal Growth Rate Sensitivity Matrix",
            row_parameter_name="Discount Rate (WACC)",
            row_parameter_unit="%",
            col_parameter_name="Terminal Growth Rate (g)",
            col_parameter_unit="%",
            row_values=row_waccs,
            col_values=col_tgs,
            grid=grid,
            base_row_value=base_wacc_pct,
            base_col_value=base_terminal_growth_pct,
            base_fair_value=base_fair_val or (grid[2][2].fair_value_per_share),
        )

    def build_growth_vs_margin_matrix(
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
    ) -> SensitivityMatrixResult:
        """Matrix 2: Rows = Revenue Growth (%), Cols = EBIT Operating Margin (%)."""
        
        dcf_engine = DCFValuationEngine()
        
        row_growths = [
            round(base_growth_pct - 4.0, 1),
            round(base_growth_pct - 2.0, 1),
            round(base_growth_pct, 1),
            round(base_growth_pct + 2.0, 1),
            round(base_growth_pct + 4.0, 1),
        ]
        
        col_margins = [
            round(base_margin_pct - 3.0, 1),
            round(base_margin_pct - 1.5, 1),
            round(base_margin_pct, 1),
            round(base_margin_pct + 1.5, 1),
            round(base_margin_pct + 3.0, 1),
        ]
        
        grid: List[List[SensitivityCell]] = []
        base_fair_val = 0.0
        
        for g in row_growths:
            row_cells: List[SensitivityCell] = []
            for m in col_margins:
                dcf_in = DCFValuationInputs(
                    forecast_years=5,
                    base_revenue=base_revenue,
                    constant_revenue_growth_pct=max(g, 1.0),
                    target_ebit_margin_pct=max(m, 2.0),
                    wacc_pct=base_wacc_pct,
                    terminal_growth_rate_pct=base_terminal_growth_pct,
                    shares_outstanding_crores=shares_outstanding_crores,
                    total_debt_crores=total_debt_crores,
                    cash_and_investments_crores=cash_and_investments_crores,
                )
                res = dcf_engine.calculate(
                    company_id=company_id,
                    ticker=ticker,
                    inputs=dcf_in,
                    current_market_price=current_market_price,
                )
                fv = res.estimated_fair_value_per_share
                upside = res.upside_downside_pct
                
                if g == base_growth_pct and m == base_margin_pct:
                    base_fair_val = fv
                    
                row_cells.append(
                    SensitivityCell(
                        row_value=g,
                        col_value=m,
                        fair_value_per_share=fv,
                        upside_downside_pct=upside,
                    )
                )
            grid.append(row_cells)

        return SensitivityMatrixResult(
            matrix_name="Revenue Growth vs EBIT Margin Sensitivity Matrix",
            row_parameter_name="Revenue Growth CAGR",
            row_parameter_unit="%",
            col_parameter_name="EBIT Operating Margin",
            col_parameter_unit="%",
            row_values=row_growths,
            col_values=col_margins,
            grid=grid,
            base_row_value=base_growth_pct,
            base_col_value=base_margin_pct,
            base_fair_value=base_fair_val or (grid[2][2].fair_value_per_share),
        )
