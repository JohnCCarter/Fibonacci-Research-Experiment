"""Tests for the locked acceptance tolerance (graded 3-tier "snarlikt räcker")."""

from __future__ import annotations

import pytest

from fibengine.evaluation.acceptance import (
    ACCEPT_AT,
    MatchTier,
    anchor_accepted,
    classify_anchor,
    leg_accepted,
    price_pct,
)


def test_price_pct_basic_and_zero_guard():
    assert price_pct(102.0, 100.0) == pytest.approx(2.0)
    with pytest.raises(ValueError, match="non-zero"):
        price_pct(1.0, 0.0)


def test_origin_tiers_by_price_and_bars():
    # EXACT: within 1 bar and 0.75%.
    assert (
        classify_anchor(100.5, 100.0, is_origin=True, pred_bar=10, true_bar=10) == MatchTier.EXACT
    )
    # SNARLIKT: 1.4% and 2 bars.
    assert (
        classify_anchor(101.4, 100.0, is_origin=True, pred_bar=12, true_bar=10)
        == MatchTier.SNARLIKT
    )
    # NEAR: 2.0% and 3 bars.
    assert classify_anchor(102.0, 100.0, is_origin=True, pred_bar=13, true_bar=10) == MatchTier.NEAR
    # MISS: 2.5% price is beyond the NEAR band (2%).
    assert classify_anchor(102.5, 100.0, is_origin=True, pred_bar=10, true_bar=10) == MatchTier.MISS


def test_origin_weakest_link_bar_offset_caps_the_tier():
    # Price is EXACT-tight (0.5%) but the bar offset is 3 → capped down to NEAR.
    assert classify_anchor(100.5, 100.0, is_origin=True, pred_bar=13, true_bar=10) == MatchTier.NEAR
    # Bar offset 4 (> NEAR's 3) → MISS despite exact price.
    assert classify_anchor(100.5, 100.0, is_origin=True, pred_bar=14, true_bar=10) == MatchTier.MISS


def test_endpoint_is_price_only_and_looser():
    # 3.5% with no bar info → SNARLIKT for the endpoint (would be MISS for the origin).
    assert classify_anchor(103.5, 100.0, is_origin=False) == MatchTier.SNARLIKT
    assert classify_anchor(103.5, 100.0, is_origin=True) == MatchTier.MISS
    # 6% endpoint = NEAR; 6.1% = MISS.
    assert classify_anchor(106.0, 100.0, is_origin=False) == MatchTier.NEAR
    assert classify_anchor(106.1, 100.0, is_origin=False) == MatchTier.MISS


def test_accept_line_is_near_by_default():
    assert ACCEPT_AT == MatchTier.NEAR
    assert anchor_accepted(MatchTier.NEAR)
    assert anchor_accepted(MatchTier.SNARLIKT)
    assert not anchor_accepted(MatchTier.MISS)
    # A stricter accept line rejects NEAR.
    assert not anchor_accepted(MatchTier.NEAR, accept_at=MatchTier.SNARLIKT)


def test_leg_accepted_weakest_link():
    assert leg_accepted(MatchTier.EXACT, MatchTier.NEAR)
    assert not leg_accepted(MatchTier.EXACT, MatchTier.MISS)
    assert not leg_accepted(MatchTier.MISS, MatchTier.EXACT)


def test_hob_origin_is_a_real_miss():
    # HO-B: engine origin 63,229 vs human 61,773 = ~2.36% price AND a different swing (bars apart) →
    # a genuine origin MISS even at the generous NEAR line; the "0" endpoints (~58,13x) agree.
    origin = classify_anchor(63229.0, 61773.0, is_origin=True, pred_bar=0, true_bar=25)
    endpoint = classify_anchor(58136.0, 58134.0, is_origin=False)
    assert origin == MatchTier.MISS
    assert endpoint == MatchTier.EXACT
    assert not leg_accepted(origin, endpoint)
