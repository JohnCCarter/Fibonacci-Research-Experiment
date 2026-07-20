"""Tests for the GUI-free selection-capture helpers (Issue #42 contrastive capture)."""

from __future__ import annotations

import pytest

from fibengine.labeling.selection_capture import (
    build_window,
    default_window_path,
    direction_from_anchors,
    make_candidate,
    next_candidate_id,
    save_window,
    time_ordered,
)
from fibengine.research.selection_annotation import Anchor, Candidate, load_window

HI = Anchor("2020-02-13T00:00:00+00:00", 10500.0)
LO = Anchor("2020-03-13T00:00:00+00:00", 3850.0)
FRESH_LOW = Anchor("2020-03-30T00:00:00+00:00", 5880.9)
IMPULSE_HIGH = Anchor("2020-04-08T00:00:00+00:00", 7420.0)


def test_direction_from_anchors_up_and_down():
    assert direction_from_anchors(FRESH_LOW, IMPULSE_HIGH) == "up"
    assert direction_from_anchors(HI, LO) == "down"


def test_direction_rejects_degenerate():
    with pytest.raises(ValueError, match="degenerate"):
        direction_from_anchors(HI, Anchor("2020-02-14T00:00:00+00:00", 10500.0))


def test_time_ordered_puts_origin_first_and_matches_direction():
    # Down leg: high is earlier in time → origin; direction resolves to "down".
    origin, endpoint = time_ordered(HI, LO)
    assert (origin, endpoint) == (HI, LO)
    assert direction_from_anchors(origin, endpoint) == "down"
    # Up leg: fresh low earlier → origin; even if passed high-first, order flips to low-first.
    origin, endpoint = time_ordered(IMPULSE_HIGH, FRESH_LOW)
    assert (origin, endpoint) == (FRESH_LOW, IMPULSE_HIGH)
    assert direction_from_anchors(origin, endpoint) == "up"


def test_next_candidate_id_increments_past_max():
    assert next_candidate_id([]) == "c1"
    c1 = make_candidate(FRESH_LOW, IMPULSE_HIGH, "accepted")
    assert next_candidate_id([c1]) == "c2"
    # Gaps tolerated: id continues past the max, not the count.
    c5 = Candidate("c5", FRESH_LOW, IMPULSE_HIGH, "up", "rejected")
    assert next_candidate_id([c1, c5]) == "c6"


def test_make_candidate_infers_direction_and_carries_reason_tags():
    cand = make_candidate(
        HI, LO, "rejected", reason="wrong scale — the parent crash leg", tags=("wrong_scale",)
    )
    assert cand.id == "c1"
    assert cand.direction == "down"
    assert cand.label == "rejected"
    assert cand.reason.startswith("wrong scale")
    assert cand.tags == ("wrong_scale",)


def test_make_candidate_rejects_unknown_tag():
    with pytest.raises(ValueError, match="unknown tags"):
        make_candidate(FRESH_LOW, IMPULSE_HIGH, "accepted", tags=("not_a_real_tag",))


def test_build_window_defaults_to_human_provenance():
    cand = make_candidate(FRESH_LOW, IMPULSE_HIGH, "accepted")
    window = build_window(
        symbol="BTC/USD",
        timeframe="1d",
        exchange="bitfinex",
        window_start="2020-02-01",
        window_end="2020-04-30",
        candidates=[cand],
    )
    assert window.created_by == "human"
    assert window.is_human
    assert window.accepted_ids == ["c1"]


def test_default_window_path_slugs_symbol_and_compacts_day():
    cand = make_candidate(FRESH_LOW, IMPULSE_HIGH, "accepted")
    window = build_window(
        symbol="BTC/USD",
        timeframe="4h",
        exchange="bitfinex",
        window_start="2021-01-21T00:00:00+00:00",
        window_end="2021-02-01",
        candidates=[cand],
    )
    path = default_window_path("data/labels/selection_annotations", window)
    assert path.as_posix().endswith(
        "selection_annotations/bitfinex/BTC-USD/4h/window_20210121.yaml"
    )


def test_save_window_round_trips_through_load(tmp_path):
    cands = [
        make_candidate(FRESH_LOW, IMPULSE_HIGH, "accepted", reason="clean impulse"),
        make_candidate(
            HI, LO, "rejected", existing=None, reason="parent crash", tags=("wrong_scale",)
        ),
    ]
    # Give the second candidate a distinct id (both built with existing=None → both c1).
    cands[1] = make_candidate(
        HI, LO, "rejected", existing=[cands[0]], reason="parent crash", tags=("wrong_scale",)
    )
    window = build_window(
        symbol="BTC/USD",
        timeframe="1w",
        exchange="bitfinex",
        window_start="2020-11-12",
        window_end="2021-01-21",
        candidates=cands,
    )
    path = save_window(window, tmp_path)
    assert path.exists()
    reloaded = load_window(path)
    assert [c.id for c in reloaded.candidates] == ["c1", "c2"]
    assert reloaded.candidates[1].direction == "down"
    assert reloaded.candidates[1].tags == ("wrong_scale",)
    assert reloaded.accepted_ids == ["c1"]
