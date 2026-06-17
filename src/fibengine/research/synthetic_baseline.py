"""Synthetic random-walk baseline generator (research-only, Lean Fib Research).

Pairs with **NU-1** of the standing prereg addendum
(`docs/research_wiki/reviews/horizontal-structure-prereg-addendum-20260617.md`): any future
horizontal-structure study must pre-register a synthetic random-walk control in addition to the
shuffle-price placebo and the causal-swing baseline. Support/resistance levels and chart
formations emerge spontaneously in pure random walks (Lo, Mamaysky & Wang 2000, *Journal of
Finance* 55(4)), so a level-reaction claim must beat a matched random-walk null — not only a
shuffled-price one.

This module is the **generator primitive only**. It is:
  * **deterministic** — all randomness flows through a caller-supplied ``np.random.Generator``;
  * **strictly causal** — it calibrates only on the history array the caller passes (a caller
    must pass bars strictly *before* a level's ``known_after_ts``);
  * **decoupled** — it returns plain floats / arrays and imports nothing from any study, so it
    cannot reopen or alter the closed BTC/Fib behaviour line. A future prereg wires these levels
    into an event study with the appropriate ``known_after_ts`` metadata.

No trading/edge claim, no auto-fib, no label mutation.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "synthetic_log_return_path",
    "synthetic_price_series",
    "random_walk_swing_levels",
]


def _log_returns(close: np.ndarray) -> np.ndarray:
    close = np.asarray(close, dtype=float)
    if close.ndim != 1 or close.size < 2:
        raise ValueError("history close must be a 1-D array of length >= 2")
    if (close <= 0).any():
        raise ValueError("history close must be strictly positive (log scale)")
    return np.diff(np.log(close))


def synthetic_log_return_path(
    history_close: np.ndarray,
    n_steps: int,
    rng: np.random.Generator,
    *,
    method: str = "gbm",
    block: int = 5,
) -> np.ndarray:
    """Generate ``n_steps`` synthetic log-returns calibrated on ``history_close``.

    ``method="gbm"`` draws i.i.d. Normal(mu, sigma) returns with mu/sigma estimated from the
    history (geometric Brownian motion). ``method="block"`` block-bootstraps the empirical
    returns in contiguous blocks of length ``block`` so short-range autocorrelation/volatility
    clustering is preserved. Both use only ``history_close`` (causal) and only ``rng`` for
    randomness (deterministic).
    """
    if n_steps < 1:
        raise ValueError("n_steps must be >= 1")
    rets = _log_returns(history_close)
    if method == "gbm":
        mu = float(rets.mean())
        sigma = float(rets.std(ddof=1)) if rets.size > 1 else 0.0
        return rng.normal(mu, sigma, size=n_steps)
    if method == "block":
        if block < 1:
            raise ValueError("block length must be >= 1")
        out = np.empty(n_steps, dtype=float)
        filled = 0
        max_start = rets.size - block
        while filled < n_steps:
            start = 0 if max_start <= 0 else int(rng.integers(0, max_start + 1))
            chunk = rets[start : start + block]
            take = min(chunk.size, n_steps - filled)
            out[filled : filled + take] = chunk[:take]
            filled += take
        return out
    raise ValueError(f"unknown method {method!r} (expected 'gbm' or 'block')")


def synthetic_price_series(
    history_close: np.ndarray,
    n_steps: int,
    rng: np.random.Generator,
    *,
    method: str = "gbm",
    block: int = 5,
) -> np.ndarray:
    """A synthetic price path of length ``n_steps + 1`` starting at ``history_close[-1]``.

    The path is ``start * exp(cumsum(synthetic_log_returns))`` with a leading ``start`` point,
    so prices stay strictly positive and begin where the real history ended (causal hand-off).
    """
    start = float(np.asarray(history_close, dtype=float)[-1])
    steps = synthetic_log_return_path(history_close, n_steps, rng, method=method, block=block)
    return start * np.exp(np.concatenate(([0.0], np.cumsum(steps))))


def random_walk_swing_levels(
    history_close: np.ndarray,
    n_steps: int,
    rng: np.random.Generator,
    *,
    pivot_k: int = 3,
    method: str = "gbm",
    block: int = 5,
) -> list[float]:
    """Horizontal levels that a *random walk* spontaneously produces (Lo et al. 2000).

    Simulates one synthetic price path (``synthetic_price_series``) and returns the prices of its
    fractal swing highs/lows (half-width ``pivot_k``) — the random-walk analogue of "levels a
    chartist would draw." Returned as plain floats; a future study attaches ``known_after_ts``.
    Empty if the path has no qualifying pivot.
    """
    series = synthetic_price_series(history_close, n_steps, rng, method=method, block=block)
    n = series.size
    k = pivot_k
    if k < 1 or n < 2 * k + 1:
        return []
    levels: list[float] = []
    for i in range(k, n - k):
        window = series[i - k : i + k + 1]
        if series[i] == window.max() and window.argmax() == k:
            levels.append(float(series[i]))
        if series[i] == window.min() and window.argmin() == k:
            levels.append(float(series[i]))
    return levels
