"""Tests for the single-fib declutter edit-mode (labeling tool + human_fib loader).

GUI rendering is not exercised (the tool ends in plt.show()); these cover the pure,
testable units: the fail-closed loader, the window helper, anchor preload, HTF-overlay
suppression, and that default behavior is unchanged when --edit-fib-id is absent.
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pandas as pd
import pytest

import fibengine.labeling.tool as tool
from fibengine.core.config import load_settings
from fibengine.labeling.human_fib import (
    FibAnchor,
    find_annotation,
    make_annotation,
)


def _write_fib(
    root: Path,
    *,
    fib_id: str = "fib_BTC-USD_4h_20171228T200000",
    symbol: str = "BTC/USD",
    timeframe: str = "4h",
    exchange: str = "bitfinex",
    subdir: str | None = None,
) -> Path:
    ann = make_annotation(
        symbol=symbol,
        timeframe=timeframe,
        exchange=exchange,
        anchor_a=FibAnchor(time="2017-12-28T20:00:00+00:00", price=13611.0),
        anchor_b=FibAnchor(time="2017-12-29T00:00:00+00:00", price=14940.0),
        fib_id=fib_id,
    )
    d = root / (subdir or f"{exchange}/BTC-USD/{timeframe}")
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{fib_id}.json"
    path.write_text(json.dumps(ann.to_dict(), indent=2), encoding="utf-8")
    return path


def test_find_annotation_loads_correct_fib(tmp_path):
    _write_fib(tmp_path)
    ann = find_annotation(
        "fib_BTC-USD_4h_20171228T200000",
        exchange="bitfinex",
        symbol="BTC/USD",
        timeframe="4h",
        root=tmp_path,
    )
    assert ann.fib_id == "fib_BTC-USD_4h_20171228T200000"
    assert ann.timeframe == "4h" and ann.symbol == "BTC/USD"


def test_unknown_fib_id_fails_clearly(tmp_path):
    _write_fib(tmp_path)
    with pytest.raises(FileNotFoundError, match="not found"):
        find_annotation(
            "fib_BTC-USD_4h_19990101T000000",
            exchange="bitfinex",
            symbol="BTC/USD",
            timeframe="4h",
            root=tmp_path,
        )


def test_ambiguous_fib_id_fails_clearly(tmp_path):
    _write_fib(tmp_path, subdir="a")
    _write_fib(tmp_path, subdir="b")
    with pytest.raises(ValueError, match="ambiguous"):
        find_annotation(
            "fib_BTC-USD_4h_20171228T200000",
            exchange="bitfinex",
            symbol="BTC/USD",
            timeframe="4h",
            root=tmp_path,
        )


def test_wrong_symbol_fails_clearly(tmp_path):
    _write_fib(tmp_path, symbol="ETH/USD")
    with pytest.raises(ValueError, match="symbol"):
        find_annotation(
            "fib_BTC-USD_4h_20171228T200000",
            exchange="bitfinex",
            symbol="BTC/USD",
            timeframe="4h",
            root=tmp_path,
        )


def test_wrong_timeframe_fails_clearly(tmp_path):
    _write_fib(tmp_path, timeframe="1d")
    with pytest.raises(ValueError, match="timeframe"):
        find_annotation(
            "fib_BTC-USD_4h_20171228T200000",
            exchange="bitfinex",
            symbol="BTC/USD",
            timeframe="4h",
            root=tmp_path,
        )


def test_load_does_not_mutate_json(tmp_path):
    path = _write_fib(tmp_path)
    before = path.read_bytes()
    find_annotation(
        "fib_BTC-USD_4h_20171228T200000",
        exchange="bitfinex",
        symbol="BTC/USD",
        timeframe="4h",
        root=tmp_path,
    )
    assert path.read_bytes() == before


def test_window_from_anchors_brackets_span():
    ann = make_annotation(
        symbol="BTC/USD",
        timeframe="4h",
        anchor_a=FibAnchor(time="2017-12-28T20:00:00+00:00", price=13611.0),
        anchor_b=FibAnchor(time="2017-12-29T00:00:00+00:00", price=14940.0),
    )
    start, end = tool._window_from_anchors(ann)
    a = pd.Timestamp("2017-12-28T20:00:00+00:00")
    b = pd.Timestamp("2017-12-29T00:00:00+00:00")
    assert start < a and end > b
    assert (a - start) >= pd.Timedelta(days=2)  # min context padding


def test_preload_fib_picks_maps_high_low_by_price():
    ann = make_annotation(
        symbol="BTC/USD",
        timeframe="4h",
        anchor_a=FibAnchor(time="2017-12-28T20:00:00+00:00", price=13611.0),
        anchor_b=FibAnchor(time="2017-12-29T00:00:00+00:00", price=14940.0),
    )
    df = pd.DataFrame(
        {"high": [14000, 15000], "low": [13000, 14000]},
        index=pd.to_datetime(["2017-12-28T20:00:00+00:00", "2017-12-29T00:00:00+00:00"], utc=True),
    )
    ws = types.SimpleNamespace(df=df, picks={}, active_kind="low")
    tool._preload_fib_picks(ws, ann)
    assert ws.picks["high"][1] == 14940.0  # higher price -> high pick
    assert ws.picks["low"][1] == 13611.0  # lower price -> low pick
    assert ws.picks["high"][0] == 1 and ws.picks["low"][0] == 0  # nearest bar by time


def test_single_fib_mode_suppresses_htf_overlays(monkeypatch):
    monkeypatch.setattr(
        tool.LabelWorkspace,
        "_load_chart_candles",
        lambda self: pd.DataFrame({"high": [1.0], "low": [1.0]}),
    )
    monkeypatch.setattr(tool, "load_htf_overlays", lambda *a, **k: ["overlay"])
    settings = load_settings()

    decluttered = tool.LabelWorkspace(settings, ["BTC/USD"], ["4h"], single_fib_mode=True)
    normal = tool.LabelWorkspace(load_settings(), ["BTC/USD"], ["4h"])

    assert decluttered.get_htf_overlays() == []  # clutter hidden
    assert normal.get_htf_overlays() == ["overlay"]  # default unchanged


def test_edit_fib_id_arg_parses_and_defaults_none(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["tool"])
    assert tool._parse_args().edit_fib_id is None
    monkeypatch.setattr(sys, "argv", ["tool", "--edit-fib-id", "fib_X"])
    assert tool._parse_args().edit_fib_id == "fib_X"
