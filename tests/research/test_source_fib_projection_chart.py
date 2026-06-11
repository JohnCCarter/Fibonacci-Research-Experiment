"""Tests for source_fib_projection_chart (Issue #30 Phase 2 — visual review)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

import fibengine.research.source_fib_projection_chart as mod
from fibengine.research.source_fib_projection_chart import (
    _cluster_windows,
    render_all_charts,
    render_projection_chart,
)


def _df(closes: list[float], *, start: str = "2024-01-01") -> pd.DataFrame:
    idx = pd.date_range(start, periods=len(closes), freq="D", tz="UTC")
    arr = np.array(closes, dtype=float)
    return pd.DataFrame(
        {
            "open": arr * 0.99,
            "high": arr * 1.01,
            "low": arr * 0.98,
            "close": arr,
            "volume": np.ones(len(arr)),
        },
        index=idx,
    )


def _write_fib_json(path: Path) -> Path:
    payload = {
        "fib_id": "fib_BTC-USD_1M_chart_test",
        "symbol": "BTC/USD",
        "timeframe": "1M",
        "exchange": "bitfinex",
        "created_by": "human",
        "source": "manual_labeling_tool",
        "scale_mode": "log",
        "levels_profile": "tradingview_log_chamoun",
        "human_highlights": [],
        "anchor_a": {"time": "2020-01-01T00:00:00Z", "price": 10000.0},
        "anchor_b": {"time": "2020-03-01T00:00:00Z", "price": 5000.0},
        "direction": "down",
        "levels": [
            {"ratio": 0.0, "price": 5000.0},
            {"ratio": 0.382, "price": 6910.0},
            {"ratio": 0.5, "price": 7071.0},
            {"ratio": 0.618, "price": 7236.0},
            {"ratio": 0.786, "price": 7492.0},
            {"ratio": 1.0, "price": 10000.0},
        ],
    }
    fib_path = path / "fib_BTC-USD_1M_chart_test.json"
    fib_path.write_text(json.dumps(payload), encoding="utf-8")
    return fib_path


def _row(event_id, chart_tf, fib_level, fib_price, role, bar, t, relation, cand):
    return {
        "event_id": event_id,
        "source_tf": "1M",
        "chart_tf": chart_tf,
        "fib_id": "fib_BTC-USD_1M_chart_test",
        "symbol": "BTC/USD",
        "exchange": "bitfinex",
        "fib_level": fib_level,
        "fib_price": fib_price,
        "level_role": role,
        "event_bar": bar,
        "event_time": t,
        "relation": relation,
        "auto_candidate": cand,
        "touch_type": "close_below",
        "approach_side": "above",
        "event_label": f"1M {fib_level} {relation} by {chart_tf} candle",
    }


def _write_csv(review_dir: Path, rows: list[dict]) -> None:
    csv_path = review_dir / "review_sample.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_review_csv(review_dir: Path) -> None:
    """Three 1d events (touch/cross/above) clustered in early January."""
    rows = [
        _row(
            "e1",
            "1d",
            "0.5",
            "7071.0",
            "retracement",
            "5",
            "2024-01-06T00:00:00+00:00",
            "touch",
            "rejection_candidate",
        ),
        _row(
            "e2",
            "1d",
            "0.0",
            "5000.0",
            "boundary",
            "8",
            "2024-01-09T00:00:00+00:00",
            "cross",
            "continuation_candidate",
        ),
        _row(
            "e3",
            "1d",
            "0.382",
            "6910.0",
            "retracement",
            "3",
            "2024-01-04T00:00:00+00:00",
            "above",
            "rejection_candidate",
        ),
    ]
    _write_csv(review_dir, rows)


def test_render_creates_human_fib_events_and_zoom(tmp_path, monkeypatch):
    """render_projection_chart returns a ChartSet with human_fib + events + zoom."""
    fib_path = _write_fib_json(tmp_path)
    df = _df(list(range(7000, 7025)), start="2024-01-01")
    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: df)

    review_dir = tmp_path / "review"
    review_dir.mkdir()
    _write_review_csv(review_dir)

    out_dir = tmp_path / "charts"
    cs = render_projection_chart(
        source_fib_path=fib_path,
        chart_tf="1d",
        out_root=out_dir,
        review_dir=review_dir,
    )

    # Clean human-fib view (no markers) comes first.
    assert cs.human_fib.exists(), f"human_fib not created at {cs.human_fib}"
    assert cs.human_fib.name == "1d_human_fib.png"
    assert cs.human_fib.parent.name == "human_fib"
    assert cs.human_fib.stat().st_size > 1000
    # Event overlay view is separate.
    assert cs.events.exists(), f"events not created at {cs.events}"
    assert cs.events.name == "1d_events.png"
    assert cs.events.parent.name == "events"
    assert cs.events.stat().st_size > 1000
    # Anchor zoom is always produced; clustered events add at least one more.
    assert cs.zoom, "no zoom charts produced"
    assert any(p.name == "1d_anchor.png" for p in cs.zoom)
    for p in cs.zoom:
        assert p.exists()
        assert p.parent.name == "zoom"


def test_render_all_charts_produces_chartset_per_tf(tmp_path, monkeypatch):
    """render_all_charts produces one ChartSet per requested timeframe."""
    fib_path = _write_fib_json(tmp_path)
    df = _df(list(range(7000, 7025)), start="2024-01-01")
    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: df)

    review_dir = tmp_path / "review"
    review_dir.mkdir()
    _write_review_csv(review_dir)

    out_dir = tmp_path / "charts_multi"
    results = render_all_charts(
        source_fib_path=fib_path,
        chart_timeframes=["1d", "1w"],
        out_root=out_dir,
        review_dir=review_dir,
    )

    assert set(results.keys()) == {"1d", "1w"}
    for tf, cs in results.items():
        assert cs.human_fib.exists(), f"human_fib missing for {tf}"
        assert cs.human_fib.name == f"{tf}_human_fib.png"
        assert cs.events.exists(), f"events missing for {tf}"
        assert cs.events.name == f"{tf}_events.png"
        assert cs.zoom and all(p.exists() for p in cs.zoom)


def test_render_no_events_still_produces_human_fib_and_anchor(tmp_path, monkeypatch):
    """A TF with no matching rows still gets human_fib + events + an anchor zoom."""
    fib_path = _write_fib_json(tmp_path)
    df = _df(list(range(7000, 7025)), start="2024-01-01")
    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: df)

    review_dir = tmp_path / "review_empty"
    review_dir.mkdir()
    _write_review_csv(review_dir)  # only 1d rows; request 4h

    out_dir = tmp_path / "charts_empty"
    cs = render_projection_chart(
        source_fib_path=fib_path,
        chart_tf="4h",
        out_root=out_dir,
        review_dir=review_dir,
    )

    assert cs.human_fib.exists()
    assert cs.human_fib.stat().st_size > 1000
    assert cs.events.exists()
    # No events → no cluster windows, but the anchor zoom is still rendered.
    assert [p.name for p in cs.zoom] == ["4h_anchor.png"]


def test_relation_filter_touch_only_runs(tmp_path, monkeypatch):
    """relation_filter narrows event markers without breaking rendering."""
    fib_path = _write_fib_json(tmp_path)
    df = _df(list(range(7000, 7025)), start="2024-01-01")
    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: df)

    review_dir = tmp_path / "review_filter"
    review_dir.mkdir()
    _write_review_csv(review_dir)

    out_dir = tmp_path / "charts_filter"
    cs = render_projection_chart(
        source_fib_path=fib_path,
        chart_tf="1d",
        out_root=out_dir,
        review_dir=review_dir,
        relation_filter="touch",
    )
    assert cs.events.exists()
    assert any(p.name == "1d_anchor.png" for p in cs.zoom)


def test_invalid_relation_filter_raises(tmp_path, monkeypatch):
    fib_path = _write_fib_json(tmp_path)
    df = _df(list(range(7000, 7025)), start="2024-01-01")
    monkeypatch.setattr(mod, "load_candles", lambda cfg, **kw: df)
    review_dir = tmp_path / "review_bad"
    review_dir.mkdir()
    _write_review_csv(review_dir)

    try:
        render_projection_chart(
            source_fib_path=fib_path,
            chart_tf="1d",
            out_root=tmp_path / "out",
            review_dir=review_dir,
            relation_filter="golden_zone",
        )
    except ValueError as exc:
        assert "relation_filter" in str(exc)
    else:
        raise AssertionError("expected ValueError for unknown relation_filter")


def test_cluster_windows_separates_distant_events():
    """Events farther apart than gap_bars produce separate windows."""
    df = _df(list(range(7000, 7050)), start="2024-01-01")  # 50 daily bars
    times = [df.index[1], df.index[30]]  # gap 29 > gap_bars
    windows = _cluster_windows(df, times, gap_bars=10, pad_bars=4, max_window_bars=120)
    assert len(windows) == 2
    (a0, b0), (a1, b1) = windows
    assert a0 <= 1 <= b0
    assert a1 <= 30 <= b1
    assert b0 < a1  # ordered, non-overlapping


def test_cluster_windows_splits_wide_dense_cluster():
    """A single dense cluster wider than max_window_bars is segmented."""
    df = _df(list(range(7000, 7200)), start="2024-01-01")  # 200 bars
    # Events every 8 bars from 0..184 — each gap <= gap_bars, so one cluster.
    times = [df.index[p] for p in range(0, 185, 8)]
    windows = _cluster_windows(df, times, gap_bars=10, pad_bars=6, max_window_bars=80)
    assert len(windows) >= 2, "wide cluster should split into multiple windows"
    # Segments are ordered and bounded by max_window_bars.
    for a, b in windows:
        assert b - a <= 80
    for (_a0, b0), (a1, _b1) in zip(windows, windows[1:], strict=False):
        assert a1 > b0


def test_cluster_windows_empty_for_no_events():
    df = _df(list(range(7000, 7025)), start="2024-01-01")
    assert _cluster_windows(df, [], gap_bars=10, pad_bars=6, max_window_bars=120) == []
