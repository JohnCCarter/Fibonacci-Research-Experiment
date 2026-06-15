"""Tests for overlap_detector — report-only overlap/near-duplicate candidates, stdlib."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from fibengine.research.overlap_detector import (
    FibBox,
    box_iou,
    find_overlap_candidates,
    load_boxes,
    write_candidates_csv,
)


def _write_fib(
    fib_dir: Path,
    *,
    sid: str,
    a_time: str,
    a_price: float,
    b_time: str,
    b_price: float,
    timeframe: str = "4h",
) -> Path:
    fib_dir.mkdir(parents=True, exist_ok=True)
    fid = f"fib_BTC-USD_{timeframe}_{sid}"
    path = fib_dir / f"{fid}.json"
    path.write_text(
        json.dumps(
            {
                "fib_id": fid,
                "symbol": "BTC/USD",
                "timeframe": timeframe,
                "anchor_a": {"time": a_time, "price": a_price},
                "anchor_b": {"time": b_time, "price": b_price},
                "direction": "down" if b_price < a_price else "up",
            }
        ),
        encoding="utf-8",
    )
    return path


def _box(sid: str, t_lo: float, t_hi: float, p_lo: float, p_hi: float) -> FibBox:
    return FibBox(
        fib_id=sid,
        timeframe="4h",
        t_lo=t_lo,
        t_hi=t_hi,
        p_lo=math.log(p_lo),
        p_hi=math.log(p_hi),
        a_epoch=t_lo,
        a_price=p_lo,
        b_epoch=t_hi,
        b_price=p_hi,
    )


def test_time_overlap_full_when_identical_boxes():
    a = _box("a", 0, 100, 100, 200)
    b = _box("b", 0, 100, 100, 200)
    assert box_iou(a, b) == pytest.approx(1.0)


def test_no_overlap_when_time_disjoint():
    a = _box("a", 0, 100, 100, 200)
    b = _box("b", 200, 300, 100, 200)  # same price band, disjoint in time
    assert box_iou(a, b) == 0.0


def test_no_overlap_when_price_disjoint():
    a = _box("a", 0, 100, 100, 200)
    b = _box("b", 0, 100, 1000, 2000)  # same time, disjoint in price
    assert box_iou(a, b) == 0.0


def test_partial_overlap_between_zero_and_one():
    a = _box("a", 0, 100, 100, 200)
    b = _box("b", 50, 150, 100, 200)  # half time overlap, full price overlap
    iou = box_iou(a, b)
    assert 0.0 < iou < 1.0


def test_shared_anchor_b_is_flagged_even_at_low_iou(tmp_path):
    # Two distinct sub-legs sharing anchor_b (the real 20210110 pattern).
    _write_fib(
        tmp_path,
        sid="20210110T080000",
        a_time="2021-01-10T08:00:00+00:00",
        a_price=41066.0,
        b_time="2021-01-11T16:00:00+00:00",
        b_price=30635.0,
    )
    _write_fib(
        tmp_path,
        sid="20210110T200000",
        a_time="2021-01-10T20:00:00+00:00",
        a_price=38998.0,
        b_time="2021-01-11T16:00:00+00:00",
        b_price=30635.0,
    )
    boxes = load_boxes(tmp_path, require_timeframe="4h")
    cands = find_overlap_candidates(boxes, min_box_iou=0.99)  # IoU alone would not flag
    assert len(cands) == 1
    assert cands[0].shared_anchor == "anchor_b"


def test_detector_reports_without_changing_labels(tmp_path):
    p1 = _write_fib(
        tmp_path,
        sid="a",
        a_time="2021-01-01T00:00:00+00:00",
        a_price=100,
        b_time="2021-01-02T00:00:00+00:00",
        b_price=200,
    )
    before = p1.read_bytes()
    boxes = load_boxes(tmp_path, require_timeframe="4h")
    find_overlap_candidates(boxes)
    assert p1.read_bytes() == before  # source JSON untouched


def test_empty_dir_fails_clearly(tmp_path):
    d = tmp_path / "empty"
    d.mkdir()
    with pytest.raises(FileNotFoundError, match="No fib_.*json"):
        load_boxes(d)


def test_timeframe_guard_fails_closed(tmp_path):
    _write_fib(
        tmp_path,
        sid="x",
        a_time="2021-01-01T00:00:00+00:00",
        a_price=100,
        b_time="2021-01-02T00:00:00+00:00",
        b_price=200,
        timeframe="1d",
    )
    with pytest.raises(ValueError, match="timeframe"):
        load_boxes(tmp_path, require_timeframe="4h")


def test_csv_roundtrip_columns(tmp_path):
    boxes = [
        _box("a", 0, 100, 100, 200),
        _box("b", 0, 100, 100, 200),
    ]
    cands = find_overlap_candidates(boxes, min_box_iou=0.5)
    out = write_candidates_csv(tmp_path / "rep.csv", cands)
    text = out.read_text(encoding="utf-8")
    assert text.splitlines()[0] == "fib_a,fib_b,time_iou,price_iou,box_iou,shared_anchor"
    assert "a,b" in text or "b,a" in text
