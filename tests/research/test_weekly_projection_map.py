"""Tests for weekly_projection_map — 1M→1W source-segment map (clean + levels)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import fibengine.research.weekly_projection_map as mod
from fibengine.research.weekly_projection_map import (
    _swing_snap_pos,
    render_weekly_projection_map,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _weekly_df(start: str = "2020-01-02", periods: int = 340) -> pd.DataFrame:
    idx = pd.date_range(start, periods=periods, freq="W-THU", tz="UTC")  # weekly bars
    base = np.linspace(8000, 90000, periods)
    return pd.DataFrame(
        {
            "open": base * 0.98,
            "high": base * 1.05,
            "low": base * 0.95,
            "close": base,
            "volume": np.ones(periods),
        },
        index=idx,
    )


def _write_fib(path: Path, sid: str, a_time: str, a_price: float, b_time: str, b_price: float):
    direction = "up" if b_price > a_price else "down"
    lo, hi = min(a_price, b_price), max(a_price, b_price)
    payload = {
        "fib_id": f"fib_BTC-USD_1M_{sid}",
        "symbol": "BTC/USD",
        "timeframe": "1M",
        "exchange": "bitfinex",
        "created_by": "human",
        "source": "manual_labeling_tool",
        "scale_mode": "log",
        "levels_profile": "tradingview_log_chamoun",
        "anchor_a": {"time": a_time, "price": a_price},
        "anchor_b": {"time": b_time, "price": b_price},
        "direction": direction,
        "levels": [
            {"ratio": 0.0, "price": b_price},
            {"ratio": 0.5, "price": (lo + hi) / 2},
            {"ratio": 1.0, "price": a_price},
        ],
    }
    fib_path = path / f"fib_BTC-USD_1M_{sid}.json"
    fib_path.write_text(json.dumps(payload), encoding="utf-8")
    return fib_path


def _seed_fibs(fib_dir: Path) -> None:
    fib_dir.mkdir(parents=True, exist_ok=True)
    _write_fib(
        fib_dir, "20201001T000000", "2020-10-01T00:00:00Z", 10000.0, "2021-04-01T00:00:00Z", 64000.0
    )  # up
    _write_fib(
        fib_dir, "20210401T000000", "2021-04-01T00:00:00Z", 64000.0, "2021-07-01T00:00:00Z", 30000.0
    )  # down
    # Events sidecar that must be ignored by the loader.
    (fib_dir / "fib_BTC-USD_1M_20201001T000000_events.json").write_text("{}", encoding="utf-8")


# ---------------------------------------------------------------------------
# Rendering tests
# ---------------------------------------------------------------------------


def test_render_creates_two_views_and_index(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_fibs(fib_dir)
    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: _weekly_df())

    out_dir = tmp_path / "map"
    result = render_weekly_projection_map(fib_dir=fib_dir, out_root=out_dir)

    assert result.clean.exists() and result.clean.stat().st_size > 1000
    assert result.clean.name == "weekly_projection_map_clean.png"
    assert result.levels.exists() and result.levels.stat().st_size > 1000
    assert result.levels.name == "weekly_projection_map_levels.png"
    assert result.index.exists()
    # All loaded fibs drawn — no silent dropout.
    assert result.fib_count == 2
    assert result.drawn == 2
    assert result.skipped == []

    index_text = result.index.read_text(encoding="utf-8")
    assert "20201001" in index_text
    assert "20210401" in index_text
    assert "source_segment" in index_text
    # Self-contained level table: all six ratio headers + a known price.
    assert "## Levels" in index_text
    for ratio in ("0.382", "0.618", "0.786"):
        assert ratio in index_text
    assert "37,000" in index_text  # 0.5 of the synthetic up-fib = (10000+64000)/2


def test_anchor_beyond_cache_is_surfaced_not_skipped(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_fibs(fib_dir)
    _write_fib(
        fib_dir,
        "20991201T000000",
        "2099-12-01T00:00:00Z",
        100000.0,
        "2100-06-01T00:00:00Z",
        50000.0,
    )
    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: _weekly_df())

    result = render_weekly_projection_map(fib_dir=fib_dir, out_root=tmp_path / "map")
    assert result.fib_count == 3
    assert result.drawn == 2
    assert len(result.skipped) == 1
    assert "20991201" in result.skipped[0]
    assert "20991201" in result.index.read_text(encoding="utf-8")


def test_swing_snap_picks_price_matching_week(tmp_path):
    """Snap lands on the weekly bar whose high/low hits the anchor price, not just
    the time-nearest bar."""
    idx = pd.date_range("2021-01-07", periods=8, freq="W-THU", tz="UTC")
    # Flat $100 everywhere except bar 5, which spikes up to $200.
    highs = [110.0] * 8
    lows = [90.0] * 8
    highs[5] = 200.0
    df = pd.DataFrame(
        {
            "open": [100.0] * 8,
            "high": highs,
            "low": lows,
            "close": [100.0] * 8,
            "volume": [1.0] * 8,
        },
        index=idx,
    )
    # Anchor time is bar 2, but the $195 extreme only exists in bar 5.
    pos = _swing_snap_pos(df, idx[2], 195.0)
    assert pos == 5
    # In-range price near the time-nearest bar stays put (tie broken by time).
    assert _swing_snap_pos(df, idx[2], 100.0) == 2
    # Out-of-range time → None (same contract as _nearest_pos).
    assert _swing_snap_pos(df, pd.Timestamp("1990-01-01", tz="UTC"), 100.0) is None


def test_no_fibs_raises(tmp_path, monkeypatch):
    fib_dir = tmp_path / "empty"
    fib_dir.mkdir()
    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: _weekly_df())
    try:
        render_weekly_projection_map(fib_dir=fib_dir, out_root=tmp_path / "map")
    except FileNotFoundError as exc:
        assert "fib_*.json" in str(exc)
    else:
        raise AssertionError("expected FileNotFoundError for empty fib dir")
