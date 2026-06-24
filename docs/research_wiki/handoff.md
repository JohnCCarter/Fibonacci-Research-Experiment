# Current Handoff

This page is the current working context for future agents. It is editable; the
append-only trail lives in [log.md](log.md).

## Current Focus

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

## Recent Changes

- **2026-06-22 Fib SELECTION-LEARNING W-gap study — BUILT + module split, RUN PENDING (home).** Commit 2 of side-quest #1, built to the [W-gap LOCK](reviews/btc-fib-selection-learning-w-gap-lock-20260622.md) (`4f47d8e`): `gap(k)=AP(retro-W)−AP(live-k)` on identical rows, embargo=W, L5 verdict. New `research/selection_learning_gap.py` (+5 tests); W-gap code split out to keep `selection_learning.py` under the §6 size cap (was 995 lines); flushed-stderr `_progress` logging in `build_candidates`+`build_retro_features` so a long run is never blind (result-neutral). **Run NOT executed** — inherent ~2-3h per-endpoint-detect cost on the ~20k-bar 4h frame (leakage-bearing truncation, no legal shortcut); to run at home (see Next tracks). No gap results, no verdict. Commit `884d4c0`, gates green (pytest 549, cov 75%).
- **2026-06-18 Fib SELECTION-LEARNING k-sweep {0,3,6,12} (4h) → `k_stable_live_selection_signal`.** Mandatory confirmation-buffer sweep (live-only), locked prominence-FAMILY survival rule (powered AND CI excludes 0 vs **every** §6 baseline — magnitude + prominence A/B). **k=0 degenerate** (0 candidates, reachable 0.0, unpowered — *not interpretable*, excluded); **k=3/6/12 all powered and survive** the locked family (`p_one_sided lift≤0 = 0/2000` throughout; lowest CI floor k=12 vs prom-sum 0.025). ≥2 survivors → cross-k verdict **`k_stable_live_selection_signal`**: the lead is **not** a narrow-buffer artifact. **Modest framing holds:** `cleanliness` still dominates (~0.20) at every powered k; at k=12 `scale_confluence` enters at ~0.13 only as a **secondary hint** (causally available there), not a second pillar; AP rises only 0.057→0.066, far under the 0.83 ceiling — **still single-feature, NOT a reproduction, no edge/behaviour/backtest/Genesis claim**; 1M/1w/1d **underpowered, not refuted**. Code+tests `ea6c2ea` (gates green). [Results](reviews/btc-fib-selection-learning-results-20260618.md).
- **2026-06-18 Fib SELECTION-LEARNING prominence-baseline sensitivity (4h) → `survives_prominence_family`.** Locked pre-run (A=summed endpoint prominence = `prominence` feature col; B=max endpoint prominence) + locked verdict rule. Same universe/viewport/k/ε/split/model — only baseline rule differs. Model AP-lift robust vs **all three** §6 baselines: magnitude [0.023,0.120], prominence-A +0.043 [0.018,0.104], prominence-B +0.049 [0.021,0.116]; every CI excludes 0, 0/2000 ≤ 0. Sanity: prominence baselines beat magnitude (as expected); model beats both. Weights unchanged → **`cleanliness` still carries the lift** (0.20). So the lead is **not** a magnitude- or prominence-artifact — but still single-feature, low absolute AP (0.057 vs 0.83 ceiling), **not a reproduction**, no edge claim; 1M/1w/1d underpowered. Open: is `cleanliness` a detection/anchoring artifact? [Results](reviews/btc-fib-selection-learning-results-20260618.md).
- **2026-06-18 Fib SELECTION-LEARNING Stage-2 headline + AP-lift inference → MODEST single-feature lead on 4h (not a reproduction).** `research/selection_learning.py` (+18 tests): causal truncate-and-whitelist at `anchor_b+k`, re-detected candidate universe, ε-match, purged split, numpy logreg vs §6 **magnitude** baseline, pooled-AP (A5.1). **Only 4h powered.** Decision-point cluster bootstrap (2000×, by `anchor_b` group): lift +0.052, **95% CI [0.023, 0.120] excludes 0** (0/2000 ≤ 0) — robust vs magnitude, OOS. **But** the interpretable weights show the lift is **carried almost entirely by `cleanliness`** (0.20 vs prominence 0.07, structure_alignment ≈ 0): human legs are *cleaner/more efficient*, **not** a multi-feature reproduction. Beats **magnitude only** (prominence baseline untested); AP 0.057 vs 0.83 ceiling = low agreement; 1M/1w/1d **underpowered, not refuted**. **Recommended next: prominence-baseline sensitivity on 4h** (does the cleanliness lift survive a stronger §6 rule?). [Results](reviews/btc-fib-selection-learning-results-20260618.md). Artifacts gitignored.
- **2026-06-18 Fib SELECTION-LEARNING §12 addendum FROZEN (docs-only, blind to output).** Step-2 of the two-step gate: reuses the engine's **8 existing interpretable features** (no new ones), tags each with a **minimum confirmation buffer `k*`** (0 / 3 / 12 / ∞) — refining §5's binary so the mandatory `k`-sweep isn't vacuous; `recency` dropped from the live model (`k*=∞`, dataset-end ref); exclusivity #4 = set-level over `structure_window=6` base-pivot chunks (`k*=3`, no parent-degree boundaries); ε **reused** from `EvaluationConfig` (`time_tol=3`, `price_tol=0.5` ATR, blindness defense); `k`-sweep {0,3,6,12} + `W` per TF + **single primary cell at `k=3`** (base detector confirmation). **Still gated: §12.3 separate explicit go before any build/run.** [Addendum](reviews/btc-fib-selection-learning-addendum-20260618.md).
- **2026-06-17 NEW LINE pre-registered — Fib SELECTION-LEARNING (docs-only, gated).** Different question from the closed behaviour/B-1 nulls: *can a model reproduce how the human selects swings/ranges* (labels as facit, **no edge/backtest/Genesis**). Stage 2 leg/range gestalt (5 components) = target, Stage 1 per-pivot = diagnostic; live-equivalent vs **bounded** retrospective viewport → causal-availability gap; binding feature-provenance rule; one primary cell + coverage ceiling. Two-step gate. [Prereg](reviews/btc-fib-selection-learning-prereg-20260617.md).
- **2026-06-17 B-1 horizontal-structure study — BUILT + RUN → NULL (closed).** SENARE-1 e-value (conditional 2×2 safe test) + 3-subject harness (swing/round/prior-extreme vs matched random-walk null), all pins locked pre-run. `any_robust=False` on all 12 cells; only swing edges the null (e=1.70 — not even marginal; e-Holm needed E≈240 → low power). Generic structure not special vs a random walk; §10 sanity-check not run. Commits `474f320`→`44e63fa`. [Results](reviews/btc-horizontal-structure-event-study-results-20260617.md).
- **2026-06-17 External-pattern-scan absorption — landed on `main`** (PR #33→main, merge-commit;
  plan `clever-yawning-catmull.md`). NU (docs): standing
  [prereg addendum](reviews/horizontal-structure-prereg-addendum-20260617.md) (random-walk control /
  anytime-valid re-looks / embargo named as purged-CV). DELAR (code): synthetic RW baseline,
  uncertainty-ordered worklist (`--by-uncertainty`), fail-closed swing-label validation. SENARE gated.
  Review fixes: P1 windowed-save facit-safety, P2 level-events now log-scale. Sec (PR #34):
  cryptography→49.0.0 (GHSA-537c-gmf6-5ccf). No facit/signal/auto-fib touch.
- **2026-06-16 BTC/Fib studies — BOTH NULL, reviewed PASS / CLOSED** (commit `f4e96f1`, Lean Fib).
  **(1) Behaviour event study:** fib ≈ placebo ≈ swing (4h reject 0.78/0.80/0.84, p=0.63/0.19).
  **(2) Context-conditioned** (continuous MFE−MAE, rank-perm + Holm; contexts trend + deep
  0.618/0.786): no context passes — fib beats *random placebo* only nominally (p=0.042/0.056, fails
  Holm) and **never beats swing**. **Insight:** any faint level-reaction is generic horizontal
  structure, not Fibonacci. Both gates fail → **no strategy work.** Code:
  `fib_behaviour_event_study.py` (19 tests) + `fib_context_conditioned_study.py` (17); preregs +
  results `reviews/btc-fib-*-20260616.md`.
- **2026-06-16 Fib → Genesis V2 Phase 2.5 feature nullability policy — reviewed PASS / CLOSED**
  (docs-only) — pins how the future bar feature table represents empty values (3 states; distances
  null not 0/inf; empty-meta ⇔ no-known-zone; dense-table + no-imputation consumer rules).
  Precondition for any real export. **Open (non-blocking):** is `has_robust_4tf_zone_nearby`
  log-price- or ATR-thresholded (latter ⇒ warmup-null / availability flag).
  [Policy](reviews/btc-fib-to-genesis-v2-feature-nullability-policy-20260616.md).
- **2026-06-16 Fib → Genesis V2 Phase 2 dummy contract test — reviewed PASS / CLOSED** —
  mechanical contract/dummy test **inside Fib only** (not export, not Genesis integration).
  `research/feature_contract.py` (stdlib) validates two committed dummy CSVs vs the Phase 1
  schema (join keys, causality, knowability floor, 1H + feature/metadata fail-closed). No fib
  computation, no Genesis touch. 20 tests; gates green. Commit `68dc006`; **human review PASS**
  2026-06-16. Follow-up for any *real* export: define a **nullability policy** for feature
  columns. [Report](reviews/btc-fib-to-genesis-v2-phase2-dummy-contract-20260616.md).
- **2026-06-15 MTF confluence CP1–CP3 CLOSED + interpretation/decision note** — first atlas
  pack done (5 cards, 3 archetypes, all **human-approved**): c001 robust fixed-band 4-TF; c002
  chaining-dependent contrast (NOT tight); c004/c006/c007 zero-span exact-price 3-TF.
  [Decision note](reviews/btc-mtf-confluence-interpretation-decision-20260615.md): confluence
  is **geometry, not edge proof** → **rec: stop MTF track**; next = pause Fib or new question.
- **2026-06-15 Structural chart-contract snapshots (#F)** — `research/render_summary.py`
  (stdlib): stable text summaries of map/zoom/gallery renders + golden JSON under
  `tests/research/snapshots/`. Automatic structural regression; no PNG baselines/deps.
- **2026-06-15 20171228 source fib corrected** — preview-first flow: anchor_a moved
  2017-12-28T20:00 @ 13611 → 2017-12-28T08:00 @ 13145 (candidate_1). Only anchor_a + levels
  changed; anchor_b/fib_id unchanged; guard PASS; ledger candidate → corrected. Closes the
  declutter→correction→ledger track. [Report](reviews/btc-4h-fib-20171228-correction-20260615.md).
- **2026-06-15 Issue #32 top-ROI tooling — DONE** (declutter edit-mode, overlap detector, review
  ledger, artifact gallery; all stdlib). Detail in [log part 1](log-archive-btc-postreset-part1.md).
- **2026-06-15 4H Tier 1 + Tier 2 visual reviews — complete** (11 groups; `20171228` corrected;
  corpus clean). Archived to [log part 1](log-archive-btc-postreset-part1.md).
- **2026-06-08→06-12 source-fib milestones (archived)** — 1M/1W/1D/4H source phases, reaction
  reviews (1816 interactions), 4H Tier 1 maps, Addendum 2 golden-zone retirement (#30), log-scale
  + profile fix + monthly-first reset. Detail: [log post-reset part 1](log-archive-btc-postreset-part1.md)
  + [log.md](log.md); current counts in Verification Snapshot below.

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
- **2026-06-24 Fib SELECTION-LEARNING campaign CHECKPOINT (docs-only, no new claim).** Consolidates
  the five committed runs (Stage-2 → prominence-family → k-sweep → W-gap `no_causal_gap` → Stage-1
  `no_pivot_signal_above_prominence`): what we KNOW (modest, OOS, live-available, buffer-stable,
  baseline-robust `cleanliness` lead in the leg gestalt; low absolute AP; 4h-only powered) and the
  single open CRUX (is `cleanliness` a genuine signal or a **detector/anchoring artifact**?). Frames
  the next-step choice A (exclusivity / artifact diagnostic) / B (detector-independent anchor-probe) /
  C (pause + theory) — **none started**. [Checkpoint](reviews/btc-fib-selection-learning-checkpoint-20260624.md).
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
- **2026-06-24 Fib SELECTION-LEARNING artifact-MECHANICS investigation — PLAN locked (docs-only),
  RUN PENDING separate GO.** Door (i) from the checkpoint: explain the *mechanics* behind the
  artifact-probe (why 4H reached-legs less clean; why 4H snapping lowers cleanliness; why snapping
  flips sign on 1D), **descriptive-only on frozen data — NO verdict, NO claim, no lock change**. Plan
  [artifact-mechanics PLAN](reviews/btc-fib-selection-learning-artifact-mechanics-plan-20260624.md):
  feasible cleanly (deterministic from frozen data + locked detection) but NOT answerable from existing
  aggregates → needs a small descriptive pass recording per-leg {span_bars, magnitude_atr,
  snap_span_delta}. Headline object = the **4H↔1D `snap_span_delta` asymmetry** (detector granularity
  vs human-anchoring precision), not the partly-arithmetic span↔cleanliness correlation. Pre-locked
  stats (P3) + population guard (M1 reached/unreached ≠ Stage-2 lead) + marginal-gap caveat. No
  matched-null/new universe/Genesis/1H/ETH/refresh. Commit 2 needs a separate GO.

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

**Bash:**
```bash
git pull
uv sync --extra dev
uv run pytest -q
uv run python scripts/check_repo_bounds.py
```

**PowerShell:**
```powershell
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

`experiments/review/` is gitignored. The completed 1M review packages can be
restored from the ZIP if you want the charts and CSV files locally:

**Bash:**
```bash
unzip btc-1m-reaction-review-artifacts-20260611.zip -d .
```

**PowerShell:**
```powershell
Expand-Archive -Path btc-1m-reaction-review-artifacts-20260611.zip -DestinationPath .
```

This is **optional**. The committed repo files (`fib_*.json`, `review_windows.yaml`,
`btc-1m-reaction-review-cycle-20260611.md`) remain the source of truth.
Artifacts under `experiments/review/` are local convenience files only.

### Windows / Symantec SEP note

Plain `uv run` triggers a full `.venv` rebuild scan on each invocation when
Symantec Auto-Protect is active. Mitigate:

- Prefer `uv run --no-sync` for all run commands after the initial `uv sync`.
- Set `PYTHONDONTWRITEBYTECODE=1` (user-scope env var) to suppress `.pyc`
  generation and reduce scan surface.

**PowerShell — set env var for current session:**
```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
```

**PowerShell — set permanently (user scope):**
```powershell
[System.Environment]::SetEnvironmentVariable("PYTHONDONTWRITEBYTECODE", "1", "User")
```

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
