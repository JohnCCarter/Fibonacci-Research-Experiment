"""Tests for fourh_source_fib_map — true 4H source fibs on annual 4H candle maps.

Covers per-year grouping, the dense-year half-year split, the shared index, the
fail-closed guards (timeframe/profile/scale/ratio/origin), fib-span windowing (a
December-anchored fib whose anchor_b crosses the year boundary still renders), and
surfaced-not-hidden out-of-range anchors.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import fibengine.research.fourh_source_fib_map as mod
from fibengine.research.fourh_source_fib_map import (
    SOURCE_TF,
    _group_by_year,
    render_fourh_source_fib_map,
)


def _df() -> pd.DataFrame:
    """One long 4H frame spanning 2016-12 → 2018-06 so multi-year groups fit."""
    idx = pd.date_range("2016-12-01", periods=3500, freq="4h", tz="UTC")
    base = np.linspace(700, 20000, len(idx))
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
    return _df()


def _write_fib(
    fib_dir: Path,
    *,
    sid: str = "20170105T040000",
    a_time: str = "2017-01-05T04:00:00Z",
    a_price: float = 1166.0,
    b_time: str = "2017-01-07T04:00:00Z",
    b_price: float = 815.0,
    timeframe: str = "4h",
    profile: str = "tradingview_log_chamoun",
    scale: str = "log",
    created_by: str = "human",
    source: str = "manual_labeling_tool",
    ratios: tuple[float, ...] = (0.0, 0.382, 0.5, 0.618, 0.786, 1.0),
    fib_id: str | None = None,
) -> Path:
    """Write one valid 4H source fib; override any field for the guard tests."""
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
    """Two valid 4H source fibs (2017 + 2018) + an events sidecar that is ignored."""
    _write_fib(fib_dir)  # 2017 down @ 20170105
    _write_fib(
        fib_dir,
        sid="20180110T040000",
        a_time="2018-01-10T04:00:00Z",
        a_price=14000.0,
        b_time="2018-02-06T04:00:00Z",
        b_price=6000.0,
    )  # 2018 down
    (fib_dir / "fib_BTC-USD_4h_20170105T040000_events.json").write_text("{}", encoding="utf-8")


def test_render_creates_clean_levels_per_group_and_shared_index(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_valid(fib_dir)
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_fourh_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")

    assert result.fib_count == 2
    labels = [art.label for art in result.per_group]
    assert labels == ["2017", "2018"]  # chronological, sub-threshold → one per year
    for art in result.per_group:
        assert art.drawn == 1
        assert art.skipped == []
        assert art.clean.name == f"fourh_source_fib_map_{art.label}_4h_clean.png"
        assert art.levels.name == f"fourh_source_fib_map_{art.label}_4h_levels.png"
        assert art.clean.exists() and art.clean.stat().st_size > 1000
        assert art.levels.exists() and art.levels.stat().st_size > 1000

    index_text = result.index.read_text(encoding="utf-8")
    assert result.index.name == "fourh_source_fib_map_index.md"
    assert "4H source fib map" in index_text
    assert "4H source" in index_text
    assert "20170105" in index_text and "20180110" in index_text
    assert "## Groups" in index_text
    assert "## Levels" in index_text  # self-contained level table
    # Strict separation: source-quality review, not reaction-review.
    assert "not** reaction-review" in index_text


def test_dense_year_is_split_into_half_years(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    # 4 fibs in 2017 (2 in H1, 2 in H2) split with a threshold of 3.
    _write_fib(fib_dir, sid="20170105T040000", a_time="2017-01-05T04:00:00Z")
    _write_fib(fib_dir, sid="20170320T040000", a_time="2017-03-20T04:00:00Z")
    _write_fib(fib_dir, sid="20170815T040000", a_time="2017-08-15T04:00:00Z")
    _write_fib(fib_dir, sid="20171110T040000", a_time="2017-11-10T04:00:00Z")
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_fourh_source_fib_map(
        fib_dir=fib_dir, out_root=tmp_path / "map", dense_threshold=3
    )
    labels = [art.label for art in result.per_group]
    assert labels == ["2017_h1", "2017_h2"]
    assert {art.drawn for art in result.per_group} == {2}
    assert "Half-year splits: 2017_h1, 2017_h2" in result.index.read_text(encoding="utf-8")


def test_december_fib_crossing_year_boundary_renders_full_leg(tmp_path, monkeypatch):
    """anchor_a in Dem 2017, anchor_b in Jan 2018: span-window must not drop it."""
    fib_dir = tmp_path / "fibs"
    _write_fib(
        fib_dir,
        sid="20171228T040000",
        a_time="2017-12-28T04:00:00Z",
        a_price=14000.0,
        b_time="2018-01-15T04:00:00Z",
        b_price=10000.0,
    )
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_fourh_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")
    assert [art.label for art in result.per_group] == ["2017"]
    art = result.per_group[0]
    assert art.drawn == 1 and art.skipped == []
    # The window's right edge must reach into 2018 to cover anchor_b.
    assert art.window_end >= "2018-01-15"


def test_out_of_range_anchor_surfaced_not_hidden(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _seed_valid(fib_dir)
    _write_fib(
        fib_dir,
        sid="20991201T040000",
        a_time="2099-12-01T04:00:00Z",
        a_price=100000.0,
        b_time="2099-12-20T04:00:00Z",
        b_price=50000.0,
    )
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_fourh_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")
    assert result.fib_count == 3
    by_label = {art.label: art for art in result.per_group}
    assert by_label["2099"].drawn == 0
    assert len(by_label["2099"].skipped) == 1 and "20991201" in by_label["2099"].skipped[0]
    assert "20991201" in result.index.read_text(encoding="utf-8")


def test_label_levels_emits_labeled_png_per_group(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir)
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_fourh_source_fib_map(
        fib_dir=fib_dir, out_root=tmp_path / "map", label_levels=True
    )
    art = result.per_group[0]
    assert art.levels_labeled is not None and art.levels_labeled.exists()
    assert art.levels_labeled.name == "fourh_source_fib_map_2017_4h_levels_labeled.png"


def test_empty_fib_dir_fails(tmp_path, monkeypatch):
    fib_dir = tmp_path / "empty"
    fib_dir.mkdir()
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)
    with pytest.raises(FileNotFoundError, match="fib_.*json"):
        render_fourh_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")


def test_pointing_at_1d_dir_fails(tmp_path):
    """A directory of 1D fibs (timeframe '1d') is refused — structural separation."""
    fib_dir = tmp_path / "1d"
    _write_fib(fib_dir, sid="20201001T000000", timeframe="1d")
    with pytest.raises(ValueError, match="not a 4H fib"):
        render_fourh_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")


@pytest.mark.parametrize(
    ("over", "match"),
    [
        ({"timeframe": "1d"}, "timeframe"),
        ({"profile": "some_linear_profile"}, "levels_profile"),
        ({"scale": "linear"}, "scale_mode"),
        ({"ratios": (0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0)}, "0.236"),
        ({"created_by": "machine", "source": "auto_fib_detector"}, "non-manual origin"),
        ({"fib_id": "fib_BTC-USD_4h_candidate_20170105"}, "candidate"),
    ],
)
def test_fail_closed_guard_rejects(tmp_path, over, match):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, **over)
    with pytest.raises(ValueError, match=match):
        render_fourh_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "map")


def test_group_by_year_chronological_and_split():
    """Unit-level: grouping orders years and splits only the dense one."""
    fib_dir = Path()
    del fib_dir

    class _A:
        def __init__(self, t):
            self.anchor_a = type("X", (), {"time": t})()

    fibs = [
        _A("2018-03-01T04:00:00Z"),
        _A("2017-02-01T04:00:00Z"),
        _A("2017-09-01T04:00:00Z"),
        _A("2017-04-01T04:00:00Z"),
    ]
    groups = _group_by_year(fibs, dense_threshold=2)
    labels = [g[0] for g in groups]
    assert labels == ["2017_h1", "2017_h2", "2018"]
    assert SOURCE_TF == "4h"
