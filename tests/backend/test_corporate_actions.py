"""Unit tests for Corporate Actions calculations."""

import pytest
from app.models.corporate_actions import ActionType, CorporateAction
from app.engine.corporate_actions_calculator import CorporateActionsCalculator
from datetime import date


def test_stock_split_factor_calculation():
    """Test 1:5 stock split factor (1 share becomes 5 shares)."""
    factor = CorporateActionsCalculator.calculate_adjustment_factor(
        action_type=ActionType.STOCK_SPLIT,
        numerator=5.0,
        denominator=1.0
    )
    assert factor == 5.0


def test_bonus_issue_factor_calculation():
    """Test 2:1 bonus issue (2 bonus shares for every 1 share held -> total 3 shares)."""
    factor = CorporateActionsCalculator.calculate_adjustment_factor(
        action_type=ActionType.BONUS_ISSUE,
        numerator=2.0,
        denominator=1.0
    )
    assert factor == 3.0

    # 1:2 bonus (1 bonus for every 2 held -> total 1.5)
    factor_half = CorporateActionsCalculator.calculate_adjustment_factor(
        action_type=ActionType.BONUS_ISSUE,
        numerator=1.0,
        denominator=2.0
    )
    assert factor_half == 1.5


def test_cumulative_actions_ordering():
    """Test sorting and cumulative factor calculation."""
    actions = [
        CorporateAction(
            id=1,
            company_id=1,
            action_type=ActionType.BONUS_ISSUE,
            ex_date=date(2023, 6, 1),
            ratio_numerator=1.0,
            ratio_denominator=1.0
        ),
        CorporateAction(
            id=2,
            company_id=1,
            action_type=ActionType.STOCK_SPLIT,
            ex_date=date(2021, 5, 1),
            ratio_numerator=2.0,
            ratio_denominator=1.0
        ),
    ]
    computed = CorporateActionsCalculator.compute_cumulative_adjustment_factors(actions)
    assert len(computed) == 2
    assert computed[0].ex_date == date(2021, 5, 1)
    assert computed[0].adjustment_factor == 2.0
    assert computed[1].ex_date == date(2023, 6, 1)
    assert computed[1].adjustment_factor == 2.0  # 1 + 1/1 = 2.0
