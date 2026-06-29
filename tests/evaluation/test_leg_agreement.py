"""Tests for the leg-agreement ruler — the locked synthetic sanity table + diagnostics."""

from __future__ import annotations

import pytest

from fibengine.evaluation.leg_agreement import (
    W_LOCKED,
    Leg,
    auc,
    best_match,
    leg_agreement,
    leg_agreement_iou,
    leg_agreement_min,
)

# A down leg: high bar earlier (10) than low bar (40).
FACIT = Leg(high_bar=10, low_bar=40)


# --- locked knob ---------------------------------------------------------------


def test_locked_window_is_two():
    assert W_LOCKED == 2


# --- Leg basics ----------------------------------------------------------------


def test_direction_down_when_high_earlier():
    assert Leg(10, 40).direction == "down"


def test_direction_up_when_low_earlier():
    assert Leg(40, 10).direction == "up"


def test_degenerate_leg_rejected():
    with pytest.raises(ValueError):
        Leg(10, 10)


def test_span_bars():
    assert Leg(10, 40).span_bars == 30


# --- synthetic sanity table (LOCKED decision rule) -----------------------------


def test_identity_is_one():
    assert leg_agreement(FACIT, FACIT) == 1.0


def test_off_by_one_is_graded():
    # one endpoint shifted 1 bar: s_high=1, s_low=max(0,1-1/2)=0.5 -> mean 0.75
    shifted = Leg(high_bar=10, low_bar=41)
    score = leg_agreement(FACIT, shifted)
    assert 0.0 < score < 1.0
    assert score == pytest.approx(0.75)


def test_direction_flip_is_zero():
    flipped = Leg(high_bar=40, low_bar=10)  # up, not down
    assert leg_agreement(FACIT, flipped) == 0.0


def test_disjoint_is_zero():
    far = Leg(high_bar=100, low_bar=130)  # both endpoints >= W away
    assert leg_agreement(FACIT, far) == 0.0


def test_two_bar_miss_hits_zero_at_locked_w():
    # at W=2, Δbar=2 -> s=0; both endpoints 2 off -> 0
    two_off = Leg(high_bar=12, low_bar=42)
    assert leg_agreement(FACIT, two_off) == 0.0


# --- secondary diagnostics (NOT the gate) --------------------------------------


def test_min_is_stricter_than_mean_on_one_sided_miss():
    shifted = Leg(high_bar=10, low_bar=41)  # high perfect, low 1 off
    assert leg_agreement_min(FACIT, shifted) == pytest.approx(0.5)
    assert leg_agreement(FACIT, shifted) == pytest.approx(0.75)
    assert leg_agreement_min(FACIT, shifted) < leg_agreement(FACIT, shifted)


def test_min_direction_gated():
    assert leg_agreement_min(FACIT, Leg(40, 10)) == 0.0


def test_iou_identity_is_one():
    assert leg_agreement_iou(FACIT, FACIT) == 1.0


def test_iou_partial_overlap():
    # facit span [10,40]; cand span [25,55] same direction -> inter [25,40]=15, union [10,55]=45
    cand = Leg(high_bar=25, low_bar=55)
    assert leg_agreement_iou(FACIT, cand) == pytest.approx(15 / 45)


def test_iou_direction_gated():
    assert leg_agreement_iou(FACIT, Leg(40, 10)) == 0.0


# --- best-match assignment -----------------------------------------------------


def test_best_match_picks_closest_facit():
    cand = Leg(high_bar=11, low_bar=40)  # near FACIT, far from the other
    other = Leg(high_bar=200, low_bar=230)
    idx, score = best_match(cand, [other, FACIT])
    assert idx == 1
    assert score == pytest.approx(0.75)


def test_best_match_empty_raises():
    with pytest.raises(ValueError):
        best_match(FACIT, [])


# --- auc gate statistic --------------------------------------------------------


def test_auc_perfect_separation():
    assert auc([1.0, 1.0, 0.9], [0.0, 0.1, 0.2]) == 1.0


def test_auc_chance_is_half():
    assert auc([0.5, 0.5], [0.5, 0.5]) == 0.5


def test_auc_ties_count_half():
    # pos {1,0}, neg {1,0}: pairs (1>1)=.5 (1>0)=1 (0>1)=0 (0>0)=.5 -> mean .5
    assert auc([1.0, 0.0], [1.0, 0.0]) == pytest.approx(0.5)


def test_auc_empty_raises():
    with pytest.raises(ValueError):
        auc([], [1.0])
