from datetime import UTC, datetime

import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from fibengine.core.fib import fib_from_prices, fib_levels
from fibengine.core.models import Pivot, Swing
from fibengine.validation.schemas import validate_ohlcv_df


def _up_swing(start_price: float, end_price: float) -> Swing:
    return Swing(
        start=Pivot(0, datetime(2024, 1, 1, tzinfo=UTC), start_price, "low", 1.0),
        end=Pivot(40, datetime(2024, 2, 10, tzinfo=UTC), end_price, "high", 1.0),
        status="confirmed",
    )


@given(
    start=st.floats(min_value=1.0, max_value=1000.0, allow_nan=False),
    end=st.floats(min_value=1.0, max_value=1000.0, allow_nan=False),
    ratios=st.lists(
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        min_size=1,
        max_size=8,
        unique=True,
    ),
)
@settings(max_examples=50)
def test_fib_levels_up_leg_prices_within_anchor_range(start, end, ratios):
    if end <= start:
        return
    swing = _up_swing(start, end)
    prices = fib_levels(swing, ratios)
    lo, hi = min(start, end), max(start, end)
    for price in prices.values():
        assert lo - 1e-9 <= price <= hi + 1e-9


@given(
    n=st.integers(min_value=2, max_value=30),
    base=st.floats(min_value=10.0, max_value=500.0, allow_nan=False),
    spread=st.floats(min_value=0.01, max_value=5.0, allow_nan=False),
)
@settings(max_examples=40)
def test_synthetic_ohlcv_high_ge_low(n, base, spread):
    close = pd.Series([base + i * 0.1 for i in range(n)])
    df = pd.DataFrame(
        {
            "open": close,
            "high": close + spread,
            "low": close - spread,
            "close": close,
            "volume": 1.0,
        }
    )
    validate_ohlcv_df(df)


@given(
    start=st.floats(min_value=1.0, max_value=500.0, allow_nan=False),
    end=st.floats(min_value=1.0, max_value=500.0, allow_nan=False),
)
@settings(max_examples=50)
def test_fib_from_prices_endpoints(start, end):
    if start == end:
        return
    levels = [0.0, 0.382, 0.5, 0.618, 1.0]
    prices = fib_from_prices(start, end, levels)
    assert prices[0.0] == pytest.approx(end)
    assert prices[1.0] == pytest.approx(start)
