"""Sequential-conditioning feature: predecessor lookup + chained_origin logic (prereg 2026-07-21)."""

import numpy as np
import pandas as pd

from fibengine.research.selection_learning import HumanLeg
from fibengine.research.selection_sequential import (
    SeqCandidate,
    chained_origin_features,
    facit_positions,
    nondegenerate_legs,
)


def _df(n=200, start_price=100.0):
    idx = pd.date_range("2024-01-01", periods=n, freq="4h", tz="UTC")
    prices = start_price + np.linspace(0, 10, n)
    return pd.DataFrame(
        {"open": prices, "high": prices + 1, "low": prices - 1, "close": prices},
        index=idx,
    )


def _leg(df, a_pos, b_pos, a_price, b_price):
    return HumanLeg(
        anchor_a_ts=df.index[a_pos],
        anchor_a_price=a_price,
        anchor_b_ts=df.index[b_pos],
        anchor_b_price=b_price,
        direction="up" if b_price > a_price else "down",
    )


def _cand(start_pos, start_price, b_pos=150):
    return SeqCandidate(
        anchor_b_pos=b_pos, start_pos=start_pos, start_price=start_price, features={}, label=0
    )


def test_exact_chain_scores_one():
    df = _df()
    legs = [_leg(df, 10, 50, 90.0, 120.0)]
    fp = facit_positions(df, legs)
    # candidate origin exactly on the predecessor endpoint (bar 50, price 120)
    chained, prox, _ = chained_origin_features([_cand(50, 120.0)], fp, 3)
    assert chained[0] == 1.0
    assert prox[0] == 1.0  # bar_dist 0


def test_far_origin_scores_zero_and_prox_decays():
    df = _df()
    legs = [_leg(df, 10, 50, 90.0, 120.0)]
    fp = facit_positions(df, legs)
    chained, prox, _ = chained_origin_features([_cand(120, 200.0)], fp, 3)
    assert chained[0] == 0.0
    assert prox[0] == 1.0 / 71.0  # 1/(1+|120-50|)


def test_no_predecessor_scores_zero():
    df = _df()
    legs = [_leg(df, 100, 140, 90.0, 120.0)]  # completes after the candidate's origin
    fp = facit_positions(df, legs)
    chained, prox, _ = chained_origin_features([_cand(50, 120.0)], fp, 3)
    assert chained[0] == 0.0 and prox[0] == 0.0


def test_predecessor_is_latest_completed_before_origin():
    df = _df()
    early = _leg(df, 5, 20, 90.0, 100.0)
    late = _leg(df, 30, 60, 95.0, 130.0)
    fp = facit_positions(df, [early, late])
    # origin at bar 60 -> predecessor must be `late` (endpoint 130 @ bar 60), not `early`
    chained_hit, _, _ = chained_origin_features([_cand(60, 130.0)], fp, 3)
    chained_early_price, _, _ = chained_origin_features([_cand(60, 100.0)], fp, 3)
    assert chained_hit[0] == 1.0
    assert chained_early_price[0] == 0.0  # right bar, wrong price (early leg's endpoint)


def test_within_locked_band_counts_as_chained():
    df = _df()
    legs = [_leg(df, 10, 50, 90.0, 120.0)]
    fp = facit_positions(df, legs)
    # +2 bars, +1% price: inside NEAR (3 bars / 2.0%) for origins -> chained
    chained, _, _ = chained_origin_features([_cand(52, 121.2)], fp, 3)
    assert chained[0] == 1.0
    # +5 bars: outside the NEAR bar band -> not chained
    chained_far, _, _ = chained_origin_features([_cand(55, 120.0)], fp, 3)
    assert chained_far[0] == 0.0


def test_self_leg_cannot_be_predecessor():
    """Prereg section 9 A1: a leg able to eps-match the candidate's endpoint is banned."""
    df = _df()
    # short human leg ending at bar 50; candidate start=50, end=52 (within eps of b_pos)
    legs = [_leg(df, 47, 50, 90.0, 120.0)]
    fp = facit_positions(df, legs)
    chained, prox, n_excl = chained_origin_features([_cand(50, 120.0, b_pos=52)], fp, 3)
    # unrestricted lookup would have found the leg (b_pos 50 <= start 50) -> banned by the
    # second condition (b_pos 50 >= anchor_b_pos 52 - 3), counted as a rule exclusion
    assert chained[0] == 0.0 and prox[0] == 0.0
    assert n_excl == 1
    # a genuinely prior leg stays eligible for the same candidate geometry
    legs2 = [_leg(df, 20, 40, 90.0, 118.0)]
    fp2 = facit_positions(df, legs2)
    chained2, _, n_excl2 = chained_origin_features([_cand(50, 120.0, b_pos=52)], fp2, 3)
    assert n_excl2 == 0
    assert chained2[0] == 0.0  # bar 40 vs start 50: outside the NEAR bar band -> not chained


def test_nondegenerate_filter_excludes_same_candle_legs():
    df = _df()
    good = _leg(df, 10, 50, 90.0, 120.0)
    bad = _leg(df, 60, 60, 130.0, 110.0)  # same-candle misclick (a_ts == b_ts)
    kept, n_excluded = nondegenerate_legs([good, bad])
    assert kept == [good]
    assert n_excluded == 1
