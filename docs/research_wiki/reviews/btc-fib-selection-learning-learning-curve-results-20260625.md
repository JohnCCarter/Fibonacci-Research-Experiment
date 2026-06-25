# BTC Fib Selection-Learning — learning-curve RESULTS (facit data-sensitivity) (2026-06-25)

Blind Commit-2 execution of the [learning-curve LOCK
(2026-06-25)](btc-fib-selection-learning-learning-curve-lock-20260625.md). Is the current Stage-2
model **data-starved or saturated** w.r.t. facit size? Reuse Stage-2 verbatim, fix the held-out test
set, vary only the training-facit fraction (whole human legs), build-once-vary-labels, R=64, finer
grid near f=1.0. Harness:
[`selection_learning_curve.py`](../../../src/fibengine/research/selection_learning_curve.py) (commit
`c4bd330`); seed `20260618`; frozen-data parity (no `--refresh`); preflight READY before run.
**Diagnostic only — no edge/behaviour/PnL/Genesis claim (LOCK L7); does not resolve the `cleanliness`
crux.**

> **Verdict (blind, 4h primary k=3): `saturated` — but marginally (a knife-edge call).** The OOS-AP
> curve means rise **monotonically across the whole range** (0.0501 → … → 0.0567); the verdict rests
> on a single fact: the **last 5 % increment (+0.0008) falls inside the tightest band, f=0.95 ±0.0030**
> — i.e. the marginal label at full facit adds **within subsample noise**, *not* that the curve has
> flattened. Per the locked ASYMMETRIC rule (L4) this is **ambiguous AND expected**: the Stage-2 model
> is ≈1 effective parameter (`cleanliness`-dominated), so it saturates after a few dozen positives. It
> means **the current 1-feature model is capacity-bound → route to the feature / `cleanliness` crux**,
> **NOT** that growing the facit is pointless.

## Observed (measured — 4h primary, powered: 65 test positives)

**Parity gate:** `ap_full_facit` (f=1.0) = **0.056737** = the Stage-2 headline **0.0567**;
n_test_positives = **65**; n_candidates = **86244** (full universe); n_train_legs = **246** (facit legs
subsamplable in the train period). The f=1.0 point reproduces the current model exactly.

Learning curve (mean pooled test AP over R=64 train-subsamples; f=1.0 is the single full point):

| f | n_retain legs | mean train pos | AP mean | [p5, p95] | AUC |
|---|---|---|---|---|---|
| 0.25 | 62 | 84 | 0.05010 | [0.0319, 0.0664] | 0.913 |
| 0.50 | 123 | 169 | 0.05220 | [0.0419, 0.0618] | 0.913 |
| 0.75 | 184 | 251 | 0.05415 | [0.0485, 0.0604] | 0.914 |
| 0.80 | 197 | 269 | 0.05449 | [0.0461, 0.0603] | 0.914 |
| 0.90 | 221 | 302 | 0.05508 | [0.0491, 0.0583] | 0.914 |
| 0.95 | 234 | 320 | 0.05595 | [0.0529, 0.0589] | 0.914 |
| 1.00 | 246 | 336 | 0.05674 | — | 0.914 |

- **Means rise monotonically across the whole range** — there is **no clean knee/plateau.** Per-leg,
  the top increments are not smaller than the middle: .50→.75 ≈ 0.000033/leg vs .95→1.0 ≈
  0.000066/leg (noisy). The `saturated` label rests *only* on the last 5 % increment (+0.0008) sitting
  inside the tightest (f=0.95) band over a 12-leg lever arm — "marginal label within noise", not "curve
  flattened".
- **Verdict arithmetic (locked rule):** spread of means = 0.00664; f=0.95 band half-width = 0.00299;
  last increment = 0.00078 < band → **not `data_starved`**; band < spread → **not
  `inconclusive_underpowered`** → **`saturated`**.
- **AUC is essentially flat (~0.913–0.914) at every fraction** — ranking separation barely depends on
  facit size; even a quarter of the labels already gives the full ranking quality.

**Context cells (underpowered, never refuted — L2 power floor ≥10 test positives):**

| TF | test pos | AP @0.25 → @1.0 | shape | note |
|---|---|---|---|---|
| 1M | 5 | 0.255 → 0.264 | flat/noisy | 5 legs; bands huge |
| 1w | 0 | — | — | no test positives |
| 1d | 7 | 0.097 → 0.162 | **still rising** | underpowered (7<10) — cannot bear weight |

Context is descriptive only; the verdict rests solely on the 4h powered cell. (The 1d *shape* looks
data-starved, but with 7 test positives it is not interpretable — L2.)

## Inferred (interpretation — not measured)

- **For the current Stage-2 model, the marginal label at full facit adds within-noise on 4h.** The
  curve still rises gently, but the last 5 % of labels move AP by less than the subsample band — so the
  *next* labels are low-leverage for *this* model. (This is **not** "more data won't help this model" —
  a monotone-rising curve does not license that; it is "the marginal gain is within noise at the ceiling
  we are at".)
- **This is the EXPECTED outcome, not a surprise (LOCK L4 asymmetry).** A ≈1-effective-parameter model
  (one feature carries the lift) saturates after a few dozen positives — every fraction from 0.25 up
  (84 train positives) is already in the saturated regime. A flat top therefore says **"this 1-feature
  model is capacity-bound"**, which routes back to the **feature side**: is `cleanliness` a genuine
  signal (the open crux), and is there an orthogonal feature that captures more of the human's judgment?
- **Direct relief for the labeling-cost worry:** you do **not** need to grind out hundreds more 4h
  labels to improve the current model — it is already saturated. The leverage is on the model/feature
  side, not the data side, *for this model*.

## Unverified (open — do not claim past these)

- **The curve speaks only for the current 5-feature, `cleanliness`-dominated model.** It does **not**
  show whether a *richer/higher-capacity* model would be data-starved at this facit size — a
  higher-capacity model could still benefit from more labels even though this one does not. Saturation
  is model-relative.
- **The `cleanliness`-as-genuine-signal crux stays OPEN.** Saturation does not tell us whether the one
  feature the model leans on is human judgment or a detector/anchoring artifact (matched-null, A8, not
  built).
- **Absolute AP stays ~0.057 vs the ~0.83 coverage ceiling** — saturation is at a *low* level: the
  model reproduces little of the human even at full facit. No edge/behaviour/PnL/Genesis/auto-fib claim.
- 1M/1w/1d are **underpowered, not refuted** (1d's rising shape is suggestive but not interpretable).

## Artifacts

- Summary JSON: `experiments/review/fib_selection_learning/curve/summary.json` (**gitignored**).
- Per-cell checkpoints: `experiments/review/fib_selection_learning/curve/cells/*.json` (**gitignored**).
- Harness + tests: `selection_learning_curve.py`,
  `tests/research/test_selection_learning_curve.py` (commit `c4bd330`; gates green).
