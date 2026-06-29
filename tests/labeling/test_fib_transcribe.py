"""Tests for the screenshot fib transcription helper (candidate output, no auto-fib)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from fibengine.labeling.fib_transcribe import (
    AnchorMatch,
    _refuse_facit_path,
    candidate_dict,
    match_anchor_time,
    transcribe_fib,
)


def _df() -> pd.DataFrame:
    """5 daily candles. Low 103310 repeats on day1 (before) and day3 (after) the day2 high."""
    idx = pd.date_range("2026-01-01", periods=5, freq="1D", tz="UTC")
    return pd.DataFrame(
        {
            "open": [95.0, 108.0, 121000.0, 124000.0, 121000.0],
            "high": [100.0, 110.0, 126110.0, 124000.0, 122000.0],
            "low": [90.0, 103310.0, 120000.0, 103310.0, 118000.0],
            "close": [99.0, 109.0, 122000.0, 120000.0, 119000.0],
            "volume": [1.0] * 5,
        },
        index=idx,
    )


# --- match_anchor_time -------------------------------------------------------


def test_exact_match_recovers_time():
    m = match_anchor_time(_df(), 126110.0, "high")
    assert m.confidence == "exact"
    assert m.time.startswith("2026-01-03")
    assert m.rel_delta == 0.0


def test_near_match_is_graded_near():
    # 103350 vs candle low 103310 -> rel ~3.9e-4, between exact (2e-4) and near (1e-3)
    m = match_anchor_time(_df(), 103350.0, "low")
    assert m.confidence == "near"
    assert 2e-4 < m.rel_delta <= 1e-3


def test_far_price_is_flagged():
    m = match_anchor_time(_df(), 500000.0, "high")
    assert m.confidence == "flag"


def test_after_disambiguates_repeated_price():
    # Without `after`, idxmin picks the first (day1). With after=day2, only day3 qualifies.
    naive = match_anchor_time(_df(), 103310.0, "low")
    assert naive.time.startswith("2026-01-02")
    later = match_anchor_time(_df(), 103310.0, "low", after="2026-01-03T00:00:00+00:00")
    assert later.time.startswith("2026-01-04")
    assert later.confidence == "exact"


def test_after_past_end_yields_flag():
    m = match_anchor_time(_df(), 103310.0, "low", after="2026-01-31T00:00:00+00:00")
    assert m.time is None
    assert m.confidence == "flag"


def test_role_validated():
    with pytest.raises(ValueError):
        match_anchor_time(_df(), 100.0, "close")


def test_n_within_near_counts_ambiguity():
    m = match_anchor_time(_df(), 103310.0, "low")
    assert m.n_within_near == 2  # day1 and day3 both sit on 103310


# --- transcribe_fib ----------------------------------------------------------


def test_down_fib_maps_anchors_and_recovers_times():
    res = transcribe_fib(
        _df(),
        high_price=126110.0,
        low_price=103310.0,
        direction="down",
        symbol="BTC/USD",
        timeframe="1d",
    )
    ann = res.annotation
    assert ann is not None
    assert ann.direction == "down"
    # anchor_a = swing origin (the high, earlier), anchor_b = recent extreme (the low, later)
    assert ann.anchor_a.price == 126110.0
    assert ann.anchor_a.time.startswith("2026-01-03")
    assert ann.anchor_b.price == 103310.0
    assert ann.anchor_b.time.startswith("2026-01-04")  # day3, not the earlier day1
    assert res.confidence == "exact"
    assert ann.created_by == "vision_poc"
    assert ann.source == "screenshot_vision_extraction"
    assert ann.scale_mode == "log"


def test_up_fib_maps_origin_to_low():
    res = transcribe_fib(
        _df(),
        high_price=126110.0,
        low_price=90.0,
        direction="up",
        symbol="BTC/USD",
        timeframe="1d",
    )
    ann = res.annotation
    assert ann is not None
    assert ann.direction == "up"
    assert ann.anchor_a.price == 90.0  # origin = low (earlier)
    assert ann.anchor_a.time.startswith("2026-01-01")
    assert ann.anchor_b.price == 126110.0
    assert ann.anchor_b.time.startswith("2026-01-03")


def test_human_price_kept_verbatim_on_near_match():
    # The annotation keeps the human's price; only the time is recovered from the candle.
    res = transcribe_fib(
        _df(),
        high_price=126110.0,
        low_price=103350.0,  # near, not exact
        direction="down",
        symbol="BTC/USD",
        timeframe="1d",
    )
    assert res.annotation.anchor_b.price == 103350.0  # verbatim, not snapped to 103310
    assert res.confidence == "near"


def test_unrecoverable_extreme_yields_no_annotation():
    one = _df().iloc[2:3]  # only the day2 high candle
    res = transcribe_fib(
        one,
        high_price=126110.0,
        low_price=120000.0,
        direction="down",
        symbol="BTC/USD",
        timeframe="1d",
    )
    assert res.annotation is None  # no candle after the origin -> low time unrecoverable
    assert res.confidence == "flag"


def test_inverted_prices_rejected():
    with pytest.raises(ValueError):
        transcribe_fib(
            _df(),
            high_price=100.0,
            low_price=200.0,
            direction="down",
            symbol="BTC/USD",
            timeframe="1d",
        )


def test_bad_direction_rejected():
    with pytest.raises(ValueError):
        transcribe_fib(
            _df(),
            high_price=126110.0,
            low_price=103310.0,
            direction="sideways",
            symbol="BTC/USD",
            timeframe="1d",
        )


# --- candidate serialization + facit guard -----------------------------------


def test_candidate_dict_marks_candidate_and_keeps_facit_shape():
    res = transcribe_fib(
        _df(),
        high_price=126110.0,
        low_price=103310.0,
        direction="down",
        symbol="BTC/USD",
        timeframe="1d",
    )
    d = candidate_dict(res)
    assert d["_candidate"] is True
    assert d["_transcription"]["confidence"] == "exact"
    assert len(d["_transcription"]["matches"]) == 2
    # facit-shaped core is still present
    assert d["anchor_a"]["price"] == 126110.0
    assert d["direction"] == "down"
    assert "levels" in d


def test_candidate_dict_empty_when_no_annotation():
    res = transcribe_fib(
        _df().iloc[2:3],
        high_price=126110.0,
        low_price=120000.0,
        direction="down",
        symbol="BTC/USD",
        timeframe="1d",
    )
    d = candidate_dict(res)
    assert d["_candidate"] is True
    assert "anchor_a" not in d  # no facit core when annotation could not be built


def test_refuse_facit_path_blocks_human_fib():
    with pytest.raises(SystemExit):
        _refuse_facit_path(Path("data/labels/human_fib/bitfinex/BTC-USD/1d/fib_x.json"))


def test_refuse_facit_path_allows_other_paths(tmp_path):
    _refuse_facit_path(tmp_path / "cand.json")  # does not raise


def test_anchor_match_dataclass_fields():
    m = AnchorMatch(1.0, "high", None, None, None, "flag", 0)
    assert m.role == "high" and m.confidence == "flag"
