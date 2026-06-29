# Anytime-valid inference: e-values + e-Holm

**Query this before re-deriving the sequential-testing math.** Code:
[`src/fibengine/research/anytime_valid.py`](../../../src/fibengine/research/anytime_valid.py)
(SENARE-1). Pinned in the
[B-1 prereg §8](../reviews/btc-horizontal-structure-event-study-prereg-20260617.md).

## When and why

A fresh fixed-horizon permutation p-value is **invalid** when the same OOS window is looked at more
than once (optional stopping / peeking). When a re-look is genuinely warranted, use **anytime-valid
inference**: an **e-value** stays valid under continuous monitoring / optional continuation. See the
standing [addendum NU-2](../reviews/horizontal-structure-prereg-addendum-20260617.md).

## The construction we use (pinned, blind to outcome)

The **conditional 2×2 / Fisher noncentral-hypergeometric e-value** for a two-sample Bernoulli
comparison (subject reject-rate vs a control reject-rate):

- Condition on the total reject count `t = k_s + k_c`. Under H0 (`p_subject = p_control`) the
  conditional law of `k_s` is the central hypergeometric — **free of the nuisance base-rate** — so
  `E[E] = 1` holds **exactly at every N**, not asymptotically. This matters because the hardest TFs
  often have N < 30 (where a two-sample mSPRT's normal approximation would drift).
- For odds-ratio `ψ`: `E_ψ(k_s) = ψ^k_s · C(N,t) / Z(ψ)`, `Z(ψ) = Σ_u C(n_s,u)C(n_c,t-u)ψ^u`.
  By Vandermonde, `E[E_ψ | t] = 1` exactly. Validity holds for **any prior over ψ**, so the
  pre-registered grid (`ψ ∈ {1.5, 2, 3}`) affects **power only, never Type-I**.
- Calibrate `p = min(1, 1/E)` (Markov / Ville) and feed into the repo's existing tested
  Holm-Bonferroni (`fib_context_conditioned_study._holm`) = **e-Holm** across the family. `E ≥ 1/α`
  is the anytime-valid rejection threshold.

## Ship-gate (the math is the deliverable, not "no crash")

Verify by the **exact** identity `Σ_x P0(x)·E(x) = 1` to ~1e-9 at small **and** large N
(deterministic, no Monte-Carlo noise), plus the tail-robust Ville check `P(E ≥ 1/α) ≤ α`. The
e-value is heavy-tailed, so its sample mean converges slowly — prove validity by the identity, not
by averaging. Tests: `tests/research/test_anytime_valid.py`.

## Power caveat (learned on B-1)

e-Holm across a 12-cell family needed the top `E ≈ 1/(α/12) ≈ 240` to reject; B-1's observed max was
1.70. Report a **multiplicity-aware power ceiling** so a null reads as "no detectable signal, limited
power for a subtle one," not "definitively no effect."

## Sources

[methodology-anchors.md](../sources/methodology-anchors.md) (Johari–Pekelis–Walsh; Grünwald–de
Heide–Koolen safe testing; Turner–Ly–Grünwald 2×2). [Source authority](../reference/source-authority.md):
code + prereg win over this synthesis page.
