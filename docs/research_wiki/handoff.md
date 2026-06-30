# Current Handoff

This page is the current working context for future agents. It is editable; the
append-only trail lives in [log.md](log.md).

## Current Focus

> **NORTH STAR (binding — canonical: [north-star.md](north-star.md)):** *learn how the human selects
> meaningful fib legs/ranges and draws Fib like the analyst (facit = ground truth)* — this is **step 1**
> of a staged path (selection → descriptive level-reads → edge/backtest → **Genesis-V2**). "No edge
> claim" = *not yet / not from this sub-study* (a validity gate protecting the future edge), **not** a
> cap. Every step first answers *"does this improve human-like leg/range selection vs the facit?"* — if
> no, park it. Mechanics drift **DONE/PARKED** ([reset](reviews/btc-fib-selection-learning-main-quest-reset-20260624.md)).

**BTC monthly-first top-down protocol** — re-labeling on BTC/USD only after the
**2026-06-09 log-scale + profile reset** (prior linear / 0.236 labels archived).

**Canonical protocol:** [BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md](../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)

| Step | Timeframe | Status |
|------|-----------|--------|
| 1 | **1M** | **Complete** — 9× source fibs, 1D + 4H reaction review approved (2026-06-11) |
| 2 | **1W** | **Complete** — 21× source fibs verified; combined map + per-fib 4H zoom (2026-06-11) |
| 3 | **1D** | **Complete** — 67× source fibs + 4H reaction-review (2026-06-12); 1816 events, 90-day window |
| 4 | **4H** | **Complete** — 365 active source fibs (366 drawn; 1 superseded 20250506 dedup) |
| 5 | 1H | Deferred — 1h cache not fetched yet |

**ETH/USD:** blocked until BTC protocol approved.

## Next Step — open (nesting tested → within-TF reframe; per-leg-feature line stays closed)

**2026-06-26 settled the nesting question** (full detail: [log.md](log.md) top entry). The human nests
**within-TF** — successive impulse legs on one timeframe — **not cross-TF** (no parent→child swing).
Two pre-registered, leakage-disciplined **nulls**: cross-TF prediction 1w→1d `no_parent_context_signal`
(directional, N=9; cohort v2 leakage-disqualified, frozen corpus used; method re-locked before run when
a feasibility count showed the first method null-by-construction); the within-TF axis as a feature
`impulse_leg` → **clean POWERED null** (4h, AP-lift CI [−0.032,+0.027] straddles 0, p=0.34) → the
per-leg-feature line **stays closed** (`exclusivity` + `impulse_leg`, both null). The +0.119 weight is
in-sample only (OOS-refuted) — **not** evidence. Reachability diag: HTF (1M 1.00 … 4h 0.85, no epoch
gaps) is **intrinsically data-starved**, not detector-broken — no feature/detector fix powers 1M/1w.

**No active model track.** Open question for the user: where next, given per-leg features exhausted,
data saturated / HTF starved, signal living in the modest 4h `cleanliness` lead. Candidate: north-star
**step 2 (descriptive level-reads)** rather than more selection features. Cohort v2 (`ed98dc4`) stays
drawn but **unused** (prediction-disqualified); `RESOLUTION_TIMEFRAME` 1M→1w no longer on the path.

