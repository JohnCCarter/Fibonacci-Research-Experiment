# BTC Fib Selection-Learning — `cleanliness` artifact-probe LOCK (2026-06-24)

**DOCS-ONLY. Authorises no code, no run, no build, no dependency, no matched-null, no new candidate
universe, no label/corpus change, no push.** This is the **blind Commit-1 lock** for the
**cleanliness artifact-probe** — the cheap-first, existing-data diagnostic that interrogates the
single open CRUX named in the
[campaign checkpoint](btc-fib-selection-learning-checkpoint-20260624.md). It is **not** a new prereg
line: it tests an **already-produced** result (the Stage-2 `cleanliness` lead) for a measurement
defect, blind to any artifact-probe output. Execution needs a **separate explicit GO** (Commit 2).

**Blindness attestation:** no artifact-probe harness exists; **no reached/unreached cleanliness mean,
no snapping gap, no CI has ever been computed or seen.** Every rule below is fixed from the campaign
locks, the frozen config, and existing code — not from any artifact-probe result.

## A0. Question + role (binding framing)

> **Is the Stage-2 `cleanliness` lead a genuine human leg-selection signal, or a detection / anchoring
> artifact?**

The campaign established (checkpoint) that the modest 4h selection lead is carried almost entirely by
leg `cleanliness`, lives in the leg gestalt, is live-available (`no_causal_gap`) and not a
coverage/pivot problem. The **one open crux** is whether `cleanliness` is partly **mechanical** —
because the whole pipeline is conditioned on the detector's pivot universe and `cleanliness` is
computed on detector-defined legs. This probe decomposes that crux into its **two** mechanisms and
tests **both on existing facit data, with no new candidate universe**:

1. **Surfacing-bias** — does the detector preferentially *surface* cleaner human legs?
2. **Snapping-bias** — does *snapping* a human anchor to the nearest detector pivot mechanically
   *raise* the measured `cleanliness`?

This is a **diagnostic, not a headline**; it adds **no positive claim** (A9).

## A1. `cleanliness` formula (locked — source-bound, NOT redefined)

The engine's existing feature, used verbatim by Stage-2
([`core/features.py::_cleanliness`](../../../src/fibengine/core/features.py)):

```
cleanliness(span [lo,hi]) = |close[hi] − close[lo]|  /  Σ_{i∈(lo,hi]} |close[i] − close[i−1]|
```

(net close-move ÷ total close-path; `1.0` for `<2` bars or zero path). **Key structural fact, locked:
`cleanliness` depends ONLY on the endpoints' bar-index span `[lo,hi]` (close prices over that span) —
NOT on the anchor's click-price.** Therefore:

- The exact-vs-snapped contrast (A3) is a **pure index-span** contrast (human bar indices vs detector
  pivot bar indices).
- Because every leg's span `[lo,hi] ⊆` (… `anchor_b`], i.e. fully **before** the decision point,
  `cleanliness` is **inherently causal** — the `k=3` truncation (A4) cannot change it. No hindsight is
  introduced by either contrast. This lock does **not** redefine the formula; it pins which one is used.

## A2. reached / unreached definition (locked — Stage-2 ε-reconstruction, ALL legs)

- **Corpus = ALL human 4h legs** (the 365 `fib_*.json` source legs; facit-discipline, human-only
  sidecars via [`load_human_legs`](../../../src/fibengine/research/selection_learning.py)). **Unreached
  legs are NOT filtered out — they are the signal** (A0.1).
- A leg is **reached** iff **BOTH** its anchors are ε-reconstructable by the detector under the **exact
  Stage-2 rule**: each human anchor has a **causally detected** pivot of matching kind within **ε**
  (`time_tol = 3` bars, `price_tol = 0.5` × causal ATR; A4 of the campaign), where detection is
  [`detect_pivots`](../../../src/fibengine/pivots/detect.py) on the frame **truncated at `anchor_b +
  k`** with the frozen config (`fractal_n=1, lookback=3, min_prominence_atr=0.5`), `k = 3` (the Stage-2
  headline cell). **Unreached** = at least one anchor not ε-reconstructable. This reproduces the
  Stage-2 ~0.83 leg-reachability split (expected ≈ 62 unreached on 4h).
