# Research-line status registry

One row per research **line** (not per doc): is it open, in-progress, closed, parked, dormant, or
deprecated. Source of truth for "where does X stand". Root-level snapshot:
[/STATUS.md](../../../STATUS.md). Per-result detail lives in [reviews/](../reviews/); current focus in
[handoff.md](../handoff.md); do-not-rerun nulls in [closed-questions.md](closed-questions.md).
**Last swept: 2026-07-21 (cascade sign-off + degenerate classification).**

Status legend: 🔬 **active** (work in flight) · ⏳ **pending-input** (waiting on a human action) ·
✅ **complete** (delivered, nothing pending) · ⛔ **closed** (null/answered, do not re-run) ·
⏸ **parked** (paused by decision, resumable) · 💤 **dormant** (docs-only prereg, never executed) ·
🗄 **superseded** (archived, not current evidence).

## Active / current

| Line | Status | Where it stands | Key docs |
|------|--------|-----------------|----------|
| **Selection-learning** (can a model select legs like the human; facit = source-fibs) | 🔬 **active** | Main line. Stage-2 = modest single-feature (`cleanliness`) lead, AP 0.057 vs 0.83 ceiling, **not a reproduction**. Controls all done; enrichment **closed**; learning-curve **saturated** (feature side is the lever, not 4h data). Now redirected to **top-down MTF nesting**. | [north-star](../north-star.md), [prereg](../reviews/btc-fib-selection-learning-prereg-20260617.md), [Stage-2 results](../reviews/btc-fib-selection-learning-results-20260618.md), [learning-curve results](../reviews/btc-fib-selection-learning-learning-curve-results-20260625.md) |
| **Top-down "sniper" MTF nesting** (model the same swing decomposed 1M→1W→1D) | ⏳ **pending-input** | Premise check: current facit does **NOT** nest (TFs are different eras). Needs **new deliberately-nested labels on one era** → **user will redraw later**. Prerequisite: extend `RESOLUTION_TIMEFRAME` (1M→1w) in `same_candle_mtf_resolution.py`. | [handoff Next Step](../handoff.md), [log 2026-06-25](../log.md) |
| **Structure-engine origin** (rule-based proposer vs facit; does the origin "sit"?) | ⏳ **pending-input** | MEASURED out-of-sample (2026-07-02): frozen 1h engine on 4h-DOWN facit (201 legs, LOCKED acceptance band) → origin sits **43 %** (CI ~36–50 %), leg 30 %; **37 % genuine wrong-swing** (bar-invariant). Overfit to 1h → does NOT generalize. Single most-prominent-high rule ≠ Chamoun's selector on ~half the legs (HO-B at scale). → **contrastive capture (#42) toward ≥30 windows** (user draws). | [handoff Next Step](../handoff.md), [log 2026-07-02](../log.md) |

## Complete

