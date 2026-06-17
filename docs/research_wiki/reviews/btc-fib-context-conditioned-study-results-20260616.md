# BTC/Fib Context-Conditioned Study — Results (2026-06-16)

Run of the pre-registered
[context-conditioned study](btc-fib-context-conditioned-study-prereg-20260616.md). Rules frozen
**before** these numbers. **No trading/edge claim.** No Genesis touch, no 1H, no ML, no label
mutation. Code: `src/fibengine/research/fib_context_conditioned_study.py` (17 tests, reuses the
event-study engine). Run artifact (gitignored):
`experiments/review/fib_context_conditioned_study/summary.json`.

## Verdict

**No confirmatory context passes the pre-registered gate** (`any_candidate_confirmatory = False`).
Fib levels are **not** rescued by context: in the predicted cells they beat the *random placebo*
only nominally (and fail multiple-comparison correction), and they **do not beat the naïve
causal-swing baseline at all**. **No candidate → stop. No strategy work authorised.**

## Setup (as run)

- Continuous primary metric `reaction_asym_atr = MFE − MAE` (positive = level repelled price),
  rank permutation test (5000, seed 20260616), **Holm** across the K=2 FIB-vs-PLACEBO tests.
- Confirmatory contexts: **trend regime** (in-trend cell) and **deep retracement** (0.618/0.786 vs
  full placebo). Confirmatory TF **4h**; 1d descriptive; 1w/1M skipped. Same frozen
  events/placebo/swing and 70/30+embargo OOS as the prior study.
- **Disclosure (binding):** this reuses the same OOS window already seen once, and a power
  pre-flight inspected test-window cells. So test p-values are a **second look** — the train-sign
  check is the real guard, and the ceiling for this pass is "candidate," never "confirmed."

## 1. Observed (4h, the only powered TF)

| Context (predicted cell) | FIB mean (N) | PLACEBO mean (N) | SWING mean (N) | p vs PLACEBO | Holm sig | MDE |
|--------------------------|--------------|------------------|----------------|--------------|----------|-----|
| **trend** (in-trend) | −0.236 (146) | −0.879 (78) | −0.105 (107) | 0.042 | **no** | 1.86 |
| **deep** (0.618/0.786) | +0.028 (346) | −0.428 (172) | +0.206 (138) | 0.056 | **no** | 1.33 |

(`reaction_asym_atr`, primary horizon 18 bars. MDE = pre-registered min detectable gap in ATR.)

- **FIB > PLACEBO in the predicted direction** in both contexts (gaps +0.64 and +0.46 ATR), with
  **consistent positive sign in the train window** (trend: fib +0.238 vs placebo −0.265; deep: fib
  +0.239 vs placebo −0.185). Nominal p = 0.042 / 0.056.
- **But FIB does NOT beat SWING:** swing mean (−0.105 trend, +0.206 deep) is **higher** than fib
  (−0.236, +0.028). `fib_beats_both_test = False` in both. The naïve prior-swing-high/low level
  reacts at least as strongly as the fib level.
- **Holm correction kills the placebo edge anyway:** the smaller p (trend 0.042) needs ≤ 0.025;
  neither survives.
- Observed gaps (~0.5 ATR) are **well below the MDE** (1.3–1.9 ATR) → a single OOS window is
  underpowered to confirm an effect this size even if real (as pre-registered).

## 2. Observed (1d, descriptive — underpowered)

- trend: fib +0.530 (N=14) > placebo +0.040 (N=11) but `N < 30`, p = 0.89, and the **train sign
  flips negative** → noise. deep: fib +0.570 (N=33) > placebo −0.020 (N=25), p = 0.49, train sign
  also negative. Neither is interpretable. Cannot set the verdict (descriptive only).

## 3. Inferred

- **The conditional fib-over-placebo pattern is faint and not robust.** It points the predicted
  way (fib repels price a little more than a random level, in trend and at deep ratios, sign-stable
  across train/test vs placebo), but it (a) fails Holm, (b) is dwarfed by its own noise (gap ≪
  MDE), and (c) **vanishes against the swing baseline** — the honest analogue is as good or better.
- **The swing-baseline result is the substantive finding:** whatever mild "levels repel price"
  effect exists in trend/deep cells is a property of *horizontal structure in general* (prior
  swing highs/lows capture it at least as well), **not** of Fibonacci geometry specifically. This
  is consistent with, and reinforces, the unconditioned null.

## 4. Unverified (open)

- Whether a **fresh-data** test (other symbols/timeframes — out of scope) would confirm even the
  faint fib-vs-placebo lean. This pass cannot, by design.
- Whether **other contexts** (HTF confluence, first-touch with a larger corpus, regime
  combinations) behave differently. First-touch could not be tested here (placebo cell N≈19).
- Nothing here measures profit; no tradeability claim in either direction.

## 5. Answers to the checklist

- **Did fib beat the baselines, conditionally?** No. It beat *random placebo* only nominally
  (fails Holm) and **never beat the swing baseline**. Gate fails on both contexts.
- **Events (4h test):** trend fib 146 / plc 78 / swing 107; deep fib 346 / plc 172 / swing 138.
- **Contexts:** confirmatory trend + deep (4h); exploratory first-touch/range/shallow/vol
  (descriptive). **TFs:** 4h confirmatory, 1d descriptive.
- **Robust or weak:** not robust — no candidate; the only directional hint is sub-MDE, Holm-killed,
  and beaten by swing.
- **Strategy sanity-check:** **not authorised, not run.**
- **Trading claim:** none.

## 6. Decision

**Stop.** Two pre-registered questions (unconditioned + context-conditioned) now both return no
usable fib-specific signal, and the naïve swing baseline matches or beats fib. Under Lean Fib
Research this closes the "does fib price-behaviour beat baselines" line on the current BTC corpus.
Re-running with new contexts/params on the *same* data would be p-hacking; any further attempt
must be a **new pre-registration**, ideally on **fresh data** (other symbols/timeframes — out of
current scope). No Genesis, no 1H, no export, no optimisation touched.
