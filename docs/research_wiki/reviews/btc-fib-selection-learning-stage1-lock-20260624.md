# BTC Fib Selection-Learning — Stage-1 per-pivot diagnostic LOCK (2026-06-24)

**DOCS-ONLY. Authorises no code, no run, no build, no dependency, no label/corpus change.** This is the
**Commit-1 concretization lock** for **Stage-1** (per-pivot diagnostic floor), the diagnostic
explicitly deferred-as-secondary in the
[prereg §2/§6/§8](btc-fib-selection-learning-prereg-20260617.md) and
[§12 addendum A5](btc-fib-selection-learning-addendum-20260618.md). It is **not** a new prereg — the
design, target unit, baseline, metric, ε, split and coverage-ceiling discipline were **already frozen
blind in 2026-06-17/06-18**; this doc only concretizes the per-pivot specifics, **blind to any Stage-1
output**, before any build. Execution needs a **separate explicit GO** (Commit 2). Builds on the
closed [W-gap study](btc-fib-selection-learning-w-gap-results-20260623.md) (`no_causal_gap` — the 4h
signal is live-available at `k=3`).

**Blindness attestation:** no Stage-1 harness exists; **no per-pivot agreement number, AP, recall, or
lift has ever been computed or seen.** Every rule below is fixed from the prereg, the addendum, the
frozen config, and existing code — not from any Stage-1 result.

## S0. Question + role (binding framing)

> **Is the endpoint / pivot choice itself learnable, *given the detector's pivot universe*?**

Stage-1 is a **diagnostic floor, not a headline** (prereg §2). It decomposes the Stage-2 agreement
ceiling (AP ~0.057 against a ~0.83 leg-reachability ceiling) into **two separately-reported halves**:

1. **detection / coverage** — are the human's anchors present in the detector's pivot universe at all?
2. **ranking / selection** — *given* they are present, do human-anchored pivots rank **above the
   prominence baseline OOS**?

These two are reported **separately** and must never be conflated: a detection miss is **not** a
ranking failure, and a ranking lift is **not** a reproduction (S8 non-claims binding).

## S1. Target / label (locked)

- **Unit = one detected pivot** from [`detect_pivots`](../../../src/fibengine/pivots/detect.py) on the
  **causally truncated** frame (S2), pooled across `high`/`low` kinds.
- **Label = 1** iff the pivot lies within **ε** of **any** human anchor — `anchor_a` **or** `anchor_b`
  of **any** human leg for that TF (from [`load_human_legs`](../../../src/fibengine/research/selection_learning.py),
  facit-discipline: human-only sidecars). **a/b role is pooled** (a pivot is "human-anchored" if the
  human used it as *either* endpoint; direction/role is a Stage-2 question). *Reason:* Stage-1 asks
  only "is this extreme one the human anchors on," independent of which leg or role.
- **ε reused verbatim** (A4): `time_tol = 3` bars, `price_tol = 0.5` ATR, with **causal ATR**
  (trailing Wilder up to the decision point, never full-series). No per-TF ε tuning.
- **Distance-to-nearest-human-anchor is the label and may NEVER be a feature** (label-leakage guard).

## S2. Live availability / decision point (locked; the one subtle item, resolved blind)

- A pivot is usable **only when confirmed**. **Decision-point cutoff = `pivot_index + max(k,
  fractal_n)`**; under the frozen config `fractal_n = 1`, so the detectability cutoff is `pivot+1`.
  Pivots are **re-detected on the frame truncated at the cutoff** (so a pivot's *existence* is never
  look-ahead); the live universe at a cell is exactly "pivots present on the truncated frame at the
  cutoff," even if a later bar would supersede one (live-realistic, mirrors Stage-2 `end_piv is None`).
- **Feature maturity is `k*`-gated identically to Stage-2 (A2.2): a feature enters a cell only when
  `k*(f) ≤ k`,** by column selection on the truncated frame. This — not the bare detectability lag —
  is what makes the `k`-sweep non-vacuous and resolves the detection-lag (`fractal_n=1`) vs
  prominence-window-lag (`lookback=3`) tension: prominence (`k*=3`) is simply **not admitted** until
  `k ≥ 3`, so no clipped/immature prominence ever enters.
- **No full-frame pivot leakage:** higher-degree pivots for `scale_confluence` are detected on the
  **truncated** frame only (via [`detect_pivots_multi`](../../../src/fibengine/core/scale.py)), never
  the full series.

## S3. `k`-buffer (locked, with the degeneracy call made explicit)

