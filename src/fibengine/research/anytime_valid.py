"""SENARE-1 — anytime-valid e-value for a two-sample Bernoulli comparison (research-only).

Pairs with **NU-2** of the standing prereg addendum
(`docs/research_wiki/reviews/horizontal-structure-prereg-addendum-20260617.md`) and §8 of the
horizontal-structure prereg: when a study is a re-look at a window already peeked at, a fresh
fixed-horizon permutation p-value is invalid (optional stopping). An **e-value** stays valid under
continuous monitoring / optional continuation.

**Construction (pinned in prereg §8 amendment 2026-06-17, blind to any result):** the conditional
**2×2 / Fisher noncentral-hypergeometric** e-value. Testing whether the *subject* reject rate
exceeds the *control* (RW-null) rate, we condition on the total reject count ``t = k_s + k_c``.
Under H0 (``p_subject = p_control``) the conditional law of ``k_s`` is the central hypergeometric —
**free of the nuisance base rate** — so validity is *exact at every sample size*, not asymptotic
(the closed study's hardest TFs have N < 30). For a fixed alternative odds ratio ``psi`` the
e-value is the noncentral/central likelihood ratio

    E_psi(k_s) = psi**k_s * C(N, t) / Z(psi),   Z(psi) = sum_u C(n_s,u) C(n_c,t-u) psi**u

over the conditional support ``u in [max(0, t-n_c), min(t, n_s)]``. By Vandermonde's identity
``sum_u C(n_s,u) C(n_c,t-u) = C(N,t)``, so ``E[E_psi | t] = sum_x P_0(x) E_psi(x) = sum_x P_psi(x)
= 1`` **exactly**. Any convex mixture over a grid of ``psi`` inherits ``E[E]=1`` — therefore the
grid choice affects **power only, never the Type-I guarantee** (see ``DEFAULT_PSI_GRID``).

Lineage: Johari, Pekelis & Walsh (arXiv:1512.04922) for anytime-valid inference generally;
Grünwald, de Heide & Koolen, *Safe Testing* (2024) and Turner, Ly & Grünwald (two-sample / 2×2
safe tests) for the conditional e-value form.

Multiplicity: calibrate ``p = min(1, 1/E)`` (Markov / Ville) and feed into the repo's existing
tested Holm-Bonferroni (``fib_context_conditioned_study._holm``) — Holm controls FWER under
arbitrary dependence, so this is the e-value analogue of the Holm the repo already applies.

No trading/edge claim, no auto-fib, no label mutation.
"""

from __future__ import annotations

import math

# Reuse the repo's already-tested Holm-Bonferroni rather than re-implementing it (NU-2 / §8).
from fibengine.research.fib_context_conditioned_study import _holm

__all__ = [
    "DEFAULT_PSI_GRID",
    "conditional_bernoulli_evalue",
    "evalue_to_pvalue",
    "holm_evalues",
]

# One-sided alternative grid (subject repels MORE → odds ratio > 1). Equal weights. Pinned in
# prereg §8 before running, blind to output; affects power only — validity is exact for any prior.
DEFAULT_PSI_GRID: tuple[float, ...] = (1.5, 2.0, 3.0)


def _log_comb(n: int, k: int) -> float:
    """log C(n, k); -inf outside the valid range so out-of-support terms drop in log-sum-exp."""
    if k < 0 or k > n:
        return -math.inf
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def _logsumexp(values: list[float]) -> float:
    finite = [v for v in values if v != -math.inf]
    if not finite:
        return -math.inf
    m = max(finite)
    return m + math.log(sum(math.exp(v - m) for v in finite))


def _log_evalue_single(k_s: int, n_s: int, k_c: int, n_c: int, psi: float) -> float:
    """log E_psi(k_s) for one odds ratio (see module docstring)."""
    t = k_s + k_c
    big_n = n_s + n_c
    log_psi = math.log(psi)
    u_min, u_max = max(0, t - n_c), min(t, n_s)
    log_z = _logsumexp(
        [_log_comb(n_s, u) + _log_comb(n_c, t - u) + u * log_psi for u in range(u_min, u_max + 1)]
    )
    return k_s * log_psi + _log_comb(big_n, t) - log_z


def conditional_bernoulli_evalue(
    k_s: int,
    n_s: int,
    k_c: int,
    n_c: int,
    psi_grid: tuple[float, ...] = DEFAULT_PSI_GRID,
    weights: tuple[float, ...] | None = None,
) -> float:
    """Mixture conditional 2×2 e-value for ``p_subject > p_control`` (one-sided).

    ``k_s``/``n_s`` = subject rejects / events; ``k_c``/``n_c`` = control (RW-null). Returns the
    e-value ``E`` (``E[E] = 1`` exactly under H0). ``E >= 1/alpha`` is the anytime-valid rejection
    threshold. Returns ``1.0`` (no evidence) when either side has zero events.
    """
    if not psi_grid:
        raise ValueError("psi_grid must be non-empty")
    for label, k, n in (("subject", k_s, n_s), ("control", k_c, n_c)):
        if n < 0 or k < 0 or k > n:
            raise ValueError(f"{label}: need 0 <= k <= n (got k={k}, n={n})")
    if any(p <= 0 for p in psi_grid):
        raise ValueError("psi values must be > 0")
    if n_s == 0 or n_c == 0:
        return 1.0  # one side has no events → no comparison → no evidence
    if weights is None:
        weights = tuple(1.0 / len(psi_grid) for _ in psi_grid)
    if len(weights) != len(psi_grid):
        raise ValueError("weights must match psi_grid length")
    if any(w < 0 for w in weights) or not math.isclose(sum(weights), 1.0, abs_tol=1e-9):
        raise ValueError("weights must be non-negative and sum to 1")
    log_terms = [
        math.log(w) + _log_evalue_single(k_s, n_s, k_c, n_c, psi)
        for w, psi in zip(weights, psi_grid, strict=True)
        if w > 0
    ]
    return math.exp(_logsumexp(log_terms))


def evalue_to_pvalue(e: float) -> float:
    """Calibrate an e-value to an anytime-valid p-value ``p = min(1, 1/E)`` (Markov / Ville)."""
    if e == math.inf:
        return 0.0
    if e <= 0:
        return 1.0
    return min(1.0, 1.0 / e)


def holm_evalues(evalues: dict[str, float], alpha: float = 0.05) -> dict[str, bool]:
    """e-Holm: calibrate each e-value to ``1/E`` and run the repo's tested Holm-Bonferroni.

    Returns ``{key: significant_bool}`` with family-wise error controlled at ``alpha`` under
    arbitrary dependence across the ``subject × timeframe`` family.
    """
    return _holm({k: evalue_to_pvalue(v) for k, v in evalues.items()}, alpha)