**2026-06-29: #38 daily wick-pair anchor accuracy → `wick_pair_no_better` (SIGNED OFF 2026-06-29).**
The **strong-form** rejection-wick premise (anchors sit on ≥50%-wick candles) is **not supported** at
`wick_frac=0.5` a priori: coverage 0.08 vs control 0.90, despite the selector picking a pair in 44/71
cases (dominant-wick pivots sit at *different* bars than the human's anchors). **#31's fractal line
stays the candidate.** The **rank-form** question (does wick geometry help *rank* candidates?) is
**left open** — `agreement` was uninformative (floor for both arms) — for a *separately-registered*
`wick_frac` sweep (not a rescue). Does **not** reopen the closed per-leg-feature line. [log.md](log.md) top.

## Recent Changes

- **2026-06-30 Checkpoint reminder hook wired** — `UserPromptSubmit` hook auto-pings once at ~25%
  context (the in-time sweet spot); model-discretion invocation was unreliable, `PreCompact` rejected as
  too late. [log.md](log.md) top.

- **2026-06-30 GROW-FACIT started — daily 2025–26 gap filled.** 5 source fibs transcribed from the
  2026-06-29 chamoun TradingView screenshots, human-reviewed to facit via labeling-tool
  [`--review-candidate`](../../src/fibengine/labeling/tool.py) (`created_by=human`,
  `source=manual_screenshot_transcription_reviewed`); ids `20251006, 20251027, 20251111, 20260114,
  20260601`. North-star grow-facit bridge now live. [log.md](log.md) top.
- **2026-06-29 Leg-agreement RULER — built + SIGNED OFF (north-star step-1 measurement instrument).**
  The free facit-checker the selection campaign lacked (#38 `agreement` floored: `compare_label`/
  `select_swing` not localized to the facit leg). [Locked prereg](reviews/btc-fib-leg-agreement-ruler-prereg-20260629.md)
  + [postlock](reviews/btc-fib-leg-agreement-ruler-prereg-20260629-postlock.md); new
  [`evaluation/leg_agreement.py`](../../src/fibengine/evaluation/leg_agreement.py) (`mean(s_high,s_low)`,
  `s=max(0,1−Δbar/W)`, absolute **W=2**, direction-gated; +21 tests). Knobs set by selector-independent
  pre-lock calibration (spacing guard rejected W=5). **leakage-review caught a real overclaim** → hard-
  null + bucket histogram → re-scoped: a **valid strict selection-scorer** with a narrow coverage-capped
  range (ceiling mean ~0.79; sub-1.0 = detector-coverage artifacts, not near-misses; binary for
  selection). Usable as **eval**, NOT a graded **training objective** → the learned-selector prereg must
  confront the narrow range. Descriptive step-1, no edge/OOS. [log.md](log.md) top.
- **2026-06-29 #38 daily wick-pair anchor accuracy — clean NULL (SIGNED OFF 2026-06-29; fractal
  control 0.90 confirmed via B-closure, postlock A5).** Pre-reg
  [locked 2026-06-29](reviews/btc-fib-daily-wick-pair-anchor-prereg-20260629.md) (selector-only,
  addendum A1). New [`strategies/chamoun_daily_wick_pair.py`](../../src/fibengine/strategies/chamoun_daily_wick_pair.py)
  + run harness [`research/chamoun_wick_pair_accuracy.py`](../../src/fibengine/research/chamoun_wick_pair_accuracy.py)
  (+`pivot_recall` producer-injection, +4 tests). Result (N=71): coverage 0.08 vs control 0.90 →
  **`wick_pair_no_better`**; #31 stays the candidate. Gates green (623 pytest, 74% cov, ruff, bounds).
  [log.md](log.md) top.
- **2026-06-26 Nesting REFRAME + two nulls.** Within-TF (not cross-TF) impulse-leg decomposition (facit);
  cross-TF 1w→1d [`no_parent_context_signal`](reviews/btc-fib-nesting-prediction-prereg-1w1d-20260626.md) (N=9) +
  [`impulse_leg`](reviews/btc-fib-impulse-leg-feature-prereg-20260626.md) 4h **clean POWERED null** (CI [−0.032,+0.027]); per-leg line closed; HTF data-starved. [log.md](log.md).
