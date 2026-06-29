"""Detektor-test för wick-par-väljaren (#38): rejection-wick-filter + BOS-paring."""

from __future__ import annotations

import pandas as pd

from fibengine.core.config import PivotConfig
from fibengine.strategies.chamoun_daily_wick_pair import (
    _wick_fracs,
    detect_wick_pivots,
    select_wick_pair,
)


def _bar(o, h, low, c):
    return {"open": o, "high": h, "low": low, "close": c}


def _frame() -> pd.DataFrame:
    """32 doji-platta barer + en rejection-HIGH (idx 18) och rejection-LOW (idx 26)."""
    bars = []
    for _ in range(32):
        bars.append(_bar(99.96, 100.05, 99.95, 100.04))  # wick-frac ~0.1, filtreras bort
    # Rejection high: lång övre stake, unik window-max.
    bars[18] = _bar(100.0, 130.0, 99.0, 102.0)  # övre wick = 28/31 ≈ 0.90
    # Rejection low: lång undre stake, unik window-min → bryter alla tidigare lows (BOS down).
    bars[26] = _bar(80.0, 83.0, 60.0, 82.0)  # undre wick = 20/23 ≈ 0.87
    idx = pd.date_range("2020-01-01", periods=32, freq="D", tz="UTC")
    return pd.DataFrame(bars, index=idx)


def test_wick_fracs_basic():
    upper, lower = _wick_fracs(100.0, 130.0, 99.0, 102.0)
    assert upper > 0.85 and lower < 0.1


def test_doji_candle_is_filtered_out():
    df = _frame()
    cfg = PivotConfig(lookback=5, atr_period=14)
    cands = detect_wick_pivots(df, cfg)
    # Endast de två rejection-wickarna överlever filtret.
    assert {p.index for p in cands} == {18, 26}
    kinds = {p.index: p.kind for p in cands}
    assert kinds[18] == "high" and kinds[26] == "low"


def test_select_wick_pair_down_impulse():
    df = _frame()
    cfg = PivotConfig(lookback=5, atr_period=14)
    sel = select_wick_pair(df, cfg)
    assert sel.swing is not None
    assert sel.swing.start.index == 18  # A = rejection high
    assert sel.swing.end.index == 26  # B = BOS rejection low
    assert sel.swing.direction == "down"
    assert any(a["event"] == "start_chosen" for a in sel.audit)


def test_no_pair_when_no_bos():
    # Bara doji-barer → inga kandidater → ingen swing (miss, inte krasch).
    idx = pd.date_range("2020-01-01", periods=20, freq="D", tz="UTC")
    df = pd.DataFrame([_bar(99.96, 100.05, 99.95, 100.04) for _ in range(20)], index=idx)
    sel = select_wick_pair(df, PivotConfig(lookback=5, atr_period=14))
    assert sel.swing is None