- **Primary = causal `k=3` detection** (parity with the pipeline that produced the lead). Full-frame
  detection is a **named sensitivity only**, not the verdict basis.

## A3. exact-vs-snapped definition (locked — paired, reached legs only, no imputation)

For each **reached** leg:

- **exact-anchor cleanliness** = `cleanliness` over the span `[idx(anchor_a), idx(anchor_b)]`, where
  `idx(·)` is the human anchor's bar index ([`_pos_of_ts`](../../../src/fibengine/research/selection_learning.py)).
- **snapped-anchor cleanliness** = `cleanliness` over `[idx(piv_a), idx(piv_b)]`, where `piv_·` is the
  **ε-matched detector pivot nearest** to each human anchor (tie-break: smallest time distance, then
  smallest price distance; ties logged).
- **Contrast = `gap_snap = snapped − exact`** (paired, within-leg).
- **No imputation.** Unreached legs have no snapped endpoints → **excluded from THIS contrast only**
  (they remain in the A2 surfacing contrast). Any reached leg whose snap is ambiguous/degenerate
  (e.g. `piv_a == piv_b`) is **dropped and logged**, never imputed.

## A4. causal computation (locked)

`cleanliness` and detection both computed on the frame **truncated at `anchor_b + k`, `k = 3`**, ATR
**causal** (trailing Wilder to the decision point). Per A1, truncation is moot for `cleanliness`
itself (span is pre-`anchor_b`); the lock keeps full parity with Stage-2/W-gap and forbids any
full-series leakage in the **detection** step (A2).

## A5. Statistic + bootstrap unit (locked — NOT row-level)

- **Surfacing statistic:** `gap_surface = mean(cleanliness | reached) − mean(cleanliness | unreached)`.
- **Snapping statistic:** `gap_snap = mean(snapped − exact)` over reached legs (paired).
- **Bootstrap = block bootstrap by CALENDAR QUARTER of `anchor_b`** (detector-free, exogenous unit —
  the A3 structural-chunk used detector pivots and does **not** transfer to a detector-free probe).
  Resample whole quarters with replacement (each quarter carries its reached + unreached legs),
  recompute the statistic, **2000 resamples, seed `20260618`**. Report point estimate, 95% CI, and
  one-sided `p`. **Row-level bootstrap is explicitly rejected** (legs cluster by regime/quarter).
  Month-block is a named sensitivity, not the primary.

## A6. Power floor (locked)

- **Surfacing contrast powered** iff `min(n_reached, n_unreached) ≥ 10` **and** ≥ 3 distinct quarters
  contain an unreached leg (so the block bootstrap is non-degenerate).
- **Snapping contrast powered** iff `n_reached ≥ 10`.
- **Expected powered: 4h only.** 1M/1w/1d are **context if underpowered, never refuted** (too few
  unreached legs).

## A7. Verdict rules (pre-stated, falsifiable — 4h primary; applied verbatim)

**Surfacing (`gap_surface`, 95% CI):**
- **`detector_surfacing_artifact`** — CI **excludes 0 ABOVE** (reached significantly cleaner): the
  detector preferentially surfaces cleaner human legs → the lead is **partly** a surfacing artifact.
- **`no_surfacing_artifact`** — CI **includes 0**: no evidence the detector surfaces cleaner human legs
  → surfacing artifact **not supported** (artifact risk reduced on this axis).
- **`inverse_surfacing`** (direction guard) — CI **excludes 0 BELOW** (unreached cleaner): unexpected;
  **investigate, not a finding.**

**Snapping (`gap_snap`, 95% CI):**
- **`snapping_inflates_cleanliness`** — CI **excludes 0 ABOVE**: snapping to detector endpoints
  mechanically raises `cleanliness` → measurement-bias artifact present.
- **`no_snapping_inflation`** — CI **includes 0**: snapping does not inflate `cleanliness`.
- **`snapping_deflates`** (direction guard) — CI **excludes 0 BELOW**: **investigate, not a finding.**

