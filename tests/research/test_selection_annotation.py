"""Round-trip + validation tests for the contrastive selection-annotation schema (Issue #42 v0)."""

from __future__ import annotations

import pytest

from fibengine.core.config import REPO_ROOT
from fibengine.research.selection_annotation import (
    Anchor,
    AnnotationWindow,
    Candidate,
    dump_window,
    load_window,
    window_from_dict,
    window_to_dict,
)

FIXTURE = (
    REPO_ROOT / "data/labels/selection_annotations/bitfinex/BTC-USD/1d/window_20200330_fixture.yaml"
)


def _cand(cid: str, pa: float, pb: float, direction: str, label: str, tags=()) -> Candidate:
    return Candidate(
        id=cid,
        anchor_a=Anchor("2020-03-30T00:00:00+00:00", pa),
        anchor_b=Anchor("2020-04-08T00:00:00+00:00", pb),
        direction=direction,
        label=label,
        reason="x",
        tags=tuple(tags),
    )


def _window(*cands: Candidate, created_by: str = "fixture") -> AnnotationWindow:
    return AnnotationWindow(
        symbol="BTC/USD",
        timeframe="1d",
        exchange="bitfinex",
        window_start="2020-02-01",
        window_end="2020-04-30",
        regime_label="r",
        structure_label="daily_wick_pair",
        created_by=created_by,
        candidates=cands,
    )


def test_fixture_loads_and_shapes():
    w = load_window(FIXTURE)
    assert w.created_by == "fixture"
    assert not w.is_human
    assert len(w.candidates) == 4
    assert w.accepted_ids == ["c1"]


def test_dict_round_trip(tmp_path):
    w = _window(
        _cand("c1", 5880.9, 7420.0, "up", "accepted"),
        _cand("c2", 10500.0, 3850.0, "down", "rejected", ["wrong_scale"]),
    )
    assert window_from_dict(window_to_dict(w)) == w
    p = tmp_path / "w.yaml"
    dump_window(w, p)
    assert load_window(p) == w


def test_direction_must_match_price_ordering():
    with pytest.raises(ValueError, match="disagrees with price"):
        _cand("c1", 5880.9, 7420.0, "down", "accepted")  # up prices, down label


def test_degenerate_candidate_rejected():
    with pytest.raises(ValueError, match="degenerate"):
        _cand("c1", 7000.0, 7000.0, "up", "accepted")


def test_bad_label_and_tag_rejected():
    with pytest.raises(ValueError, match="label must be"):
        _cand("c1", 5880.9, 7420.0, "up", "maybe")
    with pytest.raises(ValueError, match="unknown tags"):
        _cand("c1", 5880.9, 7420.0, "up", "rejected", ["not_a_tag"])


def test_bad_price_rejected():
    with pytest.raises(ValueError, match="price must be"):
        Anchor("2020-01-01T00:00:00+00:00", 0.0)


def test_window_validation():
    with pytest.raises(ValueError, match="no candidates"):
        _window()
    with pytest.raises(ValueError, match="duplicate candidate ids"):
        _window(
            _cand("c1", 5880.9, 7420.0, "up", "accepted"),
            _cand("c1", 6000.0, 7000.0, "up", "rejected"),
        )
    with pytest.raises(ValueError, match="created_by must be"):
        _window(_cand("c1", 5880.9, 7420.0, "up", "accepted"), created_by="robot")