| Line | Status | Outcome | Key docs |
|------|--------|---------|----------|
| **Cascade-conditioning probe** (does the previous fib predict the next origin? Sequential/U1 on existing facit) | ✅ **complete** | **RAN 2026-07-20, SIGNED OFF 2026-07-21** → **`sequential_origin_signal` on 4h**: H1a 0.256 vs null 0.005, p<0.0005, CI [0.205, 0.298], N=363; ~all EXACT chains (76/93), both directions; 1d+1w agree, 1M nothing. ~1 in 4 origins = previous endpoint → a **component**, not the selector (74% unchained). Next cascade work (P3 data model) gated behind a separate GO. | [prereg](../reviews/btc-fib-cascade-conditioning-probe-prereg-20260720.md), [results](../reviews/btc-fib-cascade-conditioning-probe-results-20260720.md) |
| **BTC source-fib labeling** (1M→1W→1D→4H top-down) | ✅ **complete** | Base batches 9 / 20 / 67 / 365; current corpus **13 / 24 / 76 / 371 = 484** after the 06-26 nesting cohort (+4/TF) and 06-30 grow-facit (+5 1d, +6 4h) — locked in [`MANIFEST.json`](../../../data/labels/human_fib/MANIFEST.json) (audit 2026-07-20). **1H deferred** (cache not fetched). | [protocol](../../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md), [1M review](../reviews/btc-1m-reaction-review-cycle-20260611.md), [1D review](../reviews/btc-1d-reaction-review-cycle-20260612.md) |
| **Corpus integrity / dedup / corrections** | ✅ **complete** (1 pending fix) | Corpus declared clean (counts, conventions, caveats); 20171228 correction + 20250506 dedup (4H 366→365). **2026-07-21:** the 7 same-candle degenerates = **misclicks** (owner) → redraw/delete in home GUI, then relock `MANIFEST.json` — worklist in [handoff](../handoff.md). | [corpus integrity](../reviews/btc-source-fib-corpus-integrity-20260615.md) |
| **Selection-learning controls** (w-gap, stage-1, artifact + mechanics) | ✅ **complete** | `no_causal_gap` (W-gap); stage-1 per-pivot diagnostic; artifact-probe → detector-inflation **not supported** (investigate, not a finding). Crux stays open but cheaply unresolvable. | [w-gap results](../reviews/btc-fib-selection-learning-w-gap-results-20260623.md), [stage-1 results](../reviews/btc-fib-selection-learning-stage1-results-20260624.md), [artifact results](../reviews/btc-fib-selection-learning-artifact-results-20260624.md) |
| **Tooling / ecosystem** (#25, #30, #32) | ✅ **complete** | Ecosystem scan + review-ledger + overlap detector + HTML gallery direction. Issues closed. | [tooling scan](../reviews/fib-tooling-ecosystem-scan-20260615.md) |

## Closed (null / do-not-rerun)

| Line | Status | Outcome | Key docs |
|------|--------|---------|----------|
| **Fib behaviour event study (B-1) + context-conditioned** | ⛔ **closed** | All NULL. Registered in [closed-questions](closed-questions.md) — do not re-run. | [behaviour results](../reviews/btc-fib-behaviour-event-study-results-20260616.md), [context-conditioned results](../reviews/btc-fib-context-conditioned-study-results-20260616.md) |
| **Horizontal-structure event study** | ⛔ **closed** | Generic structure not special vs a random walk (`any_robust=False`). | [results](../reviews/btc-horizontal-structure-event-study-results-20260617.md) |
| **Selection-learning enrichment** (`exclusivity`) | ⛔ **closed** | `enriched_worse_check` — per-leg-feature line closed (0.80 collinear with `cleanliness`). | [enrichment results](../reviews/btc-fib-selection-learning-enrichment-results-20260625.md) |
| **`cleanliness` matched-null crux** | ⛔ **closed (rejected)** | Gated out by artifact-LOCK A8 (trigger not met), A11 asymmetric-weak, A9 out-of-scope. Not built. | [artifact lock A8/A11](../reviews/btc-fib-selection-learning-artifact-lock-20260624.md) |

## Parked / dormant

| Line | Status | Why | Key docs |
|------|--------|-----|----------|
| **MTF confluence atlas** (CP1–CP3) | ⏸ **parked** | Confluence exists as geometry, **not edge**. Recommendation: stop the track. | [interpretation decision](../reviews/btc-mtf-confluence-interpretation-decision-20260615.md), [CP3 capstone](../reviews/btc-mtf-confluence-atlas-cp3-20260615.md) |
| **Selection-learning mechanics** (snapping / net-vs-path / artifact-mechanics) | ⏸ **parked** | Descriptive geometry done; detector-geometry side-quests parked at the [main-quest reset](../reviews/btc-fib-selection-learning-main-quest-reset-20260624.md). | [mechanics](../reviews/btc-fib-selection-learning-artifact-mechanics-20260624.md) |
| **Fib → Genesis-V2** (phase 0 / 1 / 2, nullability policy) | 💤 **dormant** | Docs-only prereg/spec for the eventual edge→Genesis step; **never executed**. The path runs through selection-learning (step 1) first — see [north-star](../north-star.md). | [phase 0 prereg](../reviews/btc-fib-to-genesis-v2-phase0-prereg-20260615.md), [phase 1 spec](../reviews/btc-fib-to-genesis-v2-phase1-feature-export-spec-20260615.md) |
| **Chart regression strategy** | ⏸ **deferred** | Structural-first; pixel/golden snapshots deferred (follow-up issue #F drafted). | [strategy spike](../reviews/chart-regression-strategy-20260615.md) |

## Open GitHub issues

**None** — all research/tooling issues closed as of 2026-07-02.

Recent closures (2026-07-02 sweep):

| # | Title | Outcome |
|---|-------|---------|
| **#42** | ML/Optuna Fib Selection Learner | ✅ v0 landed (`afb5a5f`); lane continues in [handoff](../handoff.md), ML build gated behind a fresh prereg. |
| **#39** | Fib Skill Pack (style distillation) | ✅ `chamoun-fib-style-distiller` delivered ([style doc](chamoun-daily-fib-style.md)); labeler/test-writer/implementer superseded by `labeling/tool.py` + facit pipeline + `selection_annotation.py`. |
| **#38** | Rolling daily wick-pair A/B engine | ⛔ NULL `wick_pair_no_better` (coverage 0.08 vs 0.90); rank-form `wick_frac` left as an open tail. |
| **#31** | Fractal-based anchor detection | ⛔ Answered by the selection campaign — detection recall 0.902 (Stage-1), "detection is not the bottleneck — selection is". |

*(#37 **closed 2026-06-25** — verified verbatim duplicate of #35; the principle is a binding agent
principle in [AGENTS.md](../../../AGENTS.md) (commit 27232cb).)*

> 🗄 **Superseded:** pre-BTC-monthly-reset descriptive reads are archived under
> `archive/research_superseded/2026-06-08_pre_btc_monthly_reset/` — not current evidence
> ([reviews/README](../reviews/README.md)).
