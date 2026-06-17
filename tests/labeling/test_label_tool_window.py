"""Tests for window-slicing, _resolve_window, and HTF overlay cache (A1/B1)."""

from argparse import Namespace

import pandas as pd
import pytest

from fibengine.core.config import Settings
from fibengine.labeling import tool
from fibengine.labeling.tool import LabelWorkspace, _resolve_window

# ---------------------------------------------------------------------------
# _resolve_window
# ---------------------------------------------------------------------------


def test_resolve_window_no_args_returns_none():
    ns = Namespace(window_start=None, window_end=None, label_year=None, buffer_months=3)
    start, end = _resolve_window(ns)
    assert start is None
    assert end is None


def test_resolve_window_explicit_start_end():
    ns = Namespace(
        window_start="2019-01-01", window_end="2019-12-31", label_year=None, buffer_months=3
    )
    start, end = _resolve_window(ns)
    assert start == pd.Timestamp("2019-01-01", tz="UTC")
    assert end == pd.Timestamp("2019-12-31", tz="UTC")


def test_resolve_window_label_year_default_buffer():
    # 2019-01-01 - 3 months = 2018-10-01; 2020-01-01 + 3 months = 2020-04-01
    ns = Namespace(window_start=None, window_end=None, label_year=2019, buffer_months=3)
    start, end = _resolve_window(ns)
    assert start == pd.Timestamp("2018-10-01", tz="UTC")
    assert end == pd.Timestamp("2020-04-01", tz="UTC")


def test_resolve_window_label_year_custom_buffer():
    ns = Namespace(window_start=None, window_end=None, label_year=2019, buffer_months=6)
    start, end = _resolve_window(ns)
    assert start == pd.Timestamp("2018-07-01", tz="UTC")
    assert end == pd.Timestamp("2020-07-01", tz="UTC")


def test_resolve_window_conflict_raises_systemexit():
    ns = Namespace(window_start="2019-01-01", window_end=None, label_year=2019, buffer_months=3)
    with pytest.raises(SystemExit):
        _resolve_window(ns)


def test_resolve_window_only_start():
    ns = Namespace(window_start="2020-06-01", window_end=None, label_year=None, buffer_months=3)
    start, end = _resolve_window(ns)
    assert start == pd.Timestamp("2020-06-01", tz="UTC")
    assert end is None


# ---------------------------------------------------------------------------
# LabelWorkspace window-slicing
# synthetic_df: 61 bars from 2024-01-01 00:00 UTC, freq=1h
# bar 24 = 2024-01-02 00:00 UTC
# ---------------------------------------------------------------------------


def test_workspace_no_window_returns_full_df(monkeypatch, synthetic_df):
    monkeypatch.setattr(tool, "load_candles", lambda _cfg, fetch_if_missing=True: synthetic_df)
    monkeypatch.setattr(tool, "find_label", lambda *_: None)
    ws = LabelWorkspace(settings=Settings(), symbols=["BTC/USD"], timeframes=["1h"])
    assert len(ws.df) == len(synthetic_df)


def test_workspace_window_start_slices_df(monkeypatch, synthetic_df):
    # bar 24 = 2024-01-02 00:00; bars 24-60 = 37 bars
    monkeypatch.setattr(tool, "load_candles", lambda _cfg, fetch_if_missing=True: synthetic_df)
    monkeypatch.setattr(tool, "find_label", lambda *_: None)
    ws = LabelWorkspace(
        settings=Settings(),
        symbols=["BTC/USD"],
        timeframes=["1h"],
        window_start=pd.Timestamp("2024-01-02", tz="UTC"),
    )
    assert ws.df.index[0] == pd.Timestamp("2024-01-02", tz="UTC")
    assert len(ws.df) == 37


def test_workspace_window_end_slices_df(monkeypatch, synthetic_df):
    # bars 0-23 = 24 bars (00:00 to 23:00 on 2024-01-01)
    monkeypatch.setattr(tool, "load_candles", lambda _cfg, fetch_if_missing=True: synthetic_df)
    monkeypatch.setattr(tool, "find_label", lambda *_: None)
    ws = LabelWorkspace(
        settings=Settings(),
        symbols=["BTC/USD"],
        timeframes=["1h"],
        window_end=pd.Timestamp("2024-01-01 23:00", tz="UTC"),
    )
    assert ws.df.index[-1] == pd.Timestamp("2024-01-01 23:00", tz="UTC")
    assert len(ws.df) == 24


def test_workspace_window_outside_range_raises(monkeypatch, synthetic_df):
    monkeypatch.setattr(tool, "load_candles", lambda _cfg, fetch_if_missing=True: synthetic_df)
    monkeypatch.setattr(tool, "find_label", lambda *_: None)
    with pytest.raises(SystemExit):
        LabelWorkspace(
            settings=Settings(),
            symbols=["BTC/USD"],
            timeframes=["1h"],
            window_start=pd.Timestamp("2025-01-01", tz="UTC"),
        )


def test_workspace_set_market_applies_window(monkeypatch, synthetic_df):
    monkeypatch.setattr(tool, "load_candles", lambda _cfg, fetch_if_missing=True: synthetic_df)
    monkeypatch.setattr(tool, "find_label", lambda *_: None)
    ws = LabelWorkspace(
        settings=Settings(),
        symbols=["BTC/USD", "ETH/USD"],
        timeframes=["1h"],
        window_end=pd.Timestamp("2024-01-01 23:00", tz="UTC"),
    )
    assert len(ws.df) == 24
    ws.cycle_symbol(1)
    assert len(ws.df) == 24


# ---------------------------------------------------------------------------
# HTF overlay cache (A1)
# ---------------------------------------------------------------------------


def test_htf_overlays_cached_across_redraws(monkeypatch, synthetic_df):
    call_count = [0]

    def counting_load_htf(*_args):
        call_count[0] += 1
        return []

    monkeypatch.setattr(tool, "load_candles", lambda _cfg, fetch_if_missing=True: synthetic_df)
    monkeypatch.setattr(tool, "find_label", lambda *_: None)
    monkeypatch.setattr(tool, "load_htf_overlays", counting_load_htf)
    ws = LabelWorkspace(settings=Settings(), symbols=["BTC/USD"], timeframes=["1h"])
    ws.get_htf_overlays()
    ws.get_htf_overlays()
    ws.get_htf_overlays()
    assert call_count[0] == 1


def test_htf_overlays_invalidated_on_market_switch(monkeypatch, synthetic_df):
    call_count = [0]

    def counting_load_htf(*_args):
        call_count[0] += 1
        return []

    monkeypatch.setattr(tool, "load_candles", lambda _cfg, fetch_if_missing=True: synthetic_df)
    monkeypatch.setattr(tool, "find_label", lambda *_: None)
    monkeypatch.setattr(tool, "load_htf_overlays", counting_load_htf)
    ws = LabelWorkspace(settings=Settings(), symbols=["BTC/USD", "ETH/USD"], timeframes=["1h"])
    ws.get_htf_overlays()  # first load
    ws.cycle_symbol(1)  # set_market → _htf_overlays = None
    ws.get_htf_overlays()  # second load
    assert call_count[0] == 2
