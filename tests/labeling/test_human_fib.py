"""Tests for the Human Fib Annotation Layer (manual ground truth, no auto-fib)."""

from __future__ import annotations

import pandas as pd
import pytest

from fibengine.labeling import human_fib, store
from fibengine.labeling.human_fib import (
    DEFAULT_FIB_RATIOS,
    RELATIONS,
    FibAnchor,
    anchors_from_picks,
    classify_candle,
    classify_candles,
    compute_levels,
    infer_direction,
    load_annotation,
    make_annotation,
    save_annotation,
)


@pytest.fixture
def labels_tmp(tmp_path):
    store.set_labels_dir(tmp_path)
    yield tmp_path
    store.set_labels_dir(None)


def _ohlc(n: int) -> pd.DataFrame:
    idx = pd.date_range("2026-01-01", periods=n, freq="1D", tz="UTC")
    return pd.DataFrame(
        {
            "open": [100.0] * n,
            "high": [105.0] * n,
            "low": [95.0] * n,
            "close": [101.0] * n,
            "volume": [1.0] * n,
        },
        index=idx,
    )


# 1. Fib levels are calculated correctly from anchors.
def test_levels_match_spec_example():
    a = FibAnchor(time="2026-01-14T00:00:00Z", price=97924.0)
    b = FibAnchor(time="2026-02-06T00:00:00Z", price=60000.0)
    levels = {lvl.ratio: lvl.price for lvl in compute_levels(a, b)}
    assert levels[1.0] == pytest.approx(97924.0)
    assert levels[0.5] == pytest.approx(78962.0)
    assert levels[0.236] == pytest.approx(68950.064)
    assert levels[0.382] == pytest.approx(74486.968)
    assert levels[0.618] == pytest.approx(83437.032)
    assert levels[0.786] == pytest.approx(89808.264)
    assert tuple(lvl.ratio for lvl in compute_levels(a, b)) == DEFAULT_FIB_RATIOS


def test_levels_are_rounded_no_float_noise():
    a = FibAnchor("2015-11-04T00:00:00Z", 504.0)
    b = FibAnchor("2015-11-11T00:00:00Z", 300.28)
    levels = {lvl.ratio: lvl.price for lvl in compute_levels(a, b)}
    # 0.618 would be 426.17895999999996 without rounding.
    assert levels[0.618] == 426.17896
    assert all(round(price, 8) == price for price in levels.values())


def test_direction_inference():
    high = FibAnchor("2026-01-01T00:00:00Z", 100.0)
    low = FibAnchor("2026-02-01T00:00:00Z", 60.0)
    assert infer_direction(high, low) == "down"
    assert infer_direction(low, high) == "up"


# 2. above / below / touch / cross classification works.
@pytest.mark.parametrize(
    ("open_", "high", "low", "close", "expected"),
    [
        (92.0, 95.0, 90.0, 93.0, "below"),  # whole candle below
        (108.0, 110.0, 106.0, 109.0, "above"),  # whole candle above
        (104.0, 105.0, 95.0, 103.0, "touch"),  # level inside range, same side
        (98.0, 105.0, 95.0, 102.0, "cross"),  # open<level<close
        (102.0, 105.0, 95.0, 98.0, "cross"),  # open>level>close
        (100.0, 105.0, 95.0, 102.0, "touch"),  # open exactly on level -> not a strict cross
        (98.0, 100.0, 95.0, 97.0, "touch"),  # level == high boundary
    ],
)
def test_classify_candle(open_, high, low, close, expected):
    assert classify_candle(open_, high, low, close, level=100.0) == expected


def test_classify_candles_one_row_per_candle_and_level():
    a = FibAnchor("2026-01-01T00:00:00Z", 110.0)
    b = FibAnchor("2026-01-05T00:00:00Z", 90.0)
    annotation = make_annotation(symbol="BTC/USD", timeframe="1d", anchor_a=a, anchor_b=b)
    df = _ohlc(3)
    rows = classify_candles(df, annotation)
    assert len(rows) == 3 * len(annotation.levels)
    assert all(r["relation"] in RELATIONS for r in rows)
    assert {r["ratio"] for r in rows} == set(DEFAULT_FIB_RATIOS)


# 3. Saved annotations reload correctly.
def test_save_and_reload(labels_tmp):
    a = FibAnchor("2026-01-14T00:00:00Z", 97924.0)
    b = FibAnchor("2026-02-06T00:00:00Z", 60000.0)
    ann = make_annotation(
        symbol="BTC/USD", timeframe="1d", exchange="bitfinex", anchor_a=a, anchor_b=b
    )
    path = save_annotation(ann)
    assert path.exists()
    assert path.is_relative_to(labels_tmp)

    reloaded = load_annotation(path)
    assert reloaded.fib_id == ann.fib_id
    assert reloaded.direction == "down"
    assert reloaded.created_by == "human"
    assert reloaded.source == "manual_labeling_tool"
    assert reloaded.anchor_a.price == pytest.approx(97924.0)
    assert reloaded.anchor_b.price == pytest.approx(60000.0)
    assert [lvl.ratio for lvl in reloaded.levels] == list(DEFAULT_FIB_RATIOS)
    assert reloaded.levels[2].price == pytest.approx(78962.0)


# 4. No auto-fib detection is introduced.
def test_no_autofib_api():
    suspicious = [
        name
        for name in dir(human_fib)
        if not name.startswith("_") and ("detect" in name.lower() or "auto" in name.lower())
    ]
    assert suspicious == []


def test_make_annotation_requires_explicit_anchors():
    with pytest.raises(TypeError):
        make_annotation(symbol="BTC/USD", timeframe="1d")  # type: ignore[call-arg]


def test_anchors_from_picks_orders_by_time():
    df = _ohlc(10)
    # high earlier than low -> anchor_a is the high (down move)
    a, b = anchors_from_picks(df, high_idx=2, high_price=120.0, low_idx=7, low_price=80.0)
    assert a.price == 120.0
    assert b.price == 80.0
    assert infer_direction(a, b) == "down"

    # low earlier than high -> anchor_a is the low (up move)
    a2, b2 = anchors_from_picks(df, high_idx=8, high_price=120.0, low_idx=1, low_price=80.0)
    assert a2.price == 80.0
    assert b2.price == 120.0
    assert infer_direction(a2, b2) == "up"
