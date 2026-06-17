"""Tests for the synthetic random-walk baseline generator (NU-1 primitive).

Hermetic: no network, no corpus. Asserts determinism, positivity, and fail-closed inputs.
"""

from __future__ import annotations

import numpy as np
import pytest

from fibengine.research.synthetic_baseline import (
    random_walk_swing_levels,
    synthetic_log_return_path,
    synthetic_price_series,
)

SEED = 20260616


def _history() -> np.ndarray:
    # A gently trending positive price history.
    return 100.0 * np.exp(np.cumsum(np.full(200, 0.001)))


def test_price_series_is_deterministic_per_seed():
    h = _history()
    a = synthetic_price_series(h, 50, np.random.default_rng(SEED))
    b = synthetic_price_series(h, 50, np.random.default_rng(SEED))
    assert np.array_equal(a, b)


def test_different_seeds_diverge():
    h = _history()
    a = synthetic_price_series(h, 50, np.random.default_rng(1))
    b = synthetic_price_series(h, 50, np.random.default_rng(2))
    assert not np.array_equal(a, b)


def test_price_series_starts_at_last_history_and_is_positive():
    h = _history()
    series = synthetic_price_series(h, 50, np.random.default_rng(SEED))
    assert series.size == 51  # n_steps + 1 (leading start point)
    assert series[0] == pytest.approx(float(h[-1]))
    assert (series > 0).all()


@pytest.mark.parametrize("method", ["gbm", "block"])
def test_both_methods_produce_positive_paths(method):
    h = _history()
    series = synthetic_price_series(h, 80, np.random.default_rng(SEED), method=method)
    assert (series > 0).all()
    assert series.size == 81


def test_log_return_path_length():
    h = _history()
    steps = synthetic_log_return_path(h, 30, np.random.default_rng(SEED))
    assert steps.shape == (30,)


def test_swing_levels_are_path_values_and_deterministic():
    h = _history()
    a = random_walk_swing_levels(h, 120, np.random.default_rng(SEED))
    b = random_walk_swing_levels(h, 120, np.random.default_rng(SEED))
    assert a == b
    assert all(price > 0 for price in a)


def test_swing_levels_empty_when_path_too_short():
    h = _history()
    assert random_walk_swing_levels(h, 2, np.random.default_rng(SEED), pivot_k=3) == []


def test_fail_closed_non_positive_history():
    bad = np.array([100.0, -1.0, 50.0])
    with pytest.raises(ValueError, match="strictly positive"):
        synthetic_price_series(bad, 10, np.random.default_rng(SEED))


def test_fail_closed_short_history():
    with pytest.raises(ValueError, match="length >= 2"):
        synthetic_log_return_path(np.array([100.0]), 10, np.random.default_rng(SEED))


def test_fail_closed_unknown_method():
    h = _history()
    with pytest.raises(ValueError, match="unknown method"):
        synthetic_log_return_path(h, 10, np.random.default_rng(SEED), method="nope")


def test_fail_closed_bad_n_steps():
    h = _history()
    with pytest.raises(ValueError, match="n_steps must be"):
        synthetic_log_return_path(h, 0, np.random.default_rng(SEED))
