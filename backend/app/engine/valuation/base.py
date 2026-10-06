"""Valuation Engine Base Class and Abstraction Layer.

Provides modular interfaces for deterministic financial valuation models:
- DCF (FCFF / FCFE)
- Reverse DCF
- Relative Multiples
- Financial Institutions (DDM / Residual Income)
- Sum-of-the-Parts (SOTP)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

VALUATION_METHODOLOGY_VERSION = "v1.0.0-phase4"


class BaseValuationEngine(ABC):
    """Abstract base class for all deterministic valuation models."""

    def __init__(self, methodology_version: str = VALUATION_METHODOLOGY_VERSION):
        self.methodology_version = methodology_version

    @abstractmethod
    def calculate(self, *args, **kwargs) -> BaseModel:
        """Executes pure deterministic valuation calculations without LLM dependency."""
        pass

    @staticmethod
    def calculate_capm_cost_of_equity(
        risk_free_rate_pct: float,
        beta: float,
        equity_risk_premium_pct: float,
    ) -> float:
        """Capital Asset Pricing Model (CAPM): Ke = Rf + Beta * ERP."""
        return risk_free_rate_pct + (beta * equity_risk_premium_pct)

    @staticmethod
    def calculate_wacc(
        cost_of_equity_pct: float,
        pre_tax_cost_of_debt_pct: float,
        effective_tax_rate_pct: float,
        debt_to_capital_pct: float,
    ) -> float:
        """Weighted Average Cost of Capital (WACC): WACC = (We * Ke) + (Wd * Kd * (1 - t))."""
        equity_weight = (100.0 - debt_to_capital_pct) / 100.0
        debt_weight = debt_to_capital_pct / 100.0
        after_tax_kd = pre_tax_cost_of_debt_pct * (1.0 - (effective_tax_rate_pct / 100.0))
        return (equity_weight * cost_of_equity_pct) + (debt_weight * after_tax_kd)

    @staticmethod
    def calculate_gordon_terminal_value(
        final_fcf: float,
        discount_rate_pct: float,
        terminal_growth_rate_pct: float,
    ) -> float:
        """Gordon Growth Model: TV = (FCF_n * (1 + g)) / (r - g)."""
        r = discount_rate_pct / 100.0
        g = terminal_growth_rate_pct / 100.0
        if r <= g:
            # Guardrail against singularity or negative denominator
            raise ValueError(f"Discount rate ({discount_rate_pct:.2f}%) must strictly exceed terminal growth rate ({terminal_growth_rate_pct:.2f}%).")
        fcf_next = final_fcf * (1.0 + g)
        return fcf_next / (r - g)

    @staticmethod
    def discount_cash_flows(cash_flows: list[float], discount_rate_pct: float) -> list[float]:
        """Discounts a series of future cash flows at the specified rate."""
        r = discount_rate_pct / 100.0
        discounted = []
        for i, cf in enumerate(cash_flows, start=1):
            df = 1.0 / ((1.0 + r) ** i)
            discounted.append(cf * df)
        return discounted
