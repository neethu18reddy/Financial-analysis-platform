"""Corporate Actions factor calculator for stock splits, bonuses, and share count adjustments."""

from typing import List
from app.models.corporate_actions import CorporateAction, ActionType


class CorporateActionsCalculator:
    """Calculates cumulative split and bonus adjustment factors for historical metrics."""

    @staticmethod
    def calculate_adjustment_factor(action_type: ActionType, numerator: float, denominator: float) -> float:
        """
        Calculate single action adjustment factor.
        For example:
        - Stock Split 1:5 (1 share into 5 shares) -> factor = 5.0 (Share count multiplies by 5; historical EPS divides by 5)
        - Bonus Issue 2:1 (2 bonus shares for every 1 held, total 3) -> factor = (1 + 2/1) = 3.0
        - Bonus Issue 1:2 (1 bonus share for every 2 held, total 1.5) -> factor = (1 + 1/2) = 1.5
        """
        if denominator <= 0:
            return 1.0

        if action_type == ActionType.STOCK_SPLIT or action_type == ActionType.FACE_VALUE_CHANGE:
            # If numerator:denominator is new:old (e.g., old FV 10 -> new FV 2 is 5:1 split)
            return round(numerator / denominator, 4)
        
        elif action_type == ActionType.BONUS_ISSUE:
            # Bonus issue N:D means holder gets N bonus shares for every D shares held.
            # Total shares after = D + N for every D. Multiplier = (D + N) / D = 1 + N/D.
            return round(1.0 + (numerator / denominator), 4)

        return 1.0

    @staticmethod
    def compute_cumulative_adjustment_factors(actions: List[CorporateAction]) -> List[CorporateAction]:
        """
        Sort corporate actions chronologically and compute their cumulative impact.
        Returns actions with updated adjustment_factor values.
        """
        if not actions:
            return []

        sorted_actions = sorted(actions, key=lambda a: a.ex_date)
        for action in sorted_actions:
            if action.ratio_numerator and action.ratio_denominator:
                action.adjustment_factor = CorporateActionsCalculator.calculate_adjustment_factor(
                    action.action_type,
                    action.ratio_numerator,
                    action.ratio_denominator
                )
        return sorted_actions
