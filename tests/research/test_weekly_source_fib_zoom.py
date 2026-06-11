"""Tests for weekly_source_fib_zoom — per-fib windowed 1W source-fib confirmation.

Covers per-fib rendering + shared index, the bounded A→B+context window, the
fail-closed guards (reused from weekly_source_fib_map), --fib-id filtering,
surfaced-not-hidden out-of-range anchors, bounded snap, and the absence of any
review_sample.csv dependency.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import fibengine.research.weekly_source_fib_zoom as mod
from fibengine.research.weekly_source_fib_zoom import (
    _SNAP_WINDOW,
    _resolve_anchor_pos,
    render_weekly_source_fib_zoom,
)

_FREQ = {"1w": "W-THU", "1d": "D", "4h": "4h"}
_PERIODS = {"1w": 120, "1d": 500, "4h": 900}
_START = {"1w": "2020-01-02", "1d": "2020-06-01", "4h": "2020-11-01"}


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
    # Anchors land on the 4H grid (start 2020-11-01) at bars 384 and 636.
    _write_fib(fib_dir, "20210104T000000", "2021-01-04T00:00:00Z", 10000.0,
               "2021-02-15T00:00:00Z", 20000.0)  # up
    _write_fib(fib_dir, "20210215T000000", "2021-02-15T00:00:00Z", 20000.0,
               "2021-03-15T00:00:00Z", 14000.0)  # down
    (fib_dir / "fib_BTC-USD_1w_20210104T000000_events.json").write_text("{}", encoding="utf-8")


def test_render_creates_per_fib_clean_levels_and_index(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_valid(fib_dir)
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    out_dir = tmp_path / "zoom"
    result = render_weekly_source_fib_zoom(fib_dir=fib_dir, out_root=out_dir)

    assert result.fib_count == 2
    for f in result.fibs:
        z = f.per_tf["4h"]
        assert z.skipped is None
        assert z.clean.name == "4h_clean.png" and z.levels.name == "4h_levels.png"
        # Per-fib subdirectory keyed by fib_id.
        assert z.clean.parent.name == f.fib_id
        assert z.clean.exists() and z.clean.stat().st_size > 1000
        assert z.levels.exists() and z.levels.stat().st_size > 1000

    index_text = result.index.read_text(encoding="utf-8")
    assert result.index.name == "weekly_source_fib_zoom_index.md"
    assert "Weekly source fib zoom" in index_text
    assert "20210104" in index_text and "20210215" in index_text
    # Strict separation messaging.
    assert "No events" in index_text or "no events" in index_text


def test_label_levels_emits_labeled_png(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_valid(fib_dir)
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_weekly_source_fib_zoom(
        fib_dir=fib_dir, out_root=tmp_path / "zoom", fib_id="20210104", label_levels=True
    )
    z = result.fibs[0].per_tf["4h"]
    assert z.levels_labeled is not None and z.levels_labeled.exists()
    assert z.levels_labeled.name == "4h_levels_labeled.png"


def test_window_is_bounded_not_full_era(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_valid(fib_dir)
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)
    # Pin snap to exact-nearest so the window math is deterministic.
    monkeypatch.setattr(mod, "_SNAP_WINDOW", {"4h": 0})

    full_len = len(_df("4h"))
    res = render_weekly_source_fib_zoom(
        fib_dir=fib_dir, out_root=tmp_path / "z1", fib_id="20210104",
        context_bars=10, post_bars=10,
    )
    bars = res.fibs[0].per_tf["4h"].bars
    # Anchors at bars 384/636 → span 252, +10 pre +10 post +1 = 273, well under 900.
    assert bars == 273
    assert 0 < bars < full_len

    # Wider context → strictly more bars (window is context-driven, not full era).
    res2 = render_weekly_source_fib_zoom(
        fib_dir=fib_dir, out_root=tmp_path / "z2", fib_id="20210104",
        context_bars=100, post_bars=100,
    )
    assert res2.fibs[0].per_tf["4h"].bars > bars


def test_out_of_range_anchor_skipped_and_reported(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_valid(fib_dir)
    _write_fib(fib_dir, "20991201T000000", "2099-12-01T00:00:00Z", 100000.0,
               "2100-06-01T00:00:00Z", 50000.0)
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_weekly_source_fib_zoom(fib_dir=fib_dir, out_root=tmp_path / "zoom")
    assert result.fib_count == 3
    far = next(f for f in result.fibs if f.short_id == "20991201")
    z = far.per_tf["4h"]
    assert z.skipped is not None and z.clean is None and z.bars == 0
    index_text = result.index.read_text(encoding="utf-8")
    assert "20991201" in index_text and "skipped" in index_text.lower()


def test_fib_id_filters_to_one(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_valid(fib_dir)
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_weekly_source_fib_zoom(
        fib_dir=fib_dir, out_root=tmp_path / "zoom", fib_id="20210215"
    )
    assert result.fib_count == 1
    assert result.fibs[0].short_id == "20210215"


def test_unknown_fib_id_fails(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_valid(fib_dir)
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)
    with pytest.raises(ValueError, match="matched no fib"):
        render_weekly_source_fib_zoom(fib_dir=fib_dir, out_root=tmp_path / "zoom", fib_id="nope")


def test_no_review_sample_csv_required(tmp_path, monkeypatch):
    """Renders with only fib JSONs present — no review_sample.csv anywhere."""
    fib_dir = tmp_path / "fibs"
    _seed_valid(fib_dir)
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)
    result = render_weekly_source_fib_zoom(fib_dir=fib_dir, out_root=tmp_path / "zoom")
    assert result.fib_count == 2
    assert not list(tmp_path.rglob("review_sample.csv"))


def test_empty_fib_dir_fails(tmp_path, monkeypatch):
    fib_dir = tmp_path / "empty"
    fib_dir.mkdir()
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)
    with pytest.raises(FileNotFoundError, match="fib_.*json"):
        render_weekly_source_fib_zoom(fib_dir=fib_dir, out_root=tmp_path / "zoom")


def test_non_1w_timeframe_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, "20210104T000000", "2021-01-04T00:00:00Z", 10000.0,
               "2021-02-15T00:00:00Z", 20000.0, timeframe="1M")
    with pytest.raises(ValueError, match="timeframe"):
        render_weekly_source_fib_zoom(fib_dir=fib_dir, out_root=tmp_path / "zoom")


def test_pointing_at_1m_dir_fails(tmp_path):
    fib_dir = tmp_path / "1M"
    _write_fib(fib_dir, "20201001T000000", "2020-10-01T00:00:00Z", 10000.0,
               "2021-04-01T00:00:00Z", 64000.0, timeframe="1M")
    with pytest.raises(ValueError, match="not a 1W fib"):
        render_weekly_source_fib_zoom(fib_dir=fib_dir, out_root=tmp_path / "zoom")


def test_wrong_profile_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, "20210104T000000", "2021-01-04T00:00:00Z", 10000.0,
               "2021-02-15T00:00:00Z", 20000.0, profile="some_linear_profile")
    with pytest.raises(ValueError, match="levels_profile"):
        render_weekly_source_fib_zoom(fib_dir=fib_dir, out_root=tmp_path / "zoom")


def test_wrong_scale_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, "20210104T000000", "2021-01-04T00:00:00Z", 10000.0,
               "2021-02-15T00:00:00Z", 20000.0, scale="linear")
    with pytest.raises(ValueError, match="scale_mode"):
        render_weekly_source_fib_zoom(fib_dir=fib_dir, out_root=tmp_path / "zoom")


def test_forbidden_ratio_0236_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, "20210104T000000", "2021-01-04T00:00:00Z", 10000.0,
               "2021-02-15T00:00:00Z", 20000.0,
               ratios=(0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0))
    with pytest.raises(ValueError, match="0.236"):
        render_weekly_source_fib_zoom(fib_dir=fib_dir, out_root=tmp_path / "zoom")


def test_non_human_source_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, "20210104T000000", "2021-01-04T00:00:00Z", 10000.0,
               "2021-02-15T00:00:00Z", 20000.0,
               created_by="machine", source="auto_fib_detector")
    with pytest.raises(ValueError, match="non-manual origin"):
        render_weekly_source_fib_zoom(fib_dir=fib_dir, out_root=tmp_path / "zoom")


def test_candidate_fib_id_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, "20210104T000000", "2021-01-04T00:00:00Z", 10000.0,
               "2021-02-15T00:00:00Z", 20000.0,
               fib_id="fib_BTC-USD_1w_candidate_20210104")
    with pytest.raises(ValueError, match="candidate"):
        render_weekly_source_fib_zoom(fib_dir=fib_dir, out_root=tmp_path / "zoom")


def test_4h_snap_window_is_bounded_and_positive():
    assert _SNAP_WINDOW["4h"] > 0


def test_bounded_snap_lands_on_price_matching_bar():
    idx = pd.date_range("2021-01-01", periods=8, freq="D", tz="UTC")
    highs = [110.0] * 8
    lows = [90.0] * 8
    highs[5] = 200.0
    df = pd.DataFrame(
        {"open": [100.0] * 8, "high": highs, "low": lows, "close": [100.0] * 8,
         "volume": [1.0] * 8},
        index=idx,
    )
    # window>0 snaps to the price-matching bar; window=0 stays time-nearest.
    assert _resolve_anchor_pos(df, idx[2], 195.0, 42) == 5
    assert _resolve_anchor_pos(df, idx[2], 195.0, 0) == 2