- **`k`-sweep = {0, 3, 6, 12}**, reused from A5 (TF-independent, bar-based).
- **`k = 0` is DEGENERATE for Stage-1 — and this differs from "earliest-confirmed pivot."** Under the
  `k*`-gating (S2), the per-pivot usable feature set at `k=0` is `{round_number}` only (interaction-
  only, *never primary* per §3) **and the primary baseline `prominence` (`k*=3`) is not yet mature** →
  there is **no usable ranking feature and no usable baseline**. `k=0` is therefore reported as
  **degenerate / uninterpretable and excluded from the verdict** (parallel to Stage-2's `k=0`
  exclusion, though for a different reason — empty *usable feature/baseline* set, not empty universe).
  *(This corrects the earlier intent-check note that called `k=0` "earliest-confirmed, not
  degenerate": once the frozen `k*`-gating is applied, `k=0` is degenerate.)*
- **Primary cell = `k = 3`** (for comparability with the Stage-2 / W-gap headline) — the first cell
  where `prominence` (= baseline) and `structure_alignment` are mature.
- **Cells `k=3` and `k=6` share the same feature set** `{prominence, structure_alignment}` (no feature
  has `3 < k* ≤ 6`); `k=6` differs only by a more-mature truncation frame. **`k=12`** additionally
  admits `scale_confluence`. (Exactly parallel to Stage-2/W-gap.)
- The `k`-definition is **not** otherwise ambiguous; no stop-before-code condition is triggered.

## S4. Features (locked blind — per-pivot subset of the frozen eight; no new features)

Per the addendum A2 binding ("no new features invented"), Stage-1 reuses **only the per-pivot-definable
subset** of the eight frozen features. **`magnitude`, `cleanliness`, `duration`, and `exclusivity` are
leg/set-level — structurally undefined on a single pivot — and are EXCLUDED by construction (not a
choice).**

| Per-pivot feature | `k*` | role in Stage-1 |
|-------------------|:----:|-----------------|
| `prominence` | 3 | the pivot's own ATR-scaled prominence — **= the primary baseline** (S5) |
| `structure_alignment` | 3 | per-pivot alignment with recent structure |
| `scale_confluence` | 12 | pivot coincides with a higher-degree (deg-12) fractal |
| `round_number` | 0 | price proximity — **interaction-only, never primary** (§3) |
| `recency` | ∞ | **dropped at every `k`** (omniscient as coded — A2.1), never a live feature |

- **Live per-pivot model:** `k=3`/`k=6` → `{prominence, structure_alignment}`; `k=12` → `+
  {scale_confluence}` (+`round_number` as interaction only throughout).
- **Only per-pivot features** — no pairing info, no "the other endpoint," no future leg information,
  **no right-edge features**.
- **Train-only standardization:** `_standardize` mean/std fit on the **train fold only**, never pooled
  (Stage-2's `selection_learning.fit_logreg` already does this; Stage-1 **must inherit and the lock
  makes it an explicit guard**).
- **Honest consequence (foregrounded, not buried):** because `cleanliness` (the leg feature that
  carried the entire Stage-2 lead) is **structurally absent** from Stage-1, the per-pivot model adds
  only `structure_alignment` over the prominence baseline at `k=3` (and `scale_confluence` at `k=12`).
  The **ranking sub-test is intentionally thin**; Stage-1's primary informative output is the
  **detection/coverage** half (S0.1, S6). A null ranking result is the *expected, publishable* outcome
  and is fully consistent with "the human signal lives in the leg gestalt, not the lone pivot."

## S5. Baselines (locked)

- **Primary baseline = the detector's `prominence` ranking** (§6 Stage-1), causal prominence computed
  on the **same truncated frame** as the model (identical universe/viewport; only the ranking rule
  differs — mirrors Stage-2's baseline parity).
- **Verdict is decided on the prominence baseline ALONE** (single primary), **not** a baseline family.
- A `magnitude`/excursion-style sensitivity baseline **may be named and reported** but the **verdict
  is not chosen post-hoc** from whichever baseline is easiest to beat (validity-over-convenience; B-1
  forking-paths lesson binding).

## S6. Metrics / inference / coverage (locked)

- **Primary metric = pooled OOS Average Precision (AP)**; **ROC-AUC secondary** (A5.1). Pooled over all
  test-window pivot rows into one ranking, one AP per TF.
- **Lift = AP(model) − AP(prominence baseline)** on the identical test pivot set / truncated viewport.
- **Power floor = ≥ 10 test positives** (human-anchored test pivots). Expected powered: **4h only**;
  **1M/1w/1d are context if underpowered, never refuted.**
- **Purged/embargoed split** on the pivot's chart time, reach = the per-cell forward feature reach
  (`max(k, fractal_n)`); no pivot's feature window may straddle the split (reuse
  [`window_of`](../../../src/fibengine/research/selection_learning.py)).
- **Bootstrap cluster unit — locked blind, with reason (NOT row-level).** Resample whole **structural
  chunks = consecutive runs of `structure_window = 6` base pivots** (the **exact segmentation already
  frozen in A3** for exclusivity), with replacement, 2000 resamples, seed `20260618`. *Reason:* a
  single pivot has no mechanical endpoint-sharing (so Stage-2's `anchor_b` decision-point cluster does
  not transfer), but pivots in one local structure share regime/volatility correlation; the A3 6-pivot
  chunk is the **pre-frozen "structure" unit** and reusing it avoids inventing a new cluster post-hoc.
  **Row-level bootstrap is explicitly rejected** as variance-understating. Report lift point estimate +
  95% CI and one-sided `p(lift ≤ 0)`, read as a **bootstrap-stability** statement (not a permutation
  null).
- **Coverage ceiling reported SEPARATELY from ranking:** **detection-recall = fraction of human anchors
  (a/b pooled) within ε of *any* detected pivot at the cell's viewport.** Absolute AP is interpreted
  against this recall ceiling, never 1.0. Stage-1 must **decompose** the Stage-2 ceiling into
  detection-recall (this number) vs selection (the lift), and **never** fold a detection miss into a
  ranking failure.

## S7. Verdict rule (pre-stated, falsifiable — 4h primary; exact CI/power conditions)

Using lift = AP(model) − AP(prominence) on the powered cell, with the S6 structural-chunk bootstrap
95% CI, and detection-recall `R`:

- **`inconclusive_underpowered`** — no cell reaches ≥ 10 test positives (all TFs context only).
  *Checked first; if it fires, no ranking verdict is issued.*
- **`detector_coverage_limited`** — on the powered cell **`R < 0.50`** (the detector fails to surface a
  majority of human anchors): coverage, not ranking, is the bottleneck; the lift is still reported but
  this is the **headline** label (ranking is over a biased remainder). *(Stage-2 leg-reachability was
  ~0.83, so this is a guard, not the expected outcome — per-anchor recall may differ from per-leg.)*
- **`pivot_selection_learnable`** — powered (≥ 10 test pos) **and** `R ≥ 0.50` **and** lift 95% CI
  **excludes 0 (> 0)**: given the detector's universe, human-anchored pivots rank above prominence OOS.
- **`no_pivot_signal_above_prominence`** — powered **and** `R ≥ 0.50` **and** lift 95% CI **includes
  0**: per-pivot choice carries no ranking signal beyond prominence (the expected/publishable null,
  S4).
- **`artifact_check_needed`** (direction guard) — lift 95% CI **excludes 0 below (< 0)** (prominence
  *significantly beats* the model): a modeling artifact (standardization, baseline leakage, label
  noise) — **investigate before interpreting, not a finding.**

Stage-1 is **descriptive with CIs**, secondary per A5; it **does not** enter the four-TF Holm headline
family and **adds no new positive claim**.

## S8. Non-claims (binding)

- **Not a reproduction** of human selection (the gestalt is Stage-2; a learnable pivot ≠ a reproduced
  leg). **Not** an edge / behaviour / PnL / backtest / strategy claim.
- **"Beats prominence" ≠ "human pivots are special"** beyond the narrow OOS ranking statement.
- **The cleanliness / detection-anchoring artifact question stays OPEN** — Stage-1 does **not** test it
  (and `cleanliness` is structurally absent here, so it *cannot* resolve it). No overclaim either way.
- Absolute recall is **capped by the detector coverage ceiling** — interpret against it, not 1.0.
- Underpowered TFs are **context, not refuted.**
- **No Genesis, no auto-fib-as-truth, no label/corpus mutation, no 1H, no ETH, no ML-hype, no tuning
  on test, no `data.fetch --refresh`** (frozen-data parity — same universe as Stage-2/W-gap).

## S9. Implementation plan (Commit 2 — NOT executed here)

- **New module `src/fibengine/research/selection_learning_stage1.py`** with its **own CLI entry**;
  **no code may be added to `selection_learning.py`** (byte-capped at ~32 763 B, ~5 B from the 32 768
  cap). Reuses `detect_pivots`, `detect_pivots_multi`, `load_human_legs`, `_pos_of_ts`, `window_of`,
  `fit_logreg`/`predict_proba`/`average_precision`/`roc_auc`/`decision_point_bootstrap`, and the
  `FROZEN_SNAPSHOT` preflight from `selection_learning_gap.py`.
- **Tests later:** `tests/research/test_selection_learning_stage1.py`.
- **Results doc later** (`btc-fib-selection-learning-stage1-results-YYYYMMDD.md`, Observed / Inferred /
  Unverified). Artifacts under `experiments/review/fib_selection_learning/stage1/` (gitignored).
- **Preflight FIRST**, frozen-data parity, per-cell checkpoint/resume (reuse the W-gap pattern).

## S10. Why this is NOT forking-paths

The target unit (per-pivot), baseline (prominence), metric (pooled AP), ε, split discipline, coverage
ceiling, and `k`-sweep were pinned **blind in 2026-06-17/06-18** and are reused verbatim. The only new
locks (per-pivot label a/b-pooling S1, decision-point + `k*`-gating S2–S3, the per-pivot feature subset
S4 *derived definitionally* from the frozen eight, the structural-chunk bootstrap S6, and the verdict
thresholds S7) are pinned **now, before any Stage-1 model exists or any value is seen.** The verdict
rule is fixed before the data picks a branch.

## S11. What this doc does NOT do

No code, no harness, no build, no run, no dependency, no label/corpus mutation, no push. Does **not**
grant execution — Commit 2 requires a **separate explicit GO**, and must **halt and report before
code** if any of {label definition, decision-point/`k*` gating, feature subset, baseline, bootstrap
unit, coverage-vs-ranking separation} is found unclear at build time.