**Combined artifact reading (locked):**
- `no_surfacing_artifact` **AND** `no_snapping_inflation` → **`artifact_risk_reduced`** — the strongest
  non-artifact evidence the cheap probe can give: the `cleanliness` lead is **not explained** by
  detector surfacing or snapping. **This is NOT "cleanliness is proven human intuition"** (A9).
- **Either** contrast fires its artifact branch → **`detector_artifact_supported`** — the lead is
  **partly mechanical**; report **which half** and by how much.
- Underpowered → **`inconclusive_underpowered`** (checked first).

## A8. Gate-rule for the matched-null / new candidate universe (locked)

The matched-null (detector-independent leg universe) **may be considered ONLY IF** the cheap probe
returns **`detector_artifact_supported`** (surfacing artifact present) **AND** quantifying the residual
is judged necessary. If the probe returns **`artifact_risk_reduced`**, the matched-null is
**UNJUSTIFIED** — the crux is resolved on the cheap axis and the expensive universe is scope-creep.
**No matched-null, and no new candidate universe, may be built under this lock.** Any future
matched-null requires its **own separate blind lock** (own design-check, own prereg).

## A9. Non-claims (binding)

- **Not a reproduction** of human selection. **Not** an edge / behaviour / PnL / backtest / strategy
  claim. No Genesis, no auto-fib-as-truth.
- **`artifact_risk_reduced` does NOT prove `cleanliness` is "human intuition."** It only narrows the
  artifact risk on **two specific mechanisms** (surfacing, snapping). The broader "is human-leg
  cleanliness special vs any matched non-human swing" question is **out of scope** (gated, A8).
- Underpowered TFs are **context, not refuted.**
- **No 1H, no ETH, no label/corpus mutation, no `data.fetch --refresh`** (frozen-data parity — same
  universe as Stage-2 / W-gap / Stage-1).

## A10. Implementation plan (Commit 2 — NOT executed here)

- **New module `src/fibengine/research/selection_learning_artifact.py`** with its **own CLI entry**;
  **no code added to `selection_learning.py`** (byte-capped). Reuse `_cleanliness` (or its exact
  formula), `load_human_legs`, `_pos_of_ts`, `detect_pivots`, `atr`, `load_candles`, the ε constants,
  and the `FROZEN_SNAPSHOT` preflight pattern from `selection_learning_gap.py`.
- **Tests** `tests/research/test_selection_learning_artifact.py` (reached/unreached split, exact-vs-
  snapped span, quarter-block bootstrap, verdict branches, no-imputation drop/log, k=3 causal parity).
- **Results doc** later (`btc-fib-selection-learning-artifact-results-YYYYMMDD.md`, Observed / Inferred
  / Unverified). Artifacts under `experiments/review/fib_selection_learning/artifact/` (**gitignored**).
- **Preflight FIRST**, frozen-data parity, per-cell/contrast checkpoint as needed.

## A11. Why this answers the crux better than a new candidate universe

- **Symmetric, not conservative.** `reached-vs-unreached` is informative in **both** directions
  (≈ → no surfacing artifact; ≫ → artifact), where a matched-null is **asymmetric** (fail-to-reject is
  inconclusive, not non-artifact) because its endogenous swing-validity rule correlates with
  `cleanliness` by construction and raises the null baseline.
- **Detector-independent MEASUREMENT on existing data.** It uses **exact human anchors** (facit) — no
  new universe, no swing-filter, no `K`, no draw-pool, no arbitrary windowing (the convenience trap the
  B feasibility check flagged).
- It targets the **exact** two mechanisms in "detection / anchoring artifact": `reached-vs-unreached`
  **is** the surfacing test; `exact-vs-snapped` **is** the anchoring/measurement test.

## A12. What this doc does NOT do

No code, no harness, no build, no run, no dependency, no matched-null, no new candidate universe, no
label/corpus mutation, no push. Does **not** grant execution — Commit 2 requires a **separate explicit
GO**, and must **halt and report before code** if any of {`cleanliness` formula, reached/unreached
definition, exact-vs-snapped definition, bootstrap unit, power floor, verdict rules, matched-null
gate-rule} is found unclear at build time.
