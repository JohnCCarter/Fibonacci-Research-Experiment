# BTC Fib Selection-Learning — learning-curve LOCK (facit data-sensitivity) (2026-06-25)

**DOCS-ONLY. Diagnostic — no claim, no code, no run, no build, no dependency, no new universe, no
label/corpus change, no push.** Lean **blind Commit-1 lock** for one cheap learning-curve shot: is the
Stage-2 selection model **data-starved or saturated** w.r.t. facit size? Reuses Stage-2 verbatim; only
the **training-facit fraction** varies. Execution needs a **separate explicit GO** (Commit 2).

**Blindness:** no learning-curve harness exists; **no AP at any fraction has been computed or seen.**
Every rule below is fixed from the [Stage-2 headline](btc-fib-selection-learning-results-20260618.md),
the frozen config, and existing code — not from any learning-curve result.

> **Honest framing:** this answers *"would more human-labeled 4h legs plausibly raise OOS AP?"* — a
> **data-sensitivity diagnostic**, step toward the [north star](../north-star.md) step 1. It is **not**
> a headline, adds **no** positive claim, and does **not** resolve the `cleanliness` crux.

## L1. Question

> **Is the current Stage-2 model data-starved (OOS-AP curve still rising at full facit) or saturated
> (flat) as a function of training-facit size, on the 4h primary at k=3?**

## L2. Mechanics (reuse Stage-2 verbatim — locked)

- **Cell = 4h primary, k=3.** `build_candidates`, ε-match, purged/embargoed split, `fit_logreg` (the 5
  live features), pooled test **Average Precision**, decision-point cluster bootstrap — all **verbatim**
  from the Stage-2 headline. Frozen data (no `--refresh`).
- **FIXED test set = the Stage-2 held-out split** (65 positives / 24 852 candidates). **Never
  subsampled** → AP is comparable across all fractions.
- **Vary ONLY the training facit:** drop **whole human legs** whose `anchor_b` ∈ the train period; a
  training candidate is positive iff it ε-matches a **retained** human leg. The candidate universe and
  the features are **unchanged** — only which training rows are labeled positive shrinks.
- **Subsample unit = whole human legs** (the unit you would actually add when "growing facit"), uniform
  random **without replacement**.

## L3. Grid + repeats (locked)

- **Fractions** `f ∈ {0.25, 0.50, 0.75, 0.80, 0.90, 0.95, 1.00}` — finer near the top, because the
  **local slope at f=1.0** is what speaks to "would the *next* labels help".
- **R = 64** independent subsamples per fraction (`f=1.0` is the single full-facit point). Seeds =
  `20260618 + fraction_index*1000 + repeat_index`. Report **mean AP + [p5, p95] band** per fraction;
  ROC-AUC secondary (same shape check).
- **BUILD ONCE (build-time requirement):** the universe, features, and per-candidate ε-match are
  computed **once**; per `(f, r)` only **relabel train + refit logreg + recompute test AP** (all cheap).
  If the harness rebuilds the universe per fraction the cost argument collapses — it must not.

## L4. Verdict (pre-stated, ASYMMETRIC — fixed blind)

The Stage-2 lift is carried almost entirely by **one** feature (`cleanliness` ~0.20; the rest ≈ 0) →
**≈ 1 effective parameter → saturation is the EXPECTED default** and must not be over-read.

- **`data_starved`** — mean `AP(1.0) − AP(0.95)` **exceeds the f=0.95 band half-width** (the last
  increment moves AP beyond train-subsample noise) and the curve is increasing: **genuinely informative,
  strong green light** — more facit helps *even this model*.
- **`saturated`** — the last increment is **within** the band (flat): **ambiguous AND expected.** It
  means the **current 1-feature set is capacity-bound**, **NOT** that facit is big enough or that
  labeling is pointless. Routes back to the **feature / `cleanliness` crux** (matched-null), **not** away
  from labeling.
- **`inconclusive_underpowered`** — bands overlap heavily across fractions (a **live, LIKELY** outcome
  with 65 test positives): **no verdict.** A within-band wiggle is not a result.

## L5. Variance naming (locked)

The R-band = train-side **"which legs were dropped"** variance. `AP(1.0)` is a single point (no
train-subsample variance) but still carries **test-side noise from 65 positives** — shared across
fractions, so it **partly cancels in fraction differences**. The verdict reads **differences**, not
absolute levels.

## L6. Addable-supply context (reported, not a gate)

Report alongside the verdict: **labeled human legs (365)** vs the detector's **candidate universe
(~86 244)** on frozen 4h, and the **bounded** nature of addable supply (true human-meaningful count is
unknown without a human pass and is capped by available history). **If `data_starved` BUT little
human-meaningful 4h history remains, the route is more history / symbols (a protocol change), not
grinding the same chart** — this directly informs the "it takes forever" cost.

## L7. Non-claims (binding)

Diagnostic of **data-sensitivity only**. **No edge / behaviour / PnL / backtest / Genesis /
auto-fib-as-truth.** Does **not** resolve the `cleanliness` crux — a rising curve means more data
improves human-selection reproduction **regardless** of whether `cleanliness` is judgment or artifact.
Frozen data, no `--refresh`, **4h primary only powered**; 1M/1w/1d are **context, never refuted**.

## L8. Implementation (Commit 2 — NOT executed here)

- **New module `src/fibengine/research/selection_learning_curve.py`** with its **own CLI**; **no code
  added to byte-capped `selection_learning.py`**. Reuses `build_candidates`, `fit_logreg`,
  `predict_proba`, `average_precision`, `roc_auc`, the decision-point machinery, `window_of`, ε, and the
  `FROZEN_SNAPSHOT` preflight; **build-once-vary-labels** per L3.
- **Tests** `tests/research/test_selection_learning_curve.py`: fixed-test-set invariance, subsample
  unit = whole legs, **build-once** (features identical across fractions), verdict branches incl. the
  L4 asymmetry + `inconclusive`, seed determinism.
- **Results doc** later (Observed / Inferred / Unverified). Artifacts under
  `experiments/review/fib_selection_learning/curve/` (**gitignored**). **Preflight FIRST**, frozen-data
  parity. **Separate explicit GO before any build/run.**
