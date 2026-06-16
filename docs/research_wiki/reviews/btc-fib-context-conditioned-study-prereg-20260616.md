# BTC/Fib Context-Conditioned Study — Pre-registration (2026-06-16)

**Lean Fib Research, second falsifiable question.** Rules frozen **before** the confirmatory
results. Follows the
[behaviour event study](btc-fib-behaviour-event-study-results-20260616.md) which found **no
unconditioned signal**. New question — not a re-run:

> Does BTC/USD price react differently at fib levels **than at matched placebo/swing levels —
> but only within specific, causally-knowable market contexts** (where fib theory predicts it
> should)?

Null: no context shows a fib-over-baseline reaction difference surviving the pre-registered gate.
**Not** Fib → Genesis, **not** Phase 3. No Genesis touch/import/export, no 1H, no ML/optimisation,
no trading/edge claim, no label/corpus mutation.

## 0. Honesty disclosures (binding)

- **This is a second look at the same OOS window.** Events, placebo (seed 20260616), swing, and
  the 70/30 split are **reused unchanged** from the prior study; only the conditioning dimension
  is new. A power **pre-flight inspected test-window cell sizes and effect gaps**. Therefore the
  test-window p-values are **not a clean first look** — the **train/test sign-consistency** check
  is the real guard, and a positive can only become a **candidate**, never a confirmed effect.
- **Confirmation requires fresh data** (other symbols/timeframes), which is **out of scope** here.
  Best achievable outcome of this pass = a pre-registered candidate for a *future* fresh-data test.
- **Multiple-comparison control:** exactly **K = 2** confirmatory contexts, Holm-corrected.

## 1. Primary metric (continuous — fixes the prior ceiling)

The prior `reject_rate` was saturated (~0.8 across all sources) → too coarse to survive
conditioning. Primary metric here is **continuous**:

```
reaction_asym_atr = MFE_atr - MAE_atr   (in the rejection/approach-defined direction)
```

Positive ⇒ the level repelled price (support held / resistance held) net of adverse excursion.
Tested with a **rank-based permutation test** (5000 reshuffles, seed 20260616) — robust to the
fat tails of ATR excursions. Secondary descriptive: `reject_rate`, `close_through_rate`,
`abs_fwd_move_atr`. Confirmatory horizon = middle horizon per TF (4h: 18).

## 2. Pre-registered MDE (so a null is interpretable)

For a continuous metric with SD `s`, per-window `n`/arm, two-sided α and power 0.8, the minimum
detectable mean gap is `MDE ≈ (z_{1-α/2} + 0.84)·s·√(2/n)`. With observed `s ≈ 3.6–4.5 ATR` and
conditioned `n ≈ 60–350`/arm at Holm-top α = 0.025, **MDE ≈ 1.3–2.0 ATR**. The plausible effect
(pre-flight) is **~0.5 ATR**. So a single OOS window is **underpowered to confirm** such an
effect; a null means "no effect **larger than ~1.5 ATR**," not "no effect." This is why
sign-consistency (train **and** test) gates a *candidate*, and confirmation is deferred to fresh
data. Stated up front, not after.

## 3. Confirmatory contexts (K = 2, frozen — chosen on prior + power, not on observed gaps)

Both keep **both arms ≥ 30** events in the test window (the criterion that excluded first-touch,
whose placebo arm collapses to N≈19):

1. **Trend regime** — fib is a *trend-pullback* tool; predict fib works in trend, not range.
   Causal flag at bar `t`: `|mean(log-return) over L=50 bars|` **above** its **causal trailing
   rolling median** (window `W=500`, min-periods `L`) of the same quantity. Predicted cell:
   **in-trend**. (`L=50`, `W=500`, statistic, threshold all frozen; rolling/trailing only.)
2. **Deep retracement** — golden-ratio prior. Fib levels from ratios **{0.618, 0.786}** vs the
   full placebo set (placebo has no depth → not fragmented). Predicted cell: **deep**.

## 4. Exploratory contexts (descriptive only — CANNOT set the verdict)

First-touch vs later (control arm underpowered, N≈19), range, shallow {0.382,0.5}, volatility
regime (rolling ATR percentile). Reported for completeness; never upgrade the verdict.

## 5. Baselines & causality (reused, unchanged)

- **PLACEBO** (matched count/time, random causal-range price, seed 20260616) and **SWING** (causal
  fractal high/low) from the prior study. All level knowability obeys
  `known_after_ts = max(anchor_a,anchor_b) + 1 bar`; recency window per TF; `_events.json`
  auto-candidate sidecars excluded; non-human fibs rejected fail-closed. Context flags are
  **causal at `t`** (rolling/expanding only, no full-sample statistics). Fail-closed on 1H, empty
  input, naive timestamps, or a context flag that needs future data.

## 6. OOS & statistics

- Same **time-ordered 70/30** split + `max(horizon)` embargo as the prior study (reused).
- Confirmatory TF = **4h** (only adequately powered). **1d descriptive**; **1w/1M skipped**
  (N ≤ 2 last time).
- Per confirmatory context: N, mean & median `reaction_asym_atr` for FIB / PLACEBO / SWING in the
  predicted cell, per window; rank-permutation p (FIB vs PLACEBO, FIB vs SWING) on the **test**
  window; **Holm** across the K = 2 FIB-vs-PLACEBO tests (top α = 0.025).

## 7. Gate per confirmatory context (stop/go)

A context is a **candidate** iff **all** hold:

1. `N ≥ 30` for FIB and the comparison arm in the predicted cell, **test** window.
2. FIB mean `reaction_asym_atr` **>** PLACEBO **and >** SWING in the predicted cell (test).
3. Holm-adjusted permutation `p < 0.05` for FIB-vs-PLACEBO (test).
4. **Same sign** (FIB − PLACEBO > 0) in the **train** window too.

## 8. Verdict discipline (binding)

- The verdict is set **only** by the K = 2 confirmatory tests. Exploratory contexts, secondary
  metrics, 1d, and non-primary horizons are **descriptive and cannot upgrade** it.
- **Possible verdicts:** (a) **no context passes** → fib is not rescued by context → **stop**, no
  strategy work; (b) **one+ context passes** → **candidate(s)** flagged for a *future* fresh-data
  test — **not** a confirmed effect, **no** strategy sanity-check authorised by this pass alone.
- No chasing: contexts/params are frozen here; if none passes we do **not** retune and re-run.

## 9. Non-goals honoured

No Genesis touch/import/export, no 1H, no ML/Optuna/optimisation, no tuning on test, no
live/paper trading, no exchange, no label/corpus mutation, no large binaries, no "Phase 3". If a
step needs any of these → **pause and report**.
