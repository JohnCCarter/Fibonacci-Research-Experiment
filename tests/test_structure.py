import pandas as pd

from fibengine.config import PivotConfig
from fibengine.pivots.detect import detect_pivots
from fibengine.structure import (
    downtrend_alignment,
    structure_alignment,
    uptrend_alignment,
)


def _uptrend_df() -> pd.DataFrame:
    # Stigande struktur: HH + HL (varje topp och botten högre än föregående).
    pts = [(0, 100), (20, 112), (40, 108), (60, 124), (80, 118), (100, 136)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    import numpy as np

    grid = np.arange(0, xs[-1] + 1)
    closes = np.interp(grid, xs, ys)
    n = len(closes)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {"open": closes, "high": closes + 0.5, "low": closes - 0.5,
         "close": closes, "volume": np.ones(n)},
        index=idx,
    )


def test_uptrend_alignment_high_for_clean_uptrend():
    df = _uptrend_df()
    pivots = detect_pivots(df, PivotConfig(lookback=4, min_prominence_atr=0.3))
    end_index = pivots[-1].index
    up = uptrend_alignment(pivots, end_index, window=6)
    down = downtrend_alignment(pivots, end_index, window=6)
    assert up > 0.8
    assert down < 0.2


def test_structure_alignment_rewards_up_leg_in_uptrend():
    df = _uptrend_df()
    pivots = detect_pivots(df, PivotConfig(lookback=4, min_prominence_atr=0.3))
    end_index = pivots[-1].index
    aligned = structure_alignment(pivots, end_index, window=6, direction="up")
    against = structure_alignment(pivots, end_index, window=6, direction="down")
    assert aligned > against
