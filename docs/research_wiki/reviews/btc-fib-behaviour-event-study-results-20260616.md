# BTC/Fib Behaviour Event Study — Results (2026-06-16)

Run of the pre-registered
[behaviour event study](btc-fib-behaviour-event-study-prereg-20260616.md). Rules were frozen
**before** these numbers. **No trading/edge claim.** No Genesis touch, no 1H, no ML, no label
mutation, no locked-corpus change. Code: `src/fibengine/research/fib_behaviour_event_study.py`
(19 tests). Run artifact (gitignored): `experiments/review/fib_behaviour_event_study/summary.json`.

## Verdict

**Behaviour signal NOT found.** Causal human-fib retracement levels are **not** measurably
different from matched placebo levels or a causal-swing baseline under the pre-registered
criterion. **The strategy sanity-check is therefore NOT authorised and was NOT run** (prereg §9;
Phase 0 §8: "failing to beat the placebo is by itself a stop signal"). Track stops here.

## Setup (as run)

- BTC/USD, timeframes **1M, 1w, 1d, 4h** (1H excluded). Offline cache via
  `settings.expansion.yaml`, `history_start 2016-11-05`. Deterministic, `seed = 20260616`.
- Sources: **FIB** (causal interior retracements), **PLACEBO** (matched count/time, random
  causal-range price), **SWING** (causal fractal high/low). Primary metric **reject_rate** at the
  middle horizon (4h:18, 1d:12, 1w:4, 1M:3). Permutation test, 5000 reshuffles, on the **test**
  window. Time split 70/30 with `max(horizon)` embargo.

## 1. Observed (numbers on disk)

Test-window reject_rate (primary) and permutation p (FIB vs baseline):

| TF | FIB test (N) | PLACEBO test (N) | SWING test (N) | p vs PLACEBO | p vs SWING |
|----|--------------|------------------|----------------|--------------|------------|
| 4h | 0.783 (272) | 0.802 (172) | 0.841 (138) | 0.63 | 0.19 |
| 1d | 0.821 (28) | 0.720 (25) | 0.727 (44) | 0.51 | 0.40 |
| 1w | 0.000 (1) | 0.714 (7) | 0.714 (21) | 0.37 | 0.32 |
| 1M | 0.500 (2) | 0.750 (4) | 0.333 (3) | 1.00 | 1.00 |

- **4h is the only adequately powered TF** (all sources N ≥ 138 in test; ≥ 406 in train). There,
  FIB reject_rate (0.783 test / 0.791 train) ≈ PLACEBO (0.802 / 0.799) ≈ SWING (0.841 / 0.808).
  FIB beats **neither** baseline in **either** window; permutation p = 0.63 / 0.19 (not significant).
- Secondary metrics at 4h test are equally undifferentiated: `close_through` FIB 0.64 / PLACEBO
  0.66 / SWING 0.59; `abs_fwd_move_atr` FIB 2.24 / PLACEBO 2.07 / SWING 2.66.
- **1d** is the only TF where FIB nominally exceeds both baselines (test + train), but it is
  **not significant** (p = 0.51 / 0.40) and **underpowered** (FIB/PLACEBO N < 30 in test).
- **1w / 1M** are too sparse to interpret (FIB test N = 1 and 2).
- Pre-registered gate (`robust_signal`) = **False on every timeframe.**

## 2. Inferred (reasoned from the above)

- At the timeframe with real statistical power (4h), **fib retracement levels behave like random
  matched levels.** Touching a fib level is followed by a ≥ 0.5-ATR bounce ~78 % of the time —
  but so is touching a *random* placebo level (~80 %) or a prior swing (~84 %). The reaction is a
  property of **price touching any horizontal level** (general mean-reversion / noise), not a
  property of *fib* levels. This is the cleanest possible read of the Phase 0 null.
- The 1d nominal ordering is most parsimoniously **sampling noise**: it is not significant, does
  not survive the power floor, and is contradicted by the much larger 4h sample.
- The high reject base-rate (~0.8) means the primary metric has a **ceiling**; but the ceiling
  hits all sources equally, so the *comparison* is still valid — and it shows no separation on the
  primary metric **or** either secondary metric. A more sensitive metric is unlikely to rescue a
  difference this absent at 4h.

## 3. Unverified (open — not settled by this run)

- Whether a **different operationalisation** (e.g. distance-bucketed reaction, direction-
  conditioned outcomes, regime-split, or a tighter touch tolerance) would surface a small effect.
  This run tested **one** pre-registered metric family; it cannot exclude all alternatives.
- Whether fib levels matter on **other symbols / other markets** (only BTC/USD tested).
- Whether **1d** holds any weak effect with a larger 1d sample — current 1d power is insufficient
  to confirm or refute; treat as inconclusive, not as support.
- The study measures **behaviour around levels**, never profit; nothing here speaks to tradeability
  in either direction.

## 4. Answers to the report checklist

- **Did fib beat the baselines?** No. Not on the only powered TF (4h), and not significantly
  anywhere. The one nominal 1d ordering fails significance and the power floor.
- **Number of events:** 4h FIB 788 (516 train / 272 test); 1d 125; 1w 26; 1M 3. Baseline counts
  comparable (see summary.json). Sparsity dominates 1w/1M.
- **Timeframes included:** 1M, 1w, 1d, 4h (no 1H).
- **Baselines used:** causal-swing (naïve analogue) + deterministic matched placebo.
- **Robust or weak:** Not robust — fails the pre-registered gate on every TF; the powered TF is a
  clean null.
- **Strategy sanity-check:** **Not authorised → not run.** (Gate failed.)
- **Trading claim:** none made.

## 5. Decision

**Stop.** Under Lean Fib Research, a test that does not beat its baselines ends the line: no
strategy sanity-check, no further parameter variants chased on the same data (that would be
p-hacking). The corpus, prereg, code and this report are durable. Any *future* attempt must be a
**new pre-registration** with a different question or metric — not a re-run of this one until it
passes. No Genesis, no 1H, no export, no optimisation were touched.
