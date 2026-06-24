# BTC Fib Selection-Learning — model-ENRICHMENT LOCK (leg-completeness) (2026-06-24)

**DOCS-ONLY. Authorises no code, no run, no build, no dependency, no matched-null, no new candidate
universe, no label/corpus change, no push.** Blind **Commit-1 lock** for **one lean enrichment shot**
on the selection model — the only directly north-star-aligned modeling step left
([main-quest reset](btc-fib-selection-learning-main-quest-reset-20260624.md) §4). It tests whether a
single new **leg-completeness / exclusivity** feature raises human-like leg agreement **over the current
Stage-2 model**. Execution needs a **separate explicit GO** (Commit 2).

**Blindness attestation:** no enrichment harness exists; **no enriched AP, no AP-lift vs the current
model has ever been computed or seen.** Every rule below is fixed from the prereg, the addendum, the
frozen config, and existing code — not from any enrichment result.

> **NORTH-STAR CHECK (binding):** this step answers *"does it improve the model's ability to select
> human-like legs/ranges vs the facit?"* — yes, by construction (it is a nested AP test vs facit).
> Honest prior: **low** — four per-leg features already came out ~0 at k=3 (only `cleanliness` stuck),
> so `no_enrichment_signal` is a **probable** outcome, and that outcome routes us to **grow the facit**
> (E8), which is the main quest proper.

## E0. Question + role (binding framing)

> **Does adding a single causal leg-completeness / exclusivity feature raise pooled OOS AP against the
> human facit, OVER the current cleanliness-carrying Stage-2 model, on the 4h primary at live k=3?**

One pre-specified feature, one nested comparison, one blind verdict. **Not** a new headline family; adds
**no** positive claim. The expected-and-publishable outcome is either a modest lift or a clean null that
sends us to labeling (E8).

## E1. The new feature (locked — `exclusivity` / leg-completeness; causal, pivot-structural)

- **Concept:** is the human's leg **the dominant, complete impulse** — or is it interrupted by a
  significant counter-move (i.e. really a sub-leg / two legs)? A human analyst anchors a fib on a
  *complete* swing, not a fragment.
- **Locked primary operationalization** (causal, on the frame **truncated at `anchor_b + k`, k=3**,
  pivots from [`detect_pivots`](../../../src/fibengine/pivots/detect.py); all interior pivots are
  `≤ anchor_b` so this is causal, `k* = 3`, matures with the base detector — same as the existing k≤3
  set):
  - `net = |price(anchor_b) − price(anchor_a)|` (the leg magnitude).
  - `R = deepest interior structural counter-retracement` reached by a **detected opposite-kind pivot**
    strictly between `idx(anchor_a)` and `idx(anchor_b)`: for an up-leg (a=low, b=high), among interior
    detected **low** pivots, `R = max(running_interior_high_before_low − low_price)`; symmetric for a
    down-leg. **No interior opposite pivot → `R = 0`** (uninterrupted single impulse).
  - **`exclusivity = clip(1 − R / net, 0, 1)`** (1 = dominant/complete; →0 = deeply interrupted).
- **Pivot-structural by construction** (counts only *detected* structural retracements, not raw
  close-to-close path) — this is what makes it **distinct from `cleanliness`** (net ÷ total path, which
  counts all noise). **One** operationalization; no post-hoc swapping of the formula.
- **Distinctness check (reported, not a gate):** report `corr(exclusivity, cleanliness)` on the **train**
  fold. If it is near ±1 the feature is largely a cleanliness proxy — reported honestly; the verdict
  still rests on the nested AP-lift (E4), not on this correlation.

## E2. Baseline (locked — the bar that matters)

- **Baseline = the CURRENT Stage-2 model**: the locked live `k≤3` feature set
  `{magnitude, cleanliness, duration, prominence, structure_alignment}`, same
  [`fit_logreg`](../../../src/fibengine/research/selection_learning.py), same training. **NOT** the
  trivial magnitude/prominence baseline. *(Reason: vs the trivial baseline `cleanliness` alone already
  passes — that learns nothing. The only informative question is whether `exclusivity` adds over the
  model we already have.)*
- **Enriched model = baseline feature set + `exclusivity`** (6 features), identical universe / viewport
  / split / training.

## E3. Cell + universe + metric (locked — reuse Stage-2 verbatim)

- **Primary cell = 4h, live `k = 3`.** Candidate legs, ε-matching, purged/embargoed split, pooled OOS
  **Average Precision (AP)** vs facit, all **reused verbatim** from the Stage-2 headline
  ([`build_candidates`](../../../src/fibengine/research/selection_learning.py), `window_of`,
  `average_precision`). ROC-AUC secondary. No new universe, no `--refresh` (frozen-data parity).
- **Power floor = ≥ 10 test positives** → **4h only powered**; 1M/1w/1d are **context, never refuted**.

## E4. Inference + verdict (pre-stated, falsifiable — 4h primary)

