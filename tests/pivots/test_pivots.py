import numpy as np
import pandas as pd

from fibengine.core.config import PivotConfig
from fibengine.pivots.detect import detect_pivots


def test_detects_alternating_pivots(synthetic_df):
    cfg = PivotConfig(lookback=5, atr_period=14, min_prominence_atr=0.3)
    pivots = detect_pivots(synthetic_df, cfg)

    assert len(pivots) >= 2
    # Pivots ska vara sorterade i tid och alternera high/low.
    kinds = [p.kind for p in pivots]
    for a, b in zip(kinds, kinds[1:], strict=False):
        assert a != b
    assert [p.index for p in pivots] == sorted(p.index for p in pivots)


def test_finds_major_high_and_low(synthetic_df):
    cfg = PivotConfig(lookback=5, atr_period=14, min_prominence_atr=0.3)
    pivots = detect_pivots(synthetic_df, cfg)

    highs = [p for p in pivots if p.kind == "high"]
    lows = [p for p in pivots if p.kind == "low"]
    assert highs and lows
    # Toppen runt bar 60 (pris ~130) ska finnas med.
    assert max(p.price for p in highs) > 128


def test_fractal_mode_still_finds_major_swings(synthetic_df):
    cfg = PivotConfig(
        lookback=5, atr_period=14, min_prominence_atr=0.3, mode="fractal", fractal_n=2
    )
    pivots = detect_pivots(synthetic_df, cfg)

    # Strikt Williams-läge ska fortfarande hitta de stora vändpunkterna och alternera.
    assert len(pivots) >= 2
    kinds = [p.kind for p in pivots]
    for a, b in zip(kinds, kinds[1:], strict=False):
        assert a != b


def test_window_mode_does_not_emit_two_pivots_for_same_bar():
    idx = pd.date_range("2024-01-01", periods=20, freq="1h", tz="UTC")
    close = np.full(20, 100.0)
    high = np.full(20, 101.0)
    low = np.full(20, 99.0)
    high[10] = 120.0
    low[10] = 80.0
    df = pd.DataFrame(
        {"open": close, "high": high, "low": low, "close": close, "volume": np.ones(20)},
        index=idx,
    )
    pivots = detect_pivots(
        df, PivotConfig(lookback=2, atr_period=2, min_prominence_atr=0.1, mode="window")
    )
    assert len([p for p in pivots if p.index == 10]) <= 1
