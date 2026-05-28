import pytest
from pydantic import ValidationError

from fibengine.config import SizingConfig
from fibengine.models import Pivot, Swing
from fibengine.sizing.solros import build_sizing_plan


def _up_swing(df) -> Swing:
    low = Pivot(40, df.index[40], 105.0, "low", 2.0)
    high = Pivot(60, df.index[60], 130.0, "high", 2.0)
    return Swing(start=low, end=high)


def test_plan_has_one_entry_per_level(synthetic_df):
    cfg = SizingConfig(entry_levels=[0.382, 0.5, 0.618], sizes=[1.0, 2.0, 3.0])
    plan = build_sizing_plan(_up_swing(synthetic_df), cfg)
    assert len(plan) == 3
    assert [e.size for e in plan] == [1.0, 2.0, 3.0]


def test_largest_size_in_golden_zone(synthetic_df):
    cfg = SizingConfig(entry_levels=[0.382, 0.5, 0.618], sizes=[1.0, 2.0, 3.0])
    plan = build_sizing_plan(_up_swing(synthetic_df), cfg)
    biggest = max(plan, key=lambda e: e.size)
    assert biggest.ratio == 0.618


def test_entry_prices_monotonic_along_up_leg(synthetic_df):
    cfg = SizingConfig(entry_levels=[0.382, 0.5, 0.618], sizes=[1.0, 2.0, 3.0])
    plan = build_sizing_plan(_up_swing(synthetic_df), cfg)
    # Upp-leg (105 -> 130): högre retracement-ratio = lägre pris.
    prices = [e.price for e in plan]
    assert prices[0] > prices[1] > prices[2]


def test_rejects_mismatched_level_and_size_counts():
    with pytest.raises(ValidationError):
        SizingConfig(entry_levels=[0.382, 0.5], sizes=[1.0])