- **AP-lift = AP(enriched) − AP(baseline)** on the **identical** test legs (nested; models trained once,
  held fixed). **Decision-point cluster bootstrap** by `anchor_b` group (2000 resamples, seed
  `20260618`), reusing
  [`decision_point_bootstrap`](../../../src/fibengine/research/selection_learning.py) — read as a
  bootstrap-stability statement, not a permutation null.
- **`enrichment_helps`** — AP-lift 95% CI **excludes 0 (> 0)**: `exclusivity` adds human-like
  leg-selection signal over the current model OOS. *(Modest framing still binds: report the standardized
  weight of `exclusivity` and whether `cleanliness` still dominates — a lift is not a reproduction.)*
- **`no_enrichment_signal`** — AP-lift 95% CI **includes 0**: per-leg feature enrichment has hit its
  ceiling on this corpus → **park the modeling line and grow/improve the facit** (E8). *Expected,
  publishable.*
- **`enriched_worse_check`** (direction guard) — CI **excludes 0 below**: the enriched model is
  significantly worse (overfit / leakage / mis-coded feature) — **investigate, not a finding.**

## E5. Scope exclusions (locked OUT — no drift)

Explicitly **not** in this shot: `scale_confluence` / multi-scale / any HTF cross-TF feature (causally
blocked at k=3 and reopens the W-gap availability question), more detector/snapping mechanics,
matched-null, any new candidate universe, Genesis, 1H, ETH, `data.fetch --refresh`, label/corpus
mutation, any edge/behaviour/PnL/backtest claim. **`scale-fit`** (local-relative magnitude) is **not**
in this primary lock either — at most a *named, pre-registered secondary* in a future lock, never added
mid-run.

## E6. Forking-paths discipline (locked)

**One** feature (`exclusivity`), **one** operationalization (E1), **one** baseline (E2), **one** verdict
(E4) — all fixed **before any fit**. **No add-until-significant**, no formula tuning on test, no swapping
the baseline to whichever is easiest to beat. The verdict rule is fixed before the data picks a branch.

## E7. Non-claims (binding)

Not a reproduction of human selection. **No edge / behaviour / PnL / backtest / strategy claim.** A lift
means only that `exclusivity` adds OOS ranking signal over the current model — **not** that the human is
reproduced (absolute AP stays capped by the ~0.83 coverage ceiling). The `cleanliness`-as-genuine-signal
crux stays **OPEN** and this shot does not resolve it. No Genesis, no auto-fib-as-truth, no
label/corpus mutation, no 1H, no ETH.

## E8. If `no_enrichment_signal` → the routed next step (pre-committed)

A clean null is **not** a dead end — it is **evidence the per-leg-feature approach has hit its ceiling on
this corpus** (BTC-only, 365 4h legs, one analyst, ~0.83 ceiling). The pre-committed route is then to
**park the modeling line and return to the main quest: grow/improve the human facit** (more labels and/or
a corpus-quality pass), since the binding constraint is then **data, not features**. No further per-leg
enrichment without more facit or a concrete new capability hypothesis.

## E9. Implementation plan (Commit 2 — NOT executed here)

- **New module `src/fibengine/research/selection_learning_enrich.py`** with its **own CLI**; **no code
  added to byte-capped `selection_learning.py`**. Reuses `build_candidates`, `compute_features` (the 5
  baseline features), `fit_logreg`/`predict_proba`/`average_precision`/`roc_auc`/
  `decision_point_bootstrap`, `window_of`, ε, and the `FROZEN_SNAPSHOT` preflight — adds only the one
  `exclusivity` column + the nested AP-lift comparison.
- **Tests** `tests/research/test_selection_learning_enrich.py` (causal exclusivity definition, no
  look-ahead, nested-baseline lift, verdict branches, distinctness check, frozen-data parity).
- **Results doc** later (Observed / Inferred / Unverified). Artifacts under
  `experiments/review/fib_selection_learning/enrich/` (**gitignored**). **Preflight FIRST**, frozen-data
  parity.

## E10. Why this is NOT forking-paths / NOT drift

The cell, baseline machinery, ε, split, metric, and bootstrap are reused **verbatim** from Stage-2; the
only new locks (the single `exclusivity` definition E1, the nested-vs-current-model baseline E2, the
verdict thresholds E4, the routed null E8) are pinned **now, before any enriched value exists**. It is
the one causally-clean, distinct, never-built prereg feature, tested against the model we already have —
the opposite of drift: a concrete attempt to **improve human-like leg/range selection**, not to explain
the measurement machine.

## E11. What this doc does NOT do

No code, no harness, no build, no run, no dependency, no matched-null, no new universe, no
label/corpus mutation, no push. Does **not** grant execution — Commit 2 requires a **separate explicit
GO**, and must **halt and report before code** if any of {the `exclusivity` definition, the
nested baseline, the cell/metric, the bootstrap unit, the verdict rule, the routed null} is found
unclear at build time.
