"""Delade fixtures: syntetiska candles med tydliga swingar (ingen nätverk)."""

import numpy as np
import pandas as pd
import pytest


def _piecewise(points: list[tuple[int, float]]) -> np.ndarray:
    """Linjär interpolation mellan (bar, pris)-punkter."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    grid = np.arange(xs[0], xs[-1] + 1)
    return np.interp(grid, xs, ys)


@pytest.fixture
def synthetic_df() -> pd.DataFrame:
    # low@0=100 -> high@20=120 -> low@40=105 -> high@60=130
    closes = _piecewise([(0, 100), (20, 120), (40, 105), (60, 130)])
    n = len(closes)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": closes,
            "high": closes + 0.5,
            "low": closes - 0.5,
            "close": closes,
            "volume": np.ones(n),
        },
        index=idx,
    )
