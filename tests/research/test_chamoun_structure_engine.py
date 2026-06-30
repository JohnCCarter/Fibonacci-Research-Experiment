"""Tests for chamoun_structure_engine — descriptive down-structure proposer, frozen v1 params."""

from __future__ import annotations

import pandas as pd
import pytest

from fibengine.core.models import Pivot
from fibengine.research.chamoun_structure_engine import (
    DEFAULT_CONFIG,
    StructureConfig,
    propose_structures,
)


def _make_df(high: list[float], low: list[float], close: list[float]) -> pd.DataFrame:
    n = len(high)
    idx = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
    return pd.DataFrame({"open": close, "high": high, "low": low, "close": close}, index=idx)


def _high_pivot(df: pd.DataFrame, i: int, prom: float) -> Pivot:
    return Pivot(i, df.index[i], float(df["high"].iloc[i]), "high", prom)


def test_single_dominant_down_structure():
    high = [96, 98, 100, 98, 95, 93, 92, 94, 99, 101, 100]
    low = [95, 96, 98, 94, 92, 91, 90, 92, 95, 99, 98]
    close = [96, 97, 99, 95, 93, 92, 91, 93, 98, 101, 99]
    df = _make_df(high, low, close)
    structs = propose_structures(df, [_high_pivot(df, 2, 5.0)])
    assert len(structs) == 1
    s = structs[0]
    assert s.origin_index == 2
    assert s.origin_price == 100
    assert s.reached_index == 6
    assert s.reached_price == 90  # lowest low before the close-above-origin break at bar 9
    assert s.move == pytest.approx(0.10)
    assert s.bars == 4
    assert s.active is False


def test_small_move_below_min_is_dropped():
    high = [96, 98, 100, 99, 99, 99, 99, 101]
    low = [95, 96, 98, 99.0, 98.8, 98.5, 98.6, 100]
    close = [96, 97, 99, 98.7, 98.6, 98.6, 98.7, 101]
    df = _make_df(high, low, close)
    # min low 98.5 at bar 5 (bars=3 passes min_bars) -> move 1.5% < 2% -> dropped
    assert propose_structures(df, [_high_pivot(df, 2, 5.0)]) == []


def test_less_prominent_high_in_scale_is_not_an_origin():
    high = [96, 98, 100, 99, 102, 110, 105, 100, 95, 112]
    low = [95, 96, 98, 97, 99, 108, 100, 96, 90, 110]
    close = [96, 97, 99, 98, 101, 109, 101, 97, 92, 112]
    df = _make_df(high, low, close)
    structs = propose_structures(df, [_high_pivot(df, 2, 4.0), _high_pivot(df, 5, 8.0)])
    origins = {s.origin_index for s in structs}
    assert 2 not in origins  # dominated by the more-prominent high at bar 5 within the local scale
    assert 5 in origins


def test_reached_is_min_low_before_break_not_after():
    high = [96, 98, 100, 96, 94, 93, 92, 95, 101, 99]
    low = [95, 96, 98, 93, 92, 91, 90, 92, 99, 80]
    close = [96, 97, 99, 94, 93, 92, 91, 93, 101, 82]
    df = _make_df(high, low, close)
    s = propose_structures(df, [_high_pivot(df, 2, 5.0)])[0]
    assert s.reached_index == 6
    assert s.reached_price == 90  # the 80 low at bar 9 is AFTER the break and must be ignored


def test_early_spike_low_within_min_bars_is_dropped():
    high = [96, 98, 100, 95, 96, 96, 96, 96, 101]
    low = [95, 96, 98, 90, 94, 94, 94, 94, 99]
    close = [96, 97, 99, 95, 95, 95, 95, 95, 101]
    df = _make_df(high, low, close)
    # lowest low 90 is reached at bar 3 (1 bar after origin) -> degenerate early spike -> dropped
    assert propose_structures(df, [_high_pivot(df, 2, 5.0)]) == []


def test_no_down_structure_when_only_low_pivots():
    high = [90, 92, 94, 96, 98]
    low = [89, 91, 93, 95, 97]
    close = [90, 92, 94, 96, 98]
    df = _make_df(high, low, close)
    assert propose_structures(df, [Pivot(2, df.index[2], float(low[2]), "low", 5.0)]) == []


def test_active_when_never_broken():
    high = [96, 98, 100, 95, 93, 92, 91, 90]
    low = [95, 96, 98, 93, 91, 90, 89, 88]
    close = [96, 97, 99, 94, 92, 91, 90, 89]  # never closes above the origin high
    df = _make_df(high, low, close)
    s = propose_structures(df, [_high_pivot(df, 2, 5.0)])[0]
    assert s.active is True
    d = s.to_dict()
    assert d["direction"] == "down"
    assert d["origin"]["price"] == 100
    assert d["active"] is True
    assert d["move"] == pytest.approx(round(s.move, 4))


def test_custom_config_min_move_threshold():
    high = [96, 98, 100, 99, 99, 98.4, 99, 101]
    low = [95, 96, 98, 98, 97.5, 97, 97.5, 100]
    close = [96, 97, 99, 98.5, 98, 97.5, 98, 101]
    df = _make_df(high, low, close)
    pivots = [_high_pivot(df, 2, 5.0)]
    # lowest low 97 at bar 5 -> 3% move: kept under default 2%, dropped under a 5% threshold
    assert propose_structures(df, pivots) != []
    assert propose_structures(df, pivots, StructureConfig(min_move=0.05)) == []


def test_frozen_v1_params_are_locked():
    assert DEFAULT_CONFIG.local_scale == 72
    assert DEFAULT_CONFIG.min_move == 0.02
    assert DEFAULT_CONFIG.max_horizon == 480
    assert DEFAULT_CONFIG.min_bars == 3
