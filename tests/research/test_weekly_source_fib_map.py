"""Tests for weekly_source_fib_map — true 1W source fibs on 1W/1D/4H candles.

Covers rendering across chart timeframes, the shared index, the fail-closed
guards (timeframe/profile/scale/ratio/origin), the snap dispatch (exact on 1W,
bounded on finer TFs), and surfaced-not-hidden out-of-range anchors.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import fibengine.research.weekly_source_fib_map as mod
from fibengine.research.weekly_source_fib_map import (
    _SNAP_WINDOW,
    _nearest_pos,
    _resolve_anchor_pos,
    render_weekly_source_fib_map,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FREQ = {"1w": "W-THU", "1d": "D", "4h": "4h"}
_PERIODS = {"1w": 30, "1d": 160, "4h": 660}
_START = {"1w": "2020-11-05", "1d": "2020-12-01", "4h": "2020-12-15"}


def _df(tf: str) -> pd.DataFrame:
    idx = pd.date_range(_START[tf], periods=_PERIODS[tf], freq=_FREQ[tf], tz="UTC")
    base = np.linspace(8000, 90000, len(idx))
    return pd.DataFrame(
        {
            "open": base * 0.98,
            "high": base * 1.05,
            "low": base * 0.95,
            "close": base,
            "volume": np.ones(len(idx)),
        },
        index=idx,
    )


def _fake_load_candles(cfg, **_kw) -> pd.DataFrame:
    """Return a chart-TF-appropriate synthetic frame based on cfg.timeframe."""
    return _df(cfg.timeframe)


def _write_fib(
    fib_dir: Path,
    sid: str,
    a_time: str,
    a_price: float,
    b_time: str,
    b_price: float,
    *,
    timeframe: str = "1w",
    profile: str = "tradingview_log_chamoun",
    scale: str = "log",
    created_by: str = "human",
    source: str = "manual_labeling_tool",
    ratios: tuple[float, ...] = (0.0, 0.382, 0.5, 0.618, 0.786, 1.0),
    fib_id: str | None = None,
) -> Path:
    fib_dir.mkdir(parents=True, exist_ok=True)
    direction = "up" if b_price > a_price else "down"
    lo, hi = min(a_price, b_price), max(a_price, b_price)
    fid = fib_id or f"fib_BTC-USD_{timeframe}_{sid}"
    payload = {
        "fib_id": fid,
        "symbol": "BTC/USD",
        "timeframe": timeframe,
        "exchange": "bitfinex",
        "created_by": created_by,
        "source": source,
        "scale_mode": scale,
        "levels_profile": profile,
        "anchor_a": {"time": a_time, "price": a_price},
        "anchor_b": {"time": b_time, "price": b_price},
        "direction": direction,
        "levels": [{"ratio": r, "price": lo + r * (hi - lo)} for r in ratios],
    }
    path = fib_dir / f"fib_BTC-USD_{timeframe}_{sid}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _seed_valid(fib_dir: Path) -> None:
    """Two valid 1W source fibs + an events sidecar that must be ignored."""
    _write_fib(fib_dir, "20210104T000000", "2021-01-04T00:00:00Z", 10000.0,
               "2021-02-15T00:00:00Z", 20000.0)  # up
    _write_fib(fib_dir, "20210215T000000", "2021-02-15T00:00:00Z", 20000.0,
               "2021-03-15T00:00:00Z", 14000.0)  # down
    (fib_dir / "fib_BTC-USD_1w_20210104T000000_events.json").write_text("{}", encoding="utf-8")


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def test_render_creates_clean_levels_per_tf_and_shared_index(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_valid(fib_dir)
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    out_dir = tmp_path / "map"
    result = render_weekly_source_fib_map(fib_dir=fib_dir, out_root=out_dir)

    assert result.fib_count == 2
    assert set(result.per_tf) == {"1w", "1d", "4h"}
    for tf in ("1w", "1d", "4h"):
        art = result.per_tf[tf]
        assert art.clean.name == f"weekly_source_fib_map_{tf}_clean.png"
        assert art.levels.name == f"weekly_source_fib_map_{tf}_levels.png"
        assert art.clean.exists() and art.clean.stat().st_size > 1000
        assert art.levels.exists() and art.levels.stat().st_size > 1000
        assert art.drawn == 2
        assert art.skipped == []

    index_text = result.index.read_text(encoding="utf-8")
    assert result.index.name == "weekly_source_fib_map_index.md"
    assert "Weekly source fib map" in index_text
    assert "1W source fibs" in index_text
    assert "20210104" in index_text and "20210215" in index_text
    # Self-contained level table + per-timeframe sections.
    assert "## Levels" in index_text
    for tf in ("1w", "1d", "4h"):
        assert f"### {tf}" in index_text
    # Strict separation: the index states it is not the 1M→1W projection artifact.
    assert "no 1M fibs" in index_text
    assert "Not the 1M→1W projection map" in index_text


def test_chart_tfs_subset_is_respected(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_valid(fib_dir)
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_weekly_source_fib_map(
        fib_dir=fib_dir, out_root=tmp_path / "map", chart_tfs=("1w",)
    )
    assert set(result.per_tf) == {"1w"}
    assert not (tmp_path / "map" / "weekly_source_fib_map_1d_clean.png").exists()


def test_label_levels_emits_labeled_png_per_tf(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_valid(fib_dir)
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_weekly_source_fib_map(
        fib_dir=fib_dir, out_root=tmp_path / "map", chart_tfs=("1w",), label_levels=True
    )
    art = result.per_tf["1w"]
    assert art.levels_labeled is not None and art.levels_labeled.exists()
    assert art.levels_labeled.name == "weekly_source_fib_map_1w_levels_labeled.png"


def test_out_of_range_anchor_surfaced_not_hidden(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_valid(fib_dir)
    _write_fib(fib_dir, "20991201T000000", "2099-12-01T00:00:00Z", 100000.0,
               "2100-06-01T00:00:00Z", 50000.0)
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_weekly_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")
    assert result.fib_count == 3
    for tf in ("1w", "1d", "4h"):
        art = result.per_tf[tf]
        assert art.drawn == 2
        assert len(art.skipped) == 1 and "20991201" in art.skipped[0]
    assert "20991201" in result.index.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Fail-closed guards
# ---------------------------------------------------------------------------


def test_empty_fib_dir_fails(tmp_path, monkeypatch):
    fib_dir = tmp_path / "empty"
    fib_dir.mkdir()
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)
    with pytest.raises(FileNotFoundError, match="fib_.*json"):
        render_weekly_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")


def test_non_1w_timeframe_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, "20210104T000000", "2021-01-04T00:00:00Z", 10000.0,
               "2021-02-15T00:00:00Z", 20000.0, timeframe="1M")
    with pytest.raises(ValueError, match="timeframe"):
        render_weekly_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")


def test_pointing_at_1m_dir_fails(tmp_path):
    """A directory of 1M fibs (timeframe '1M') is refused — structural separation."""
    fib_dir = tmp_path / "1M"
    _write_fib(fib_dir, "20201001T000000", "2020-10-01T00:00:00Z", 10000.0,
               "2021-04-01T00:00:00Z", 64000.0, timeframe="1M")
    _write_fib(fib_dir, "20210401T000000", "2021-04-01T00:00:00Z", 64000.0,
               "2021-07-01T00:00:00Z", 30000.0, timeframe="1M")
    with pytest.raises(ValueError, match="not a 1W fib"):
        render_weekly_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")


def test_wrong_profile_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, "20210104T000000", "2021-01-04T00:00:00Z", 10000.0,
               "2021-02-15T00:00:00Z", 20000.0, profile="some_linear_profile")
    with pytest.raises(ValueError, match="levels_profile"):
        render_weekly_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")


def test_wrong_scale_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, "20210104T000000", "2021-01-04T00:00:00Z", 10000.0,
               "2021-02-15T00:00:00Z", 20000.0, scale="linear")
    with pytest.raises(ValueError, match="scale_mode"):
        render_weekly_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")


def test_forbidden_ratio_0236_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, "20210104T000000", "2021-01-04T00:00:00Z", 10000.0,
               "2021-02-15T00:00:00Z", 20000.0,
               ratios=(0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0))
    with pytest.raises(ValueError, match="0.236"):
        render_weekly_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")


def test_non_human_source_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, "20210104T000000", "2021-01-04T00:00:00Z", 10000.0,
               "2021-02-15T00:00:00Z", 20000.0,
               created_by="machine", source="auto_fib_detector")
    with pytest.raises(ValueError, match="non-manual origin"):
        render_weekly_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")


def test_candidate_fib_id_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, "20210104T000000", "2021-01-04T00:00:00Z", 10000.0,
               "2021-02-15T00:00:00Z", 20000.0,
               fib_id="fib_BTC-USD_1w_candidate_20210104")
    with pytest.raises(ValueError, match="candidate"):
        render_weekly_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")


# ---------------------------------------------------------------------------
# Snap dispatch
# ---------------------------------------------------------------------------


def _spiky_df():
    """8 daily bars, flat ~$100 except bar 5 which spikes to $200."""
    idx = pd.date_range("2021-01-01", periods=8, freq="D", tz="UTC")
    highs = [110.0] * 8
    lows = [90.0] * 8
    highs[5] = 200.0
    return pd.DataFrame(
        {"open": [100.0] * 8, "high": highs, "low": lows, "close": [100.0] * 8,
         "volume": [1.0] * 8},
        index=idx,
    )


def test_source_tf_window_is_zero():
    assert _SNAP_WINDOW["1w"] == 0
    assert _SNAP_WINDOW["1d"] > 0 and _SNAP_WINDOW["4h"] > 0


def test_window_zero_is_exact_nearest_no_snap():
    """window=0 (source TF) reproduces the drawn bar even if price mismatches."""
    df = _spiky_df()
    t = df.index[2]
    # Bar 2's range is [90,110]; the $195 extreme only exists in bar 5.
    assert _resolve_anchor_pos(df, t, 195.0, 0) == 2
    assert _resolve_anchor_pos(df, t, 195.0, 0) == _nearest_pos(df, t)


def test_bounded_window_snaps_to_price_matching_bar():
    """window>0 (finer TF) lands on the candle whose range hits the anchor price."""
    df = _spiky_df()
    assert _resolve_anchor_pos(df, df.index[2], 195.0, 7) == 5
    # In-range price near the time-nearest bar stays put (tie broken by time).
    assert _resolve_anchor_pos(df, df.index[2], 100.0, 7) == 2


def test_out_of_range_time_returns_none():
    df = _spiky_df()
    assert _resolve_anchor_pos(df, pd.Timestamp("1990-01-01", tz="UTC"), 100.0, 7) is None
    assert _resolve_anchor_pos(df, pd.Timestamp("1990-01-01", tz="UTC"), 100.0, 0) is None
