# BTC Fib Selection-Learning — Stage 2 Headline RUN (2026-06-18)

**Lean Fib Research. Research-only. Selection learning — NOT a behaviour/edge claim, no
backtest/PnL, no Genesis, no auto-fib-as-truth, no label mutation.** This reports the **first run**
of the pre-registered **Stage 2 headline cell** (live-equivalent viewport, primary `k = 3`), built
per the [prereg](btc-fib-selection-learning-prereg-20260617.md) +
[§12 addendum](btc-fib-selection-learning-addendum-20260618.md) (metric pinned A5.1, blind).

> **STATUS (updated 2026-06-18, inference slice done): a MODEST, largely single-feature lead on
> the one powered cell (4h) — not a reproduction of human selection.** The 4h AP-lift over the
> **magnitude** baseline is robustly positive out-of-sample (decision-point bootstrap 95% CI
> `[0.023, 0.120]` excludes 0; 0/2000 resamples ≤ 0). But reading the interpretable weights (§10),
> the lift is carried **almost entirely by `cleanliness`** (standardized weight 0.20 vs prominence
> 0.07, structure_alignment ≈ 0) — a single coherent correlate (human-marked legs are *cleaner/more
> efficient* than magnitude alone predicts), **not** a rich multi-feature reproduction. It beats the
> **magnitude** baseline only; the §6 **most-prominent** baseline is untested (next sensitivity).
> Absolute AP 0.057 against a 0.83 coverage ceiling = low agreement; **the human is not
> "reproduced".** 1M/1w/1d are **underpowered, not refuted**.

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

## AP-lift inference (4h, done 2026-06-18)

**Method (pre-declared in the prior commit before computing the p):** decision-point cluster
bootstrap — resample whole `anchor_b` groups with replacement (2071 groups), re-pool their
candidates, recompute `AP(model) − AP(magnitude)` on the **held-fixed** trained model (no refit; this
measures the OOS test-estimate's sampling variability), 2000 resamples, seed 20260618. Row-level
bootstrap would understate variance because candidates cluster by decision point.

- **Lift (test point estimate) = +0.0516**; bootstrap mean +0.0592.
- **95% CI = [0.0234, 0.1197] — excludes 0**; `p_one_sided(lift ≤ 0) = 0/2000`.
- **Read this as a bootstrap-stability statement** (the lift is robustly > 0 across decision-point
  resamples), **not** a permutation-null p-value (it is not "p<0.0005 under H₀ of no association").

### Learned weights (§10 interpretability — read before claiming)

Standardized logistic weights (4h): `cleanliness 0.203`, `prominence 0.071`, `duration −0.040`,
`magnitude 0.013`, `structure_alignment −0.002`. **`cleanliness` dominates (~3× the next term);
`structure_alignment` ≈ 0.** So the lift over magnitude is a **single coherent correlate** — human
legs are *cleaner / more efficient* (net move ÷ path) than magnitude alone predicts — **not** a
multi-feature "reproduction of human selection."

## Observed / Inferred / Unverified

- **Observed (verified):** the numbers above; the 4h AP-lift is robustly positive vs the magnitude
  baseline (CI excludes 0); `cleanliness` carries the lift; pipeline causal; 18 unit tests green.
- **Inferred:** beyond leg size, the human's leg choice on 4h tracks **leg cleanliness/efficiency**
  out-of-sample. 4h is the only adequately powered cell.
- **Unverified / scope limits (do not claim past these):**
  1. **Beats the *magnitude* baseline only.** The §6 alternative **most-prominent** baseline is
     untested — and since `prominence` carries some model weight, the lift could shrink against it.
     This is the obvious next sensitivity.
  2. **Largely a single feature** (`cleanliness`) → a lead, not a structural confirmation; could be
     a mechanical correlate of how clean legs are detected/anchored.
  3. **Low absolute agreement** (AP 0.057, capped by the 0.83 coverage ceiling) — the human is
     **not** reproduced.
  4. 1M/1w/1d are **underpowered, not refuted.**

## This slice is complete — next steps (NONE started; each needs a separate go)

- **(Recommended next)** prominence-baseline sensitivity: re-instantiate the §6 baseline as
  most-prominent and re-test the 4h lift — does the cleanliness-driven lift survive a stronger rule?
- Later (addendum A5, separately gated): `k`-sweep {0,3,6,12} + retrospective `W` → causal-
  availability gap; **Stage-1** per-pivot diagnostic; set-level **exclusivity** output diagnostic.

## Discipline honoured

No edge/behaviour claim, no backtest/PnL, no Genesis, no 1H, no auto-fib-as-truth, no label/corpus
mutation, no tuning on test (all knobs frozen pre-run in the addendum). Artifacts
(`experiments/review/fib_selection_learning/summary.json`) are **gitignored**, regenerable.

> A modest, largely single-feature (cleanliness) lead on one powered cell — statistically robust
> vs the magnitude baseline, but not a reproduction of human selection and untested vs prominence.
