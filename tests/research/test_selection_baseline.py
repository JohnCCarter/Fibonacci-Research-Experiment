"""Baseline scorer, selection metrics, and leakage-safe window split (Issue #42 v0)."""

from __future__ import annotations

import math

import pytest

from fibengine.research.selection_annotation import Anchor, AnnotationWindow, Candidate
from fibengine.research.selection_baseline import (
    candidate_magnitude,
    evaluate,
    rank_candidates,
    reject_precision,
    split_by_window,
    top1_match,
    top3_coverage,
)


def _cand(cid: str, pa: float, pb: float, direction: str, label: str) -> Candidate:
    return Candidate(
        id=cid,
        anchor_a=Anchor("2020-03-30T00:00:00+00:00", pa),
        anchor_b=Anchor("2020-04-08T00:00:00+00:00", pb),
        direction=direction,
        label=label,
    )


def _window(*cands: Candidate, created_by: str = "human") -> AnnotationWindow:
    return AnnotationWindow(
        symbol="BTC/USD",
        timeframe="1d",
        exchange="bitfinex",
        window_start="2020-02-01",
        window_end="2020-04-30",
        regime_label="r",
        structure_label="s",
        created_by=created_by,
        candidates=cands,
    )


def test_magnitude_and_ranking():
    small = _cand("small", 6000.0, 7000.0, "up", "accepted")  # smaller log span
    big = _cand("big", 10500.0, 3850.0, "down", "rejected")  # larger log span
    assert candidate_magnitude(big) > candidate_magnitude(small)
    w = _window(small, big)
    assert rank_candidates(w) == ["big", "small"]  # magnitude prior ranks big first


def test_top1_and_top3():
    # accepted is the largest -> top1 true
    w = _window(
        _cand("a", 3000.0, 9000.0, "up", "accepted"),
        _cand("b", 6000.0, 7000.0, "up", "rejected"),
    )
    assert top1_match(w) is True
    assert top3_coverage(w) is True
    # accepted is smallest, with 3 bigger rejecteds -> not in top3
    w2 = _window(
        _cand("acc", 6900.0, 7000.0, "up", "accepted"),
        _cand("r1", 2000.0, 9000.0, "up", "rejected"),
        _cand("r2", 2500.0, 9500.0, "up", "rejected"),
        _cand("r3", 3000.0, 9900.0, "up", "rejected"),
    )
    assert top1_match(w2) is False
    assert top3_coverage(w2) is False


def test_reject_precision_and_nan():
    w = _window(
        _cand("acc", 3000.0, 9000.0, "up", "accepted"),  # large -> above rejecteds
        _cand("r1", 6000.0, 7000.0, "up", "rejected"),
        _cand("r2", 6500.0, 7000.0, "up", "rejected"),
    )
    assert reject_precision(w) == 1.0
    # no rejected -> nan
    assert math.isnan(reject_precision(_window(_cand("a", 3000.0, 9000.0, "up", "accepted"))))


def test_evaluate_pooled():
    w = _window(
        _cand("a", 3000.0, 9000.0, "up", "accepted"), _cand("b", 6000.0, 7000.0, "up", "rejected")
    )
    res = evaluate([w])
    assert res["n"] == 1.0
    assert res["top1"] == 1.0
    assert res["reject_precision"] == 1.0
    empty = evaluate([_window(_cand("x", 6000.0, 7000.0, "up", "rejected"))])
    assert empty["n"] == 0


def test_split_is_by_window_not_row():
    ws = [
        _window(
            _cand(f"c{i}", 3000.0, 9000.0, "up", "accepted"),
            _cand(f"r{i}", 6000.0, 7000.0, "up", "rejected"),
        )
        for i in range(10)
    ]
    train, val = split_by_window(ws, train_frac=0.7, seed=1)
    assert len(train) == 7 and len(val) == 3
    # every window lands wholly on one side (identity-preserved, no row straddling)
    assert set(map(id, train)).isdisjoint(set(map(id, val)))
    assert set(map(id, train)) | set(map(id, val)) == set(map(id, ws))
    # deterministic
    assert [id(w) for w in split_by_window(ws, seed=1)[0]] == [id(w) for w in train]


def test_split_rejects_bad_frac():
    with pytest.raises(ValueError, match="train_frac"):
        split_by_window([], train_frac=1.5)
