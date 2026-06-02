"""Tests for the human-fib behavior-candidate layer (emit-only, research)."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from fibengine.core.fib import fib_levels
from fibengine.labeling import store
from fibengine.labeling.human_fib import DEFAULT_FIB_RATIOS, FibAnchor, make_annotation
from fibengine.labeling.human_fib_events import (
    LevelEventConfig,
    detect_candidates,
    events_path,
    save_events,
    swing_from_annotation,
)

# bars 0..10: close 100 -> 120 (low@0, high@10); with high=close+0.5/low=close-0.5
# the 0.5 fib level sits at 110.0 (same fixture idea as test_level_events.py).
RISE = [100 + i * 2 for i in range(11)]


@pytest.fixture
def labels_tmp(tmp_path):
    store.set_labels_dir(tmp_path)
    yield tmp_path
    store.set_labels_dir(None)


def _df(closes: list[float]) -> pd.DataFrame:
    arr = np.array(closes, dtype=float)
    n = len(arr)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {"open": arr, "high": arr + 0.5, "low": arr - 0.5, "close": arr, "volume": np.ones(n)},
        index=idx,
    )


def _up_annotation(df: pd.DataFrame):
    # anchor_a (ratio 1.0) = low@0, anchor_b (ratio 0.0) = high@10 -> direction "up".
    a = FibAnchor(df.index[0].isoformat(), float(df["low"].iloc[0]))
    b = FibAnchor(df.index[10].isoformat(), float(df["high"].iloc[10]))
    return make_annotation(symbol="BTC/USD", timeframe="1h", anchor_a=a, anchor_b=b)


def _stream_for_half(closes: list[float]):
    df = _df(closes)
    ann = _up_annotation(df)
    streams = detect_candidates(df, ann, LevelEventConfig(levels=[0.5]))
    assert len(streams) == 1
    stream = streams[0]
    assert stream.level == "0.5"
    assert stream.price == 110.0
    return stream


def test_swing_reproduces_human_levels():
    df = _df(RISE)
    ann = _up_annotation(df)
    assert ann.direction == "up"
    swing = swing_from_annotation(df, ann)
    derived = fib_levels(swing, list(DEFAULT_FIB_RATIOS))
    for lvl in ann.levels:
        assert derived[lvl.ratio] == pytest.approx(lvl.price)


def test_raises_on_reversed_anchor_time_order():
    df = _df(RISE)
    # Invalid annotation order: anchor_a is later than anchor_b.
    a = FibAnchor(df.index[10].isoformat(), float(df["high"].iloc[10]))
    b = FibAnchor(df.index[0].isoformat(), float(df["low"].iloc[0]))
    ann = make_annotation(symbol="BTC/USD", timeframe="1h", anchor_a=a, anchor_b=b)
    with pytest.raises(ValueError, match="anchors must be chronological"):
        swing_from_annotation(df, ann)


def test_continuation_break_through_level():
    stream = _stream_for_half(RISE + [118, 116, 114, 112, 110, 108, 106])
    assert len(stream.events) == 1
    event = stream.events[0]
    assert event.auto_candidate == "continuation_candidate"
    assert event.approach_side == "above"


def test_rejection_touch_and_bounce_away():
    stream = _stream_for_half(RISE + [114, 112, 110.6, 113, 116, 118])
    assert len(stream.events) == 1
    assert stream.events[0].auto_candidate == "rejection_candidate"


def test_failure_accepted_below_then_reverses():
    stream = _stream_for_half(RISE + [114, 112, 110, 109, 108, 111, 113])
    assert len(stream.events) == 1
    assert stream.events[0].auto_candidate == "failure_candidate"


def test_no_events_when_level_never_touched():
    stream = _stream_for_half(RISE + [119, 119, 118, 119, 120, 119])
    assert stream.events == []


def test_events_only_after_leg_end():
    # anchor_b sits at bar 10; every event must occur strictly after it.
    stream = _stream_for_half(RISE + [118, 116, 114, 112, 110, 108, 106])
    assert all(event.bar_index > 10 for event in stream.events)


def test_candidates_are_candidates_not_facts():
    stream = _stream_for_half(RISE + [118, 116, 114, 112, 110, 108, 106])
    assert all(event.auto_candidate.endswith("_candidate") for event in stream.events)


def test_full_ratio_set_emits_one_stream_per_level():
    df = _df(RISE + [118, 116, 114, 112, 110, 108, 106])
    ann = _up_annotation(df)
    streams = detect_candidates(df, ann)
    assert [s.level for s in streams] == [f"{r:g}" for r in DEFAULT_FIB_RATIOS]


def test_save_and_reload_events(labels_tmp):
    df = _df(RISE + [118, 116, 114, 112, 110, 108, 106])
    ann = _up_annotation(df)
    cfg = LevelEventConfig(levels=[0.5])
    streams = detect_candidates(df, ann, cfg)
    path = save_events(ann, streams, cfg)
    assert path == events_path(ann)
    assert path.is_relative_to(labels_tmp)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["fib_id"] == ann.fib_id
    assert payload["source"] == "human_fib_events"
    assert payload["direction"] == "up"
    assert payload["n_events"] == sum(len(s.events) for s in streams)
    assert payload["levels"][0]["level"] == "0.5"
    assert payload["config"]["forward_window"] == cfg.forward_window
