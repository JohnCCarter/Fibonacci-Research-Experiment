# BTC Horizontal-Structure Event Study — Results (2026-06-17)

**Result: NULL.** No generic horizontal-structure subject (SWING, ROUND, PRIOR-EXTREME) repels
BTC/USD measurably more than a matched random-walk null on the pre-registered anytime-valid test.
`any_robust = False` across all 12 subject × timeframe cells. The §10 strategy sanity-check was
**not authorised and not run.** **No trading/edge claim.**

Pre-registration (frozen, incl. the dated §3/§4/§8 amendments):
[prereg](btc-horizontal-structure-event-study-prereg-20260617.md). Run: seed `20260616`, BTC/USD,
TFs 1M/1w/1d/4h, cached candles via `config/settings.expansion.yaml`, no network, **no fib JSON
read**. Inference: conditional 2×2 e-value (SENARE-1) per subject vs its RW-null on test-window
`reject` counts, e-Holm across the family (prereg §8 amendment). Artifact (gitignored):
`experiments/review/horizontal_structure_event_study/summary.json`.

## Observed (verified from the run)

**Powered cells** (the prereg §9 floor: `N ≥ 30` for the subject **and** its RW-null in the test
window). Primary metric = `reject_rate` (direction-agnostic repulsion); e-value tests
subject > RW-null.

| subject · TF | subj reject (N) | RW-null reject (N) | beats RW-null? | e-value | p (anytime-valid) |
|---|---|---|---|---|---|
| swing · 4h | 0.841 (138) | 0.780 (322) | yes | **1.70** | 0.590 |
| prior_extreme · 4h | 0.767 (86) | 0.817 (153) | no | 0.061 | 1.0 |
| round · 4h | 0.757 (37) | 0.756 (86) | no (tie) | 0.368 | 1.0 |
| swing · 1d | 0.727 (44) | 0.698 (86) | yes | 0.468 | 1.0 |

**Underpowered cells** (`N < 30` on at least one side in test — reported descriptively, **cannot**
satisfy the gate per §9): all of 1M and 1w (test N from 0 to 21), plus `prior_extreme · 1d`
(subj N=21) and `round · 1d` (subj N=20). At 1M, PRIOR-EXTREME and the subject/RW-null had **zero**
qualifying test events (sparse top-of-ladder data).

**Gate:** every cell `robust = False`. `e_holm_significant = False` everywhere. The single e-value
above 1 (swing · 4h, 1.70 → p 0.59) is **far** from the e-Holm threshold; every other e-value is
≤ 1 (the RW-null reacted as much or more).

**Reject rates cluster ~0.70–0.84 across *all* sources** — subjects and the random-walk null
alike — at the powered TFs. High repulsion is not specific to any structure type.

## Inferred (interpretation, not measured)

- The only directional edge is **SWING** (4h: 0.841 vs 0.780; 1d: 0.727 vs 0.698; same-sign in
  train both TFs), but it is **tiny and statistically indistinguishable** from the random-walk null
  under anytime-valid inference — exactly the outcome a spontaneous-RW-structure explanation
  predicts (Lo, Mamaysky & Wang 2000). ROUND and PRIOR-EXTREME do not even beat the null directionally.
  The strongest cell (swing · 4h) is only ~1.5σ over the conditional null mean (e=1.70, one-sided
  p≈0.59) — **no cell was even individually marginally significant**, before any multiplicity
  correction. The near-null swing-1d e-value (0.468) is internally consistent: observed
  k_subject=32 against an expected ~31.1 under the conditional null, so the raw rate gap is an
  unequal-N artefact, not evidence.
- This **extends the closed fib-null**: the prior line showed fib is not special vs a causal swing
  baseline; B-1 shows generic structure (swing / round numbers / prior-period extremes) is **not
  special vs a random walk** either. The ~0.8 reject common to every source = generic
  mean-reversion / levels a random walk produces by itself, not a tradable mechanism.

## Unverified / out of scope

- **Power (honest ceiling, cf. the context-conditioned study's MDE discipline):** at these N and
  the `ψ ∈ {1.5,2,3}` grid, e-Holm across 12 cells needed the top e-value `E ≈ 1/(0.05/12) ≈ 240`
  to initiate any rejection; the observed maximum was 1.70 (~140× short). So the study had
  **low power for a subtle effect** — this is "no detectable signal, with limited power to detect a
  small one," **not** "structure definitively does not repel BTC." A fresh-data or single-subject
  (lower-multiplicity) design would discriminate a subtle effect far better.
- Whether a **different** structure family, regime conditioning, or a fresh post-2026-06-05 window
  would behave differently — not tested here; would require a **new prereg on fresh data** (the
  anytime-valid machinery already legitimised this 3rd look; it does not license parameter-hunting
  on the closed null).
- The underpowered 1M/1w cells say nothing either way (insufficient N), not "no effect."

## Decision

Gate fails on every subject × TF → **stop. No strategy sanity-check** (prereg §9/§10). B-1 closes
**NULL**, consistent with and extending the closed BTC/Fib behaviour line. Per the standing
addendum, a passing cell would have been "a candidate for fresh-data testing, never a confirmation";
no cell passed. No Genesis touch, no 1H, no label/corpus mutation, no trading claim.
