"""SENARE-1 ship-gate: the e-value must satisfy E[E] <= 1 under H0 (the math IS the deliverable).

The primary gate is the *exact* conditional identity ``sum_x P_0(x) * E(x) = 1`` computed with
``math.comb`` (independent of the module internals), which holds at every N — not a no-crash check.
Monte-Carlo draws then confirm it empirically at small and large N, plus the anytime threshold
fires on <= alpha of null runs and the e-value grows under a true alternative.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from fibengine.research.anytime_valid import (
    DEFAULT_PSI_GRID,
    conditional_bernoulli_evalue,
    evalue_to_pvalue,
    holm_evalues,
)


def _hg_pmf(x: int, n_s: int, n_c: int, t: int) -> float:
    """Central hypergeometric P0(k_s = x | total = t), via exact integer combinatorics."""
    return math.comb(n_s, x) * math.comb(n_c, t - x) / math.comb(n_s + n_c, t)


@pytest.mark.parametrize(
    ("n_s", "n_c", "t"),
    [(8, 6, 5), (8, 6, 1), (8, 6, 13), (5, 12, 7), (40, 35, 30), (3, 3, 3), (250, 250, 120)],
)
def test_evalue_is_exact_under_null(n_s, n_c, t):
    """E[E | t] = sum_x P0(x) E(x) = 1 EXACTLY at every N — the conditional validity guarantee.

    This is the primary ship-gate: a deterministic identity, no Monte-Carlo noise, holding at
    small AND large N. (A sample mean of the e-value converges slowly because the e-value is
    heavy-tailed — see the large-N test below — so exactness is proven here, not by MC averaging.)
    """
    u_min, u_max = max(0, t - n_c), min(t, n_s)
    expectation = sum(
        _hg_pmf(x, n_s, n_c, t) * conditional_bernoulli_evalue(x, n_s, t - x, n_c)
        for x in range(u_min, u_max + 1)
    )
    assert expectation == pytest.approx(1.0, abs=1e-9)


def test_single_support_point_is_no_evidence():
    """When the conditional support is a single point the e-value must be exactly 1 (Vandermonde)."""
    assert conditional_bernoulli_evalue(0, 5, 0, 7) == pytest.approx(1.0)  # t = 0
    assert conditional_bernoulli_evalue(5, 5, 7, 7) == pytest.approx(1.0)  # t = N


def test_zero_events_returns_no_evidence():
    assert conditional_bernoulli_evalue(0, 0, 3, 10) == 1.0
    assert conditional_bernoulli_evalue(3, 10, 0, 0) == 1.0


def _null_evalues(n_s, n_c, p, draws, seed=20260616):
    rng = np.random.default_rng(seed)
    k_s = rng.binomial(n_s, p, size=draws)
    k_c = rng.binomial(n_c, p, size=draws)
    return np.array(
        [
            conditional_bernoulli_evalue(int(a), n_s, int(b), n_c)
            for a, b in zip(k_s, k_c, strict=True)
        ]
    )


@pytest.mark.parametrize(("n_s", "n_c", "p"), [(12, 12, 0.4), (15, 20, 0.5)])
def test_mc_null_small_n(n_s, n_c, p):
    """Small N: the e-value is bounded enough that the sample mean tracks E[E]=1 directly."""
    es = _null_evalues(n_s, n_c, p, draws=30000)
    assert 0.85 <= es.mean() <= 1.15
    assert np.mean(es >= 1.0 / 0.05) <= 0.07  # Ville/Markov: P(E >= 1/alpha) <= alpha


def test_mc_null_large_n_threshold_fires_at_most_alpha():
    """Large N: the e-value is heavy-tailed, so 30k draws cannot pin its (exactly-1) mean — see
    ``test_evalue_is_exact_under_null`` for the deterministic large-N proof. The operationally
    meaningful, tail-robust guarantee is the anytime threshold: P(E >= 1/alpha) <= alpha (Ville)."""
    es = _null_evalues(250, 250, 0.3, draws=30000)
    assert np.mean(es >= 1.0 / 0.05) <= 0.07


def test_mc_alternative_accumulates_evidence():
    """Under a true alternative (subject rejects more) the mean e-value must exceed 1."""
    rng = np.random.default_rng(20260616)
    draws = 20000
    n_s = n_c = 200
    k_s = rng.binomial(n_s, 0.45, size=draws)
    k_c = rng.binomial(n_c, 0.30, size=draws)
    es = np.array(
        [
            conditional_bernoulli_evalue(int(a), n_s, int(b), n_c)
            for a, b in zip(k_s, k_c, strict=True)
        ]
    )
    assert es.mean() > 1.0


def test_evalue_to_pvalue_calibration():
    assert evalue_to_pvalue(1.0) == pytest.approx(1.0)
    assert evalue_to_pvalue(20.0) == pytest.approx(0.05)
    assert evalue_to_pvalue(0.5) == 1.0  # capped at 1
    assert evalue_to_pvalue(math.inf) == 0.0


def test_holm_evalues_controls_family():
    """One overwhelming e-value clears e-Holm; weak ones do not."""
    result = holm_evalues({"swing-1d": 1e6, "round-1d": 1.0, "prior-1d": 2.0}, alpha=0.05)
    assert result["swing-1d"] is True
    assert result["round-1d"] is False
    assert result["prior-1d"] is False


def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError):
        conditional_bernoulli_evalue(5, 3, 0, 10)  # k_s > n_s
    with pytest.raises(ValueError):
        conditional_bernoulli_evalue(1, 10, 1, 10, psi_grid=(0.0,))  # psi <= 0
    with pytest.raises(ValueError):
        conditional_bernoulli_evalue(1, 10, 1, 10, weights=(0.5, 0.5))  # weights/grid mismatch
    with pytest.raises(ValueError):
        conditional_bernoulli_evalue(1, 10, 1, 10, weights=(0.2, 0.2, 0.2))  # weights sum != 1


def test_default_grid_is_one_sided_above_one():
    assert all(psi > 1.0 for psi in DEFAULT_PSI_GRID)
