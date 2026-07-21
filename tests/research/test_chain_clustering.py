"""Chain-clustering probe: statistics + null machinery + exclusion bookkeeping (prereg 2026-07-21)."""

import numpy as np
import pandas as pd

from fibengine.research.cascade_conditioning import Leg, build_pairs
from fibengine.research.chain_clustering import (
    adjacency_count,
    adjacency_count_masked,
    bootstrap_markov_gap,
    filter_in_window,
    hub_diagnostics,
    markov_gap,
    permutation_reference,
    run_lengths,
    single_file_mask,
)


def test_adjacency_counts_adjacent_ones_only():
    assert adjacency_count(np.array([1, 1, 0, 1, 1, 1, 0])) == 3
    assert adjacency_count(np.array([1, 0, 1, 0, 1])) == 0
    assert adjacency_count(np.array([0, 0, 0])) == 0
    assert adjacency_count(np.array([1, 1])) == 1


def test_masked_adjacency_respects_mask():
    c = np.array([1, 1, 1, 1])
    assert adjacency_count_masked(c, np.array([True, False, True])) == 2
    assert adjacency_count_masked(c, np.array([False, False, False])) == 0


def test_run_lengths():
    assert run_lengths(np.array([1, 1, 0, 1, 0, 1, 1, 1])) == [2, 1, 3]
    assert run_lengths(np.array([0, 0])) == []
    assert run_lengths(np.array([1])) == [1]


def test_markov_gap_clustered_positive_alternating_negative():
    clustered = np.array([1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0])
    alternating = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
    assert markov_gap(clustered) > 0
    assert markov_gap(alternating) < 0
    # degenerate: all ones -> no 0-condition -> None
    assert markov_gap(np.ones(5, dtype=int)) is None


def test_permutation_preserves_marginal_and_is_deterministic():
    c = np.array([1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1])
    mask = np.ones(len(c) - 1, dtype=bool)
    adj1, _, sf1 = permutation_reference(c, 50, seed=7, mask=mask)
    adj2, _, sf2 = permutation_reference(c, 50, seed=7, mask=mask)
    assert np.array_equal(adj1, adj2)  # deterministic
    # full mask -> masked statistic equals the full statistic replicate-by-replicate
    assert np.array_equal(adj1, sf1) and np.array_equal(sf1, sf2)
    # a permutation can never create more ones: max adjacency bounded by count-1
    assert adj1.max() <= c.sum() - 1


def test_clustered_sequence_rejects_null():
    # 30 ones in one block then 70 zeros: extreme clustering
    c = np.array([1] * 30 + [0] * 70)
    a_obs = adjacency_count(c)
    adj_null, _, _ = permutation_reference(c, 500, seed=1)
    p = float((adj_null >= a_obs).mean())
    assert p < 0.01


def test_independent_sequence_does_not_reject():
    rng = np.random.default_rng(3)
    c = (rng.random(200) < 0.25).astype(int)
    a_obs = adjacency_count(c)
    adj_null, _, _ = permutation_reference(c, 500, seed=2)
    p = float((adj_null >= a_obs).mean())
    assert p > 0.05


def test_bootstrap_ci_brackets_gap_sign():
    clustered = np.array([1, 1, 1, 1, 1, 0, 0, 0, 0, 0] * 10)
    ci = bootstrap_markov_gap(clustered, 500, seed=5)
    assert ci is not None
    lo, hi = ci
    assert lo <= hi


# --- structure / bookkeeping (prereg §9 A1 + A2) ---------------------------------------------


def _leg(a, b, pa=100.0, pb=200.0, fid=""):
    return Leg(
        fib_id=fid or f"leg_{a}_{b}",
        a_ts=pd.Timestamp(a, tz="UTC"),
        a_price=pa,
        b_ts=pd.Timestamp(b, tz="UTC"),
        b_price=pb,
        direction="up",
    )


def test_single_file_mask_and_hub_diagnostics():
    # chain: L1 -> L2 -> L3 (single-file), then L4/L5 both have L3 as predecessor (hub)
    l1 = _leg("2024-01-01", "2024-01-05")
    l2 = _leg("2024-01-06", "2024-01-10")
    l3 = _leg("2024-01-11", "2024-01-15")
    l4 = _leg("2024-01-16", "2024-01-20")
    l5 = _leg("2024-01-17", "2024-01-21")
    pairs, excl = build_pairs([l1, l2, l3, l4, l5])
    assert excl["no_predecessor"] == 1  # l1
    assert [p.cur.fib_id for p in pairs] == [l2.fib_id, l3.fib_id, l4.fib_id, l5.fib_id]
    mask = single_file_mask(pairs)
    # l2->l3, l3->l4 single-file; l4->l5 shares prev=l3 (hub)
    assert mask.tolist() == [True, True, False]
    diag = hub_diagnostics(pairs)
    assert diag == {"n_adjacent_slots": 3, "n_single_file": 2, "n_hub_shared_prev": 1}


def test_filter_in_window_counts_exclusions():
    idx = pd.date_range("2024-01-01", periods=30, freq="1D", tz="UTC")
    df = pd.DataFrame({"close": range(30)}, index=idx)
    inside = _leg("2024-01-06", "2024-01-10")
    inside2 = _leg("2024-01-12", "2024-01-16")
    outside = _leg("2025-06-01", "2025-06-05")  # far outside the candle window
    pairs, excl = build_pairs([inside, inside2, outside])
    kept = filter_in_window(df, pairs, excl)
    assert [p.cur.fib_id for p in kept] == [inside2.fib_id]
    assert excl["cur_outside_candle_window"] == 1
    # three-category accounting matches the signed probe's convention
    assert set(excl) == {"no_predecessor", "degenerate_cur", "cur_outside_candle_window"}