- **2026-06-26 Top-down nesting tool support** (anchor markers, session overlay, `c` focus; cohort v2 drawn, v1 deleted) — now **unused** (prediction-disqualified). [log.md](log.md).
- **2026-06-25 Fib SELECTION-LEARNING model-ENRICHMENT — RUN → `enriched_worse_check` (4h k=3); line
  CLOSED.** Blind Commit-2 of the [enrichment LOCK](reviews/btc-fib-selection-learning-enrichment-lock-20260624.md)
  (`c80acb0`). Parity: AP-baseline = Stage-2 headline 0.0567, n_test_pos=65, excl=0 (no look-ahead).
  Causal `exclusivity` *lowers* pooled OOS AP 0.0567→0.0387; AP-lift −0.018, CI [−0.070, −0.0019],
  p(lift≤0)=0.994. Mechanism (Inferred): 0.80 collinear with `cleanliness`. Per-leg-feature line
  **closed** → grow-facit (fork under **## Next Step**). [Results](reviews/btc-fib-selection-learning-enrichment-results-20260625.md).
- **2026-06-24 Fib SELECTION-LEARNING — MAIN-QUEST RESET (docs-only).** Stop the mechanics drift,
  re-anchor to the north star (above). Controls/mechanics (artifact-probe, snapping/net-path mechanics,
  flip) **DONE; matched-null / detector-geometry side-quests PARKED.**
  [Main-quest reset](reviews/btc-fib-selection-learning-main-quest-reset-20260624.md).

- **2026-06-22 Fib SELECTION-LEARNING W-gap study — BUILT + module split, RUN PENDING (home).** Commit 2 of side-quest #1, built to the [W-gap LOCK](reviews/btc-fib-selection-learning-w-gap-lock-20260622.md) (`4f47d8e`): `gap(k)=AP(retro-W)−AP(live-k)` on identical rows, embargo=W, L5 verdict. New `research/selection_learning_gap.py` (+5 tests); W-gap code split out to keep `selection_learning.py` under the §6 size cap (was 995 lines); flushed-stderr `_progress` logging in `build_candidates`+`build_retro_features` so a long run is never blind (result-neutral). **Run NOT executed** — inherent ~2-3h per-endpoint-detect cost on the ~20k-bar 4h frame (leakage-bearing truncation, no legal shortcut); to run at home (see Next tracks). No gap results, no verdict. Commit `884d4c0`, gates green (pytest 549, cov 75%).
- **2026-06-18 Fib SELECTION-LEARNING 4h slices (`ea6c2ea`) — Stage-2 headline + prominence-family `survives_prominence_family` + k-sweep `k_stable_live_selection_signal` + §12 addendum.** Modest single-feature `cleanliness` lead; 4h-only powered; low AP (0.057–0.066 vs 0.83 ceiling); not a reproduction; 1M/1w/1d underpowered. Full detail: Status section below + [results](reviews/btc-fib-selection-learning-results-20260618.md).
- **2026-06-17 NEW LINE pre-registered — Fib SELECTION-LEARNING (docs-only, gated).** Different question from the closed behaviour/B-1 nulls: *can a model reproduce how the human selects swings/ranges* (labels as facit, **no edge/backtest/Genesis**). Stage 2 leg/range gestalt (5 components) = target, Stage 1 per-pivot = diagnostic; live-equivalent vs **bounded** retrospective viewport → causal-availability gap; binding feature-provenance rule; one primary cell + coverage ceiling. Two-step gate. [Prereg](reviews/btc-fib-selection-learning-prereg-20260617.md).
- **2026-06-17 B-1 horizontal-structure study — BUILT + RUN → NULL (closed).** SENARE-1 e-value (conditional 2×2 safe test) + 3-subject harness (swing/round/prior-extreme vs matched random-walk null), all pins locked pre-run. `any_robust=False` on all 12 cells; only swing edges the null (e=1.70 — not even marginal; e-Holm needed E≈240 → low power). Generic structure not special vs a random walk; §10 sanity-check not run. Commits `474f320`→`44e63fa`. [Results](reviews/btc-horizontal-structure-event-study-results-20260617.md).
- **2026-06-17 External-pattern-scan absorption — landed on `main`** (PR #33→main; #34 sec cryptography→49.0.0). Standing [prereg addendum](reviews/horizontal-structure-prereg-addendum-20260617.md) (RW control / anytime-valid re-looks / purged-CV embargo) + code (synthetic RW baseline, `--by-uncertainty` worklist, fail-closed swing-label validation). No facit/signal/auto-fib touch.
- **Earlier 2026-06-15/06-16 changes — archived** (kept lean for the 400-line bound): behaviour +
  context studies **NULL/CLOSED** (`f4e96f1`); Fib→Genesis V2 Phase 2 + 2.5 nullability **PASS/CLOSED**
  (`68dc006`); MTF confluence CP1–CP3 **CLOSED** (geometry, not edge); #32 tooling DONE + `20171228`
  correction + chart-contract snapshots; 2026-06-08→06-12 source-fib milestones. **All preserved** in
  the **PAUSED/CLOSED status sections below** + [log.md](log.md) /
  [log part 1](log-archive-btc-postreset-part1.md); current counts in the Verification Snapshot.

## Status — Fib SELECTION-LEARNING line (2026-06-18, slice committed `ea6c2ea`)

Distinct question from the closed behaviour/B-1 nulls: *can a model reproduce how the human selects
legs/ranges* (labels = facit; **no edge/behaviour/backtest/PnL/Genesis/auto-fib claim**). Result so far
(4h is the only powered cell):

- **Magnitude baseline — survived** (AP-lift CI `[0.023, 0.120]` excludes 0, OOS).
- **Prominence family A/B — survived** (`survives_prominence_family`; CI excludes 0 vs summed *and*
  max prominence).
- **k-sweep {0,3,6,12} — `k_stable_live_selection_signal`:** k=0 degenerate / **not interpretable**
  (0 candidates); k=3/6/12 powered and survive the locked baseline family.
- **Modest framing (binding when citing this):** `cleanliness` still dominates the weights; the k=12
  `scale_confluence` term (~0.13) is **only a secondary hint**, not a second pillar; **low absolute
  AP** (0.057–0.066 vs 0.83 ceiling); **no full reproduction of human selection**; **no
  edge/behaviour/backtest/Genesis claim**; **1M/1w/1d underpowered, not refuted**.

### Next candidate tracks (listed only — NONE started, NONE authorised)

- **Retrospective `W` / causal-availability gap (4h) — DONE (job machine 2026-06-23). Verdict
  `no_causal_gap`.** Full `--w-gap` run completed (all 6 cells, ~3.5 h, deterministic seed 20260618);
  results in [w-gap RESULTS](reviews/btc-fib-selection-learning-w-gap-results-20260623.md), locked per
  the [w-gap LOCK](reviews/btc-fib-selection-learning-w-gap-lock-20260622.md). On the only powered
  cell (4h): **gap(k=3) = −0.0045, 95% CI [−0.070, +0.031] includes 0** (p=0.61) → L5 `no_causal_gap`
  — the bounded 180-bar retrospective view buys **no** selection info the live view at `k=3` lacks.
  Gap point estimate ≤ 0 at every k (k=12 borderline: CI upper +0.0004, p=0.97, attributed to the
  wider-frame recompute — reported as sensitivity, does **not** trip the direction guard). 1M/1w/1d
  underpowered (2/0/7 test-pos), context only. Row exclusions trivial (≈0.8%). **No reproduction, no
  edge/behaviour claim** (L6). Harness `research/selection_learning_gap.py`; summary +
  `cells/*.json` gitignored/regenerable; gates green (ruff/format/557 pytest cov 74.83%/bounds).
  Re-run (deterministic, resume-able, frozen data — do **NOT** `data.fetch --refresh`):
  `PYTHONUNBUFFERED=1 uv run python -u -m fibengine.research.selection_learning --w-gap`.
- **Stage-1 per-pivot diagnostic — BUILT + RUN → `no_pivot_signal_above_prominence` (2026-06-24).**
  Commit 2 of the [Stage-1 LOCK](reviews/btc-fib-selection-learning-stage1-lock-20260624.md) (`00a97d7`),
  executed verbatim. New `research/selection_learning_stage1.py` (+12 tests) — own `--stage1` CLI, **no
  code added to byte-capped `selection_learning.py`**. The decomposition answers cleanly:
  **DETECTION is NOT the bottleneck** (4h recall **= 0.902**; ≥0.90 at every TF) but **RANKING adds
  nothing over prominence** at the live `k=3` headline (lift **= +0.0228, 95% CI [−0.0354, +0.0790]
  includes 0**, p=0.22). Powered (117 test-pos), R≥0.50, CI includes 0 → per S7
  **`no_pivot_signal_above_prominence`**: the **lone pivot** carries no OOS ranking signal above
  prominence; the Stage-2 ceiling is a **selection/gestalt** problem (the leg-level `cleanliness` is
  structurally absent here), not a coverage one. The incidentally-powered 1d context cell agrees (lift
  negative −0.162, CI includes 0). **Sensitivity (honest):** at `k=12`, `scale_confluence` (wider-frame
  `k*=12`) lifts +0.0690, CI [+0.0029, +0.1335] excludes 0 — **not** the locked primary, does **not**
  change the verdict; same wider-frame phenomenon W-gap flagged at k=12. **Diagnostic floor, not
  headline; no reproduction/edge/behaviour claim** (S8). 1M/1w underpowered (9/1 test-pos), context.
  [Results](reviews/btc-fib-selection-learning-stage1-results-20260624.md); summary + `cells/*.json`
  gitignored/regenerable. Re-run (deterministic, frozen data, **no `--refresh`**):
  `PYTHONUNBUFFERED=1 uv run --no-sync python -u -m fibengine.research.selection_learning_stage1 --stage1`.
- **2026-06-24 Fib SELECTION-LEARNING campaign CHECKPOINT (docs-only).** Consolidates the five runs
  (Stage-2 → prominence-family → k-sweep → W-gap `no_causal_gap` → Stage-1 `no_pivot_signal_above_prominence`):
  modest OOS baseline-robust `cleanliness` lead (low AP; 4h-only powered) + the open CRUX — genuine
  signal vs **detector/anchoring artifact**? [Checkpoint](reviews/btc-fib-selection-learning-checkpoint-20260624.md).
- **2026-06-24 Fib SELECTION-LEARNING `cleanliness` artifact-probe — BUILT + RUN → inflationary
  artifact NOT supported on 4h, but marginal/non-replicating → "investigate, not a finding".**
  Commit 2 of the [artifact LOCK](reviews/btc-fib-selection-learning-artifact-lock-20260624.md)
  (`b533385`), executed verbatim. New `research/selection_learning_artifact.py` (+13 tests; own
  `--artifact` CLI, no code into byte-capped `selection_learning.py`). Fidelity OK (4h reached
  **0.860**, reproduces Stage-2 ~0.83). **Surfacing:** reached legs *less* clean than unreached (gap
  **−0.0557**, CI [−0.1150, −0.00095] excludes 0 below) → locked guard **`inverse_surfacing`** (marginal:
  CI upper −0.00095). **Snapping:** snapping to detector pivots *lowers* cleanliness (gap **−0.0219**,
  CI [−0.0320, −0.0102]) → locked guard **`snapping_deflates`**. Both guards point **against** the
  inflationary detector-artifact hypothesis — but it is **NOT `artifact_risk_reduced`** (both CIs
  *exclude* 0, not include) and the snapping effect **flips sign on 1d** (+0.0222, `detector_artifact_
  supported` context) → **TF-dependent, investigate, no sign/positive claim.** **Combined: A7 did not
  pre-register a powered direction-guard outcome → no new combined verdict; harness emits a descriptive
  `meta:` status (NOT `inconclusive_underpowered`, the cells are powered). The lock was NOT changed.**
  Matched-null / new universe **NOT built** (gated, A8). Crux stays OPEN, sharper investigate-target
  (why reached/snapped legs are less clean; why snapping flips sign by TF). No reproduction/edge/
  behaviour/Genesis/1H/ETH. [Results](reviews/btc-fib-selection-learning-artifact-results-20260624.md);
  summary + `cells/*.json` gitignored/regenerable. Re-run (deterministic, frozen data, no `--refresh`):
  `PYTHONUNBUFFERED=1 uv run --no-sync python -u -m fibengine.research.selection_learning_artifact --artifact`.
- **2026-06-24 Fib SELECTION-LEARNING artifact-MECHANICS — BUILT + RUN (descriptive-only, NO verdict).**
  Commit 2 of the [mechanics PLAN](reviews/btc-fib-selection-learning-artifact-mechanics-plan-20260624.md)
  (`70174df`), executed verbatim. New sibling `research/selection_learning_artifact_mechanics.py`
  (+`--artifact-mechanics` CLI, 3 descriptive fields on `ArtifactRow`, +8 tests). Findings (descriptive,
  no claim): **(M1)** the 4H "reached less clean" gap is a **span/duration confound** — Spearman(clean,
  span)=**−0.69**, reached longer (median 5 vs 3 bars), and the −0.056 gap **vanishes when conditioning
  on span** (short-span +0.003, long-span −0.017): composition effect, not detector cleanliness-
  preference. **(M3)** 4H snapping deflates because pivots sit **outside** human anchors → span extends
  (33% extend vs 1.6% shrink); the **1D flip** is a TF-dependent geometry (1D shrinks 10% **and** the
  span-delta↔clean Spearman flips −0.19→+0.18) — *why* the local relationship reverses stays an **open
  investigate-target**. **No verdict, no lock change; artifact-probe reading unchanged; crux OPEN.**
  Population guard: M1 ≠ Stage-2 lead (different population). No matched-null/new universe/Genesis/1H/
  ETH/refresh. [Mechanics note](reviews/btc-fib-selection-learning-artifact-mechanics-20260624.md);
  mechanics_summary.json gitignored/regenerable.
- **2026-06-24 Fib SELECTION-LEARNING snapping FLIP mechanics — BUILT + RUN (descriptive, no verdict).**
  Narrow follow-up: *why does snapping↔cleanliness flip sign 4H↔1D*. Extended the mechanics module
  (+net/path decomposition, 2 more `ArtifactRow` fields, +2 tests). On the moved-snap domain it is a
  **net-vs-path channel reversal** consistent with **candle granularity**: 4H grows **path** > net
  (rel_path 0.231 > rel_net 0.181, 63% path-dominated → clean down); 1D grows **net** > path (0.063 >
  0.025, 60% net-dominated → clean up). Explains the **measurement geometry**, kept apart from any
  selection-claim; **no verdict, no lock change, crux OPEN**. No matched-null/universe/Genesis/1H/ETH/
  refresh. [Flip note](reviews/btc-fib-selection-learning-artifact-mechanics-flip-20260624.md).

**Next work requires a separate explicit GO. No W/gap, no Stage 1, no new sensitivity, and no Genesis
may be started automatically.** Parked (test-only, separate GO): lock the facit-discipline refusal
branches in `selection_learning.py:118-142` (currently uncovered — see audit).

## Verification Snapshot

- `data/labels/human_fib/bitfinex/BTC-USD/1M/` — **9** base `fib_*.json` (log scale).
- `data/labels/human_fib/bitfinex/BTC-USD/1w/` — **21** base `fib_*.json` (log scale).
- `data/labels/human_fib/bitfinex/BTC-USD/1d/` — **67** base `fib_*.json` (log scale);
  source-facit complete, verified 2026-06-11.
- `data/labels/human_fib/bitfinex/BTC-USD/4h/` — **365** active base `fib_*.json` (log scale;
  366 drawn 2026-06-12, 1 superseded via 20250506 dedup 2026-06-15). Coverage 2017-01-05 →
  2026-06-05.
- `experiments/review/weekly_source_fib_map/` and `…/weekly_source_fib_zoom/` —
  generated charts (gitignored; regenerate via the two new CLIs).
- `data/raw/bitfinex/BTC-USD/1M/limit_500.csv` — 115 bars (2016-12 .. 2026-06),
  fetched with `--config config/settings.expansion.yaml` to cover old anchors.
- `experiments/review/fib_level_events/` — active 1M pack `human_fib_review_20260609T135548Z`.
- Pre-reset archive (local disk; git tracks manifest only):
  [MANIFEST.md](../../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/MANIFEST.md)

## Open Questions

- Minimum monthly fib count before 1W mapping?

## Status — BTC/Fib behaviour/backtest line PAUSED / CLOSED (2026-06-16, reviewed PASS)

Commit `f4e96f1` reviewed **PASS / CLOSED**. Final conclusion (both studies):

- **Unconditioned** [Behaviour Event Study](reviews/btc-fib-behaviour-event-study-results-20260616.md):
  **no signal.**
- **Context-Conditioned** [Study](reviews/btc-fib-context-conditioned-study-results-20260616.md):
  **no candidate.**
- **Fib does not beat the placebo/swing baselines** on the current BTC corpus. The swing baseline
  **matches or beats** fib; the weak level reaction is **generic horizontal structure, not
  Fibonacci-specific.**
- **Strategy sanity-check: not authorised, not run.**

**Discipline (binding):** do **not** re-run these studies on the same BTC data with tweaked
parameters. Any future behaviour test must be a **new prereg on fresh data** or a **materially
different question**. **No active next implementation is authorised.**

### Future possible tracks (listed only — none started, none authorised)

- Fresh-data validation on other symbols/timeframes — **requires a new prereg.**
- Source-label quality review / correction-candidate cleanup.
- Non-fib **horizontal structure** (B-1) — **built, run, CLOSED-NULL** ([results](reviews/btc-horizontal-structure-event-study-results-20260617.md)); any re-test = **new prereg on fresh data** or lower-multiplicity single-subject design (B-1 had low power).
- Separate visual / research **tooling** improvements.
- **Genesis/Fib remains paused** unless explicitly reopened.

**Milestone:** Issue #32 top-3 complete + pushed (gallery `8f1e7a8`, ledger `d6ab9ec`,
overlap detector + anchor convention `84b42db`). local == origin, tree clean, source-fib
JSON unchanged, no new deps, no artifacts committed.

**#32 tooling track — all DONE** (single-fib declutter edit-mode, `20171228` correction,
chart-regression spike + #F render_summary/golden snapshots; detail in [log.md](log.md)).
**Corpus declared clean and
locked** (integrity capstone 2026-06-15:
[`reviews/btc-source-fib-corpus-integrity-20260615.md`](reviews/btc-source-fib-corpus-integrity-20260615.md)).
**MTF confluence track CP1–CP3 — CLOSED.** CP1 ([table](reviews/btc-mtf-confluence-table-20260615.md))
+ CP2 ([sensitivity](reviews/btc-mtf-confluence-sensitivity-20260615.md)) + CP3
([capstone](reviews/btc-mtf-confluence-atlas-cp3-20260615.md)) done — 5 cards, 3 archetypes,
**all human-approved**. [Decision note](reviews/btc-mtf-confluence-interpretation-decision-20260615.md):
confluence is **geometry, not edge proof** → **stop the MTF track**. **Fork written up
(docs-only):** [Phase 0 prereg](reviews/btc-fib-to-genesis-v2-phase0-prereg-20260615.md) registers
one falsifiable behaviour question (causal confluence zones vs placebo/naïve levels, OOS) +
leakage manifest, baselines, time-split holdout, stop/go; [Phase 1 spec](reviews/btc-fib-to-genesis-v2-phase1-feature-export-spec-20260615.md)
(zone+bar tables, `known_after_ts` rule) **reviewed PASS — Phase 1 closed as docs-only contract**. **Phase 2 (dummy-file test) — reviewed PASS / CLOSED 2026-06-16** (authorised narrow slice,
commit `68dc006`): `research/feature_contract.py` + committed dummy CSVs prove the contract
validates mechanically with no real export and no Genesis touch
([Phase 2 report](reviews/btc-fib-to-genesis-v2-phase2-dummy-contract-20260616.md)). **Stopped**
— any real export or Genesis touch needs a fresh go; first define a feature-column **nullability
policy**. No Phase 3.

**Deferred:** 1H source labeling — 4H is the lowest active timeframe; fetch 1H cache first
(`data.fetch --timeframes 1h`). Separate decision before starting.

## Guardrails

- Do not treat archived ledgers/reviews as current evidence.
- Do not treat `*_candidate` as facit.
- No ETH/SOL analysis until BTC protocol sign-off.
- No auto-fib or trading signals.

## Startup on another machine

Use this checklist when resuming from a home computer or any machine that does
not have the current working tree.

### Before leaving the current machine

- All code, tests, wiki, and data changes committed and pushed (`git status` clean).
- Gitignored review artifacts (`experiments/review/`) copied as a ZIP if wanted
  (optional — see restore step below).
- No required local-only state remains: committed facit (`fib_*.json`,
  `review_windows.yaml`) and wiki docs are the source of truth.

### On the new machine

```bash
git pull
uv sync --extra dev
uv run pytest -q
uv run python scripts/check_repo_bounds.py
```

### BTC/USD candle-cache setup

`data/raw/` is gitignored — fetch it fresh:

**Bash:**
```bash
uv run --no-sync python -m fibengine.data.fetch \
  --symbols BTC/USD \
  --timeframes "1M,1w,1d,4h" \
  --refresh \
  --config config/settings.expansion.yaml
```

**PowerShell:**
```powershell
uv run --no-sync python -m fibengine.data.fetch `
  --symbols BTC/USD `
  --timeframes "1M,1w,1d,4h" `
  --refresh `
  --config config/settings.expansion.yaml
```

### Labeling preflight

Confirms cache is complete for all active TFs before opening the labeling tool:

**Bash:**
```bash
uv run --no-sync python -m fibengine.labeling.preflight \
  --symbol BTC/USD \
  --timeframes "1M,1w,1d,4h,1h" \
  --config config/settings.expansion.yaml
```

**PowerShell:**
```powershell
uv run --no-sync python -m fibengine.labeling.preflight `
  --symbol BTC/USD `
  --timeframes "1M,1w,1d,4h,1h" `
  --config config/settings.expansion.yaml
```

Expected: 1M/1w/1d/4h pass; 1h FAIL (cache not fetched yet — deferred).

### Optional: restore local review artifacts

`experiments/review/` is gitignored (regenerable charts/CSVs). The completed 1M packages can
be restored locally from `btc-1m-reaction-review-artifacts-20260611.zip` (`unzip … -d .`) if
wanted — **optional**; committed `fib_*.json` + `review_windows.yaml` are the source of truth.

### Windows / Symantec SEP note

Use `uv run --no-sync` after the initial `uv sync` and set `PYTHONDONTWRITEBYTECODE=1`
(user-scope) to cut SEP scan surface. Full SONAR / Auto-Protect discipline + the env-var
commands: [CLAUDE.md](../../CLAUDE.md) Gotchas.

### Resume point

- **BTC/USD 1M phase is complete.** 9 source fibs, 1D + 4H reaction review
  approved 2026-06-11. Do not resume unless an explicit bug or gap is found.
- **BTC/USD 1W source-fib phase is complete.** 21 source fibs verified;
  visual confirmation via `weekly_source_fib_map` (combined 1W/1D/4H) and
  `weekly_source_fib_zoom` (per-fib 4H). Combined 4H is too compressed — use
  the per-fib zoom for 4H. Do not resume unless a bug or gap is found.
- **BTC/USD 1D phase is complete.** 67 source fibs (2017-01-05 → 2024-12-20) and
  4H reaction-review (2026-06-12). 1816 4H interactions, 90-day windows.
  Summary: `docs/research_wiki/reviews/btc-1d-reaction-review-cycle-20260612.md`.
  Do not resume unless a bug or gap is found.
- **BTC/USD 4H source-fib phase is complete.** 366 source fibs (2017-01-05 → 2026-06-05),
  up=169 / down=197, 366/366 schema PASS (2026-06-12). Do not resume unless a bug or gap
  is found. 4H is the current lowest active timeframe (1H paused).
- **4H visual confirmation Tier 1 + Tier 2 sample-pass complete** (2026-06-15). Tier 1:
  `research/fourh_source_fib_map.py`, 11 annual groups, 366/366 drawn. Tier 2:
  `research/fourh_source_fib_zoom.py`, 103+37 fibs rendered; first manual sample-pass (8
  fibs) shows no suspicious labels. Two watchlist items: `20171228` (short-span) and
  body/close vs wick convention (undocumented). Do not start with 1H. Do not start with
  reaction-review. Review:
  [`reviews/btc-4h-tier2-sample-review-20260615.md`](reviews/btc-4h-tier2-sample-review-20260615.md).
- Do not auto-fib. Do not infer anchors. Keep the four flows distinct: 1M source /
  1M→1W projection / true 1W source / true 1D source fibs.

## Links

- [BTC-first protocol](../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)
- [Research wiki index](index.md)
- [Human fib annotation](../labeling/HUMAN_FIB_ANNOTATION.md)
- [Archive manifest](../../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/MANIFEST.md)
