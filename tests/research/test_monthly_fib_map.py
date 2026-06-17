"""Tests for monthly_fib_map — 1M source-fib map (clean + levels views)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import fibengine.research.monthly_fib_map as mod
from fibengine.research.monthly_fib_map import (
    _load_fibs,
    _short_id,
    render_monthly_fib_map,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _monthly_df(start: str = "2020-01-01", periods: int = 80) -> pd.DataFrame:
    idx = pd.date_range(start, periods=periods, freq="MS", tz="UTC")  # month-start
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
    # An events sidecar that must be ignored by the loader.
    (fib_dir / "fib_BTC-USD_1M_20201001T000000_events.json").write_text("{}", encoding="utf-8")


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------


def test_short_id_from_anchor_a(tmp_path):
    fib_dir = tmp_path / "fibs"
    fib_dir.mkdir()
    p = _write_fib(
        fib_dir, "20201001T000000", "2020-10-01T00:00:00Z", 10000.0, "2021-04-01T00:00:00Z", 64000.0
    )
    ann = mod.load_annotation(p)
    assert _short_id(ann) == "20201001"


def test_load_fibs_skips_events_sidecars(tmp_path):
    fib_dir = tmp_path / "fibs"
    _seed_fibs(fib_dir)
    fibs = _load_fibs(fib_dir)
    # Two base fibs loaded; the _events.json sidecar is excluded.
    assert len(fibs) == 2
    assert [_short_id(a) for a in fibs] == ["20201001", "20210401"]  # time-sorted


# ---------------------------------------------------------------------------
# Rendering tests
# ---------------------------------------------------------------------------


def test_render_creates_two_views_and_index(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_fibs(fib_dir)
    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: _monthly_df())

    out_dir = tmp_path / "map"
    result = render_monthly_fib_map(fib_dir=fib_dir, out_root=out_dir)

    assert result.clean.exists() and result.clean.stat().st_size > 1000
    assert result.levels.exists() and result.levels.stat().st_size > 1000
    assert result.index.exists()
    # All loaded fibs are drawn — no silent dropout.
    assert result.fib_count == 2
    assert result.drawn == 2
    assert result.skipped == []

    index_text = result.index.read_text(encoding="utf-8")
    assert "20201001" in index_text
    assert "20210401" in index_text
    assert "Monthly fib map" in index_text
    # Index is self-contained: per-fib level table with all six ratios + a price.
    assert "## Levels" in index_text
    for ratio in ("0.382", "0.618", "0.786"):
        assert ratio in index_text
    # 0.5 level of the synthetic up-fib = (10000 + 64000) / 2 = 37000.
    assert "37,000" in index_text
    # Default run produces no labeled PNG.
    assert result.levels_labeled is None


def test_label_levels_emits_labeled_png(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_fibs(fib_dir)
    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: _monthly_df())

    out_dir = tmp_path / "map"
    result = render_monthly_fib_map(fib_dir=fib_dir, out_root=out_dir, label_levels=True)

    assert result.levels_labeled is not None
    assert result.levels_labeled.exists()
    assert result.levels_labeled.name == "monthly_fib_map_levels_labeled.png"
    assert result.levels_labeled.stat().st_size > 1000
    # The default views are still produced and distinct from the labeled one.
    assert result.levels.exists() and result.levels != result.levels_labeled


def test_anchor_beyond_cache_is_surfaced_not_skipped(tmp_path, monkeypatch):
    """A fib whose anchor falls past the candle range is reported, not dropped silently."""
    fib_dir = tmp_path / "fibs"
    _seed_fibs(fib_dir)
    # anchor_b in 2099 sits well beyond an 80-month cache starting 2020-01.
    _write_fib(
        fib_dir,
        "20991201T000000",
        "2099-12-01T00:00:00Z",
        100000.0,
        "2100-06-01T00:00:00Z",
        50000.0,
    )
    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: _monthly_df())

    result = render_monthly_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")
    assert result.fib_count == 3
    assert result.drawn == 2
    assert len(result.skipped) == 1
    assert "20991201" in result.skipped[0]
    assert "20991201" in result.index.read_text(encoding="utf-8")


def test_no_fibs_raises(tmp_path, monkeypatch):
    fib_dir = tmp_path / "empty"
    fib_dir.mkdir()
    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: _monthly_df())
    try:
        render_monthly_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")
    except FileNotFoundError as exc:
        assert "fib_*.json" in str(exc)
    else:
        raise AssertionError("expected FileNotFoundError for empty fib dir")
