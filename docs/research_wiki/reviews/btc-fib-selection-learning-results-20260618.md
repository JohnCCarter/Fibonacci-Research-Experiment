# BTC Fib Selection-Learning — Stage 2 Headline RUN (2026-06-18)

**Lean Fib Research. Research-only. Selection learning — NOT a behaviour/edge claim, no
backtest/PnL, no Genesis, no auto-fib-as-truth, no label mutation.** This reports the **first run**
of the pre-registered **Stage 2 headline cell** (live-equivalent viewport, primary `k = 3`), built
per the [prereg](btc-fib-selection-learning-prereg-20260617.md) +
[§12 addendum](btc-fib-selection-learning-addendum-20260618.md) (metric pinned A5.1, blind).

> **STATUS: POINT ESTIMATE — inference PENDING. This is NOT a confirmed result.** The harness
> reports the AP point estimate and a `lift_pos_powered` flag (= `lift > 0` on a powered cell), which
> is **not** a significance test. No CI / p-value on the AP-lift exists yet. Do **not** read "the
> model beats baseline" as established until the inference step (below) is done.

## What was built + run

`src/fibengine/research/selection_learning.py` (+ 15 tests). Stage 2 only: candidate legs from
`detect_pivots` + opposite-pivot pairing; **causal** features computed on a frame **truncated at
`anchor_b + k`** with the live `k*≤3` whitelist (`{magnitude, cleanliness, duration, prominence,
structure_alignment}`); the candidate universe re-detected on the truncated frame; ε-matching to
human legs (`time_tol=3` bars, `price_tol=0.5` ATR, A4); purged/embargoed split on `anchor_b` chart
time (embargo = forward reach `k`); interpretable ridge logistic regression (numpy, deterministic,
zero new deps); **baseline parity** = same test set/viewport, ranked by `magnitude` alone (§6).
Primary metric = pooled test **Average Precision** (A5.1); ROC-AUC secondary.

Run: `--timeframes 1M,1w,1d,4h --config config/settings.expansion.yaml`, seed 20260618.

## Results (point estimates)

| TF | human legs | coverage | n_test cands | test pos | AP model | AP base | AP lift | AUC (2nd) | powered (≥10) |
|----|-----------:|---------:|-------------:|---------:|---------:|--------:|--------:|----------:|:-------------:|
| 1M | 9 | 1.00 | 132 | 5 | 0.264 | 0.047 | +0.216 | 0.883 | no |
| 1w | 21 | 0.857 | 768 | 0 | — | — | — | — | no |
| 1d | 67 | 0.896 | 4 140 | 7 | 0.162 | 0.003 | +0.159 | 0.908 | no |
| **4h** | **365** | **0.830** | **24 852** | **65** | **0.057** | **0.005** | **+0.052** | **0.914** | **yes** |

- **Only 4h is powered** (65 test positives; 1M/1d thin, 1w has 0 test positives after the
  purged split — mirrors B-1, where only 4h/1d cleared the power floor).
- On 4h the positive base rate is ≈ `65 / 24 852 ≈ 0.0026`. Baseline AP `0.0051` ≈ 2× base rate
  (magnitude alone is weak); model AP `0.057` ≈ **22× base rate, ≈ 11× baseline**.
- **Secondary AUC ≈ 0.88–0.91 on every TF with positives** — the most consistent signal: the
  ranking separates human-matched legs from the rest far above chance (0.5) across 1M/1d/4h.

## Observed / Inferred / Unverified

- **Observed (from the run, verified):** the point-estimate numbers above; coverage 0.83–1.0;
  features used; pipeline runs end-to-end and is causal (truncated-frame features + re-detected
  candidate universe). 15 unit tests green (provenance whitelist, purge window, AP/AUC, logreg
  determinism, ε-match, synthetic causal build).
- **Inferred:** the model's input features carry information about the human's leg choice beyond
  raw magnitude (consistent AUC≈0.9, large relative AP lift). The 4h cell is the only adequately
  powered headline.
- **Unverified (the gap — do not claim past this):** **statistical significance** of the AP-lift.
  No CI / p-value yet; `lift_pos_powered` is a point-estimate flag, not a verdict. AP absolute
  values are low (rare-positive task, capped by the 0.83 coverage ceiling) and must be read against
  base rate, not 1.0. Multiplicity across TFs not yet applied (only one powered cell, but the
  inference must still be pre-correction-aware).

## Immediate next step (pending the user's go — still Lean, still gated)

1. **Inference on the AP-lift (4h headline):** add a CI / one-sided p-value on
   `AP_model − AP_base`, **resampled by decision point (`anchor_b` group)** to respect candidate
   clustering — independent row bootstrap would understate variance. Null = lift ≤ 0. This turns
   the 4h point estimate into a confirmed result **or** a null. *Only then* does a finding exist.
2. Then bolt on the secondary cells (addendum A5): the `k`-sweep {0,3,6,12} + retrospective `W`
   model → the per-feature **causal-availability gap**; the **Stage-1** per-pivot diagnostic; the
   set-level **exclusivity** output diagnostic (A3).

## Discipline honoured

No edge/behaviour claim, no backtest/PnL, no Genesis, no 1H, no auto-fib-as-truth, no label/corpus
mutation, no tuning on test (all knobs frozen pre-run in the addendum). Artifacts
(`experiments/review/fib_selection_learning/summary.json`) are **gitignored**, regenerable.

> Point estimate only. A confirmed finding requires the inference step above.
