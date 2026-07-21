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
| 4 | **4H** | **Complete** — 371 active source fibs (365 + 6 grow-facit 2024–2026; 1 superseded 20250506 dedup) |
| 5 | 1H | Structure-engine substrate (1h cache fetched bounded-recent 2024–2026); source-labeling deferred |

**ETH/USD:** blocked until BTC protocol approved.

## Checkpoint 2026-07-21 (350k save-point, autonomous session)

**Observed:** cascade SIGNED · chain-clustering → `no_chain_clustering` · sequential-feature →
`no_sequential_feature_signal` (AP 0.071→0.053; 17.6 % vs 3.8 % — signal exists, doesn't
convert) · negative-audit → 75 % coverage-weak negatives · overwrite-guard shipped ·
1w 20-vs-21 = collision overwrite · 7 misclicks candle-verified. **Sequential axis bounded
(3 locked results): chaining = byproduct of the zigzag rhythm, not a missing driver.**
**Signed 2026-07-21 (mobile):** both results SIGNED; `1w_20170316` = keep nesting. **D1 dialog:**
5 macro candidates approved; owner teaching = sub-impulses are drawable legs too → prenotes +
open questions in [`scratchpad/desert_d1_capture_prenotes.md`](../../scratchpad/desert_d1_capture_prenotes.md).
**Next lever: contrastive capture (#42, batch 1 + desert batch 2).**

## Next Step — degenerate-fib fix (home GUI) + contrastive capture — 2026-07-21

**CASCADE probe SIGNED OFF 2026-07-21** (`sequential_origin_signal` on 4h: H1a **0.256** vs
permutation-null **0.005**, p < 0.0005, gap CI [0.205, 0.298], N=363; ~all EXACT chains 76/93,
both directions, 1d+1w agree, 1M nothing. **~1 in 4 origins = previous endpoint → a component of
selection, NOT the selector**, 74% unchained).
[Results](reviews/btc-fib-cascade-conditioning-probe-results-20260720.md) — line **complete**;
next cascade work (P3 data model etc.) stays gated behind a separate GO.

**Degenerate fibs classified 2026-07-21: MISCLICKS — fix on the home machine (GUI).** Owner call:
the 7 same-candle fibs (`a.time == b.time`, all direction=down, spans 3–26 %) are **not**
intentional single-candle legs. Worklist — redraw with correct anchors or delete, per fib, in
`labeling.tool`:

| TF | Fib | a → b (same candle) |
|----|-----|---------------------|
| 1d | `20210907T000000` | 52888 → 43220 |
| 4h | `20170209T120000` | 1064.5 → 936.34 |
| 4h | `20170310T200000` | 1293 → 958.5 |
| 4h | `20171107T120000` | 7220 → 6948 |
| 4h | `20200316T120000` | 5193.7 → 4563.8 |
| 4h | `20200802T040000` | 12097 → 10548 |
| 4h | `20230223T080000` | 24493 → 23659 |

After fixing: re-run `corpus_manifest` to relock `MANIFEST.json` (the fail-closed verifier will
otherwise DRIFT), regenerate events for touched fibs, and note the new counts here. Agents must
**not** redraw/delete these themselves (facit discipline: no inferred anchors).

---

**Previous Next Step (still active after sign-off): RESUME contrastive capture toward ≥30 — 2026-07-02**

**MEASURED** (`scratchpad/measure_4h_down.py`, out-of-sample on all 201 4h-DOWN human legs, LOCKED band):
engine origin **sits only 43 %** (86/201, 95 % CI ~36–50 %); leg accepted 30 % (61/201). Miss decomp: **75
wrong-swing** (price >2 %, bar-tolerance-invariant = 37 %) + 24 bar-units-only. Origin-sits ∈ **[43 % locked,
55 % bars-ignored]**, CI tops at 50 % → does NOT sit broadly. On 1h calibration it re-found 4/4 → classic
overfit; the single most-prominent-high rule is not Chamoun's selector on ~half the legs (HO-B pattern at
scale). Validity-reviewed (concerns, non-blocking: acceptance bar-band not TF-rescaled = disclosed; no
leakage, no post-hoc tuning, corpus is genuine human facit). **Fork answered → the targeted contrastive set
(#42) IS justified. NEXT:** resume drawing toward ≥30 windows (`scratchpad/annotation_batch1.md`, tool
`--annotate-selection`); at ~10 check reason/tag consistency before grinding to 30. Memory
`project_capture_friction_bottleneck.md`.

---

**STRUCTURE-MEMBERSHIP thread CLOSED (all 4 features null on selection) — 2026-07-01**

**2026-07-01: the structure-engine substrate question is answered — STOP the thread.** Four structure/
detection features, each with a conservative null + adversarial verification, all NULL on *selection*:
**Directional-Change** (saturation → pooled W+D p=0.099), **BOS/CHoCH** (definitional break-rate → BOS|broke
p=0.16), **structure_alignment on the powered COMMITTED corpus** (trend-termination TAUTOLOGY → collapses vs a
two-sided-plausible null, 4h 0.400 vs 0.398 p=0.55, anchor_b too), **prominence** stays the Stage-1/2 survivor.
**Detection & structure-membership are NOT the bottleneck — SELECTION is** (echoes `no_pivot_signal_above_prominence`).
Machine-local memory `project_structure_engine_topdown.md`.

**DECOMPOSITION thread (2026-07-01) — Chamoun's rule split generate → select; BOTH halves DONE, LANDED.**
His rule: leg = retracement extreme "1" → *next fresh* impulse endpoint "0", a *clean directed impulse*. Probes
(scratchpad `impulse_leg_generator_coverage.py`/`endpoint_rank_probe.py`/`origin_rank_probe.py`): admissibility
(fresh/clean, k_between=0) holds on **BOTH** anchors but is **definitional**; the **positive** rule for WHICH
admissible extreme is **weak-to-absent** (origin flat-null p≈0.45/0.59, NOT prominence; recency DEAD); continuation
gap = **SCALE**. Six probes bound what selection is NOT → **NON-geometric**. Detail:
[style doc](reference/chamoun-daily-fib-style.md).
**CASCADE probe (2026-07-01→02) — DATED then CV probe DEAD.** 1w cascade drawn + dated (`scratchpad/
cascade_1w_{working,snap}.py`; BOTTOM_LEFT=2020-21, furthest=downtrend=RIGHT). CV probe DEAD (advisor): 7
legs, duration already inconsistent, grouping = "ingen aning" — kept as durable facit, redirected to
contrastive-annotation input (→ motivated the capture tool). **Open:** 20 M/W/D facit NOT promoted; **TZ:** Europe/Stockholm.

## Recent Changes

- **2026-07-21 AUTONOMOUS SESSION (owner blanket GO): chain-clustering probe RUN →
  `no_chain_clustering` (advisory) + implicit-negative audit + overwrite-guard + 1w mystery
  solved.** (1) Sequential axis: chaining is NOT serially clustered under the confound-guarded
  gate (full-array p=0.022 alone would have over-claimed; hub-guard p_sf=0.061 → null; reviewer's
  pre-run A1 was decisive) → per-leg sequential feature suffices, no regime model.
  [Results](reviews/btc-fib-chain-clustering-probe-results-20260721.md) pending sign-off.
  (2) Track-A negative audit: **75 % of 4h implicit negatives are coverage-weak** ("never
  reviewed", not "rejected"; near-miss only 0.5 %) — low absolute AP partly a coverage artifact;
  contrastive capture (#42) priority RAISED.
  [Audit](reviews/btc-fib-track-a-implicit-negative-audit-20260721.md). (3) Facit data-loss bug
  fixed (overwrite-guard, all save paths); 1w 20-vs-21 = silent collision overwrite (see Open
  Questions). (4) Full candle cache re-fetched in cloud; signed cascade reproduces exactly
  (39 s). [log.md](log.md) top.

- **2026-07-21 OWNER SIGN-OFF: cascade results signed + degenerate fibs classified (docs-only).**
  Cascade `sequential_origin_signal` advisory→**signed** (no objections; modest framing binding).
  The 7 same-candle fibs = **misclicks** → fix worklist (home GUI) in Next Step; Open Question
  closed. No code, no facit touched. [log.md](log.md) top.

- **2026-07-20 MAINTENANCE: Pillow 12.3.0 (all 13 Dependabot alerts cleared, owner-confirmed) +
  hypothesis-flake `deadline=None` + branch housekeeping** (audit branch merged→main & deleted;
  `feature/research-fib` recreated fresh from main — work continues there). [log.md](log.md) top.

- **2026-07-20 CASCADE probe RUN → `sequential_origin_signal` (advisory) + validity fixes.**
  Pre-run leakage review: H1a/N1 clean; N2 look-ahead fixed + 4 more findings → prereg §9
  amendments (`2c04328`). CRLF-portable manifest fingerprint (`aeccffa` — verifier false-DRIFTed
  on Windows checkout, would have blocked the probe). Candle cache fetched (full facit coverage,
  4h 21 269 bars 2016→2026). Probe executed verbatim: **4h H1a 0.256 vs null 0.005, p<0.0005,
  93 hits of which 76 EXACT** — [results](reviews/btc-fib-cascade-conditioning-probe-results-20260720.md),
  pending owner sign-off. Transcription regression test now RUNS (cache present) and passes
  (≥0.90 floor). Gates green.

- **2026-07-20 SYSTEMATIC AUDIT (read-only; report off-repo) + P0 remediation.** Corpus manifest +
  verifier (`research/corpus_manifest.py`); transcription claim re-scoped + living regression test;
  stale counts fixed; degenerate-fib + 1w ±1 owner questions logged. **NEW
  [cascade-conditioning prereg](reviews/btc-fib-cascade-conditioning-probe-prereg-20260720.md)
  (run pending candle cache)** — does the previous fib predict the next origin? Motivated by facit
  chain geometry (4h: 85/371 exact `b_{i-1}==a_i` links) + untested U1. Detail: [log.md](log.md) top.

- **2026-07-02 MEASURED engine vs 4h-DOWN facit (out-of-sample, `scratchpad/measure_4h_down.py`).** Origin sits
  **43 %** (86/201, CI ~36–50 %), leg 30 %; **75/201 genuine wrong-swing** (bar-invariant). 1h-overfit → NOT broad.
  → contrastive capture (#42) justified (validity-reviewed, non-blocking). See Next Step.

- **2026-07-02 ACCEPTANCE tolerance LOCKED (`cef082d`) + CONTRASTIVE CAPTURE tool (#42, `0b1e9a1`).**
  `evaluation/acceptance.py`: 3-tier EXACT/SNARLIKT/NEAR/MISS, accept=NEAR, origin bars+price / "0" price-only looser
  (+7 tests). `labeling/tool.py --annotate-selection` + `selection_capture.py` (+9 tests): draw/label/tag/reason →
  schema, exact prices; first window HO-B; 1w cascade dated + CV probe dead (`bf071a7`).

- **2026-07-01 Fib Selection Learner v0 LANDED (#42, `afb5a5f`) → [review](reviews/btc-fib-selection-learner-v0-20260701.md).**
  Contrastive schema + magnitude baseline + fail-closed ML/Optuna gate (deps + ≥30 human windows + locked holdout);
  `research/selection_{annotation,baseline,ranker_ml}.py`. Same day: pivot-point selector DISPROVEN (strict null, p=0.997).

- **2026-07-01 Chamoun daily-fib STYLE distilled (docs-only) → [style doc](reference/chamoun-daily-fib-style.md).**
  `/chamoun-fib-style-distiller` over 76 daily facit (Observed/Inferred/Unverified). Reconcile flag: daily base = **76**
  not 67 (Verification Snapshot stale); `20210907` degenerate leg=0.

- **2026-06-30 STRUCTURE-ENGINE v1 — origin proposer landed** (`research/chamoun_structure_engine.py`, +9 tests,
  `24a3bb5`): frozen, DOWN-only, re-finds his 4 dated-1h origins (#1-prominence @ ~3-day scale). [log.md](log.md) top.

- **2026-06-30 GROW-FACIT (screenshot → facit).** Daily 2025–26 gap +5 fibs; 4h **+6** (365→**371**) via
  human-reviewed `--review-candidate` (`created_by=human`). [log.md](log.md) top.

- **2026-06-30 Checkpoint reminder hook wired** (`UserPromptSubmit`, auto-pings on capacity; hardened
  2026-07-01 with turn-count/thread-health ladder). [log.md](log.md) top.

- **2026-06-29 Leg-agreement RULER — built + SIGNED OFF (north-star step-1 measurement instrument).**
  The free facit-checker #38 lacked. [Prereg](reviews/btc-fib-leg-agreement-ruler-prereg-20260629.md)
  + [postlock](reviews/btc-fib-leg-agreement-ruler-prereg-20260629-postlock.md); new
  [`evaluation/leg_agreement.py`](../../src/fibengine/evaluation/leg_agreement.py) (`mean(s_high,s_low)`,
  `s=max(0,1−Δbar/W)`, W=2, direction-gated; +21 tests). leakage-review caught an overclaim → re-scoped to a
  **valid strict selection-scorer**, narrow coverage-capped range (ceiling ~0.79; sub-1.0 = coverage artifacts).
  Usable as **eval**, NOT a graded training objective. [log.md](log.md) top.
- **2026-06-29 #38 daily wick-pair anchor accuracy — clean NULL (SIGNED OFF; fractal control 0.90
  via B-closure, postlock A5).** [Locked prereg](reviews/btc-fib-daily-wick-pair-anchor-prereg-20260629.md)
  (selector-only); new [`strategies/chamoun_daily_wick_pair.py`](../../src/fibengine/strategies/chamoun_daily_wick_pair.py)
  + harness `research/chamoun_wick_pair_accuracy.py` (+4 tests). N=71: coverage 0.08 vs 0.90 →
  **`wick_pair_no_better`**; #31 stays the candidate. Gates green. [log.md](log.md) top.
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
- **2026-06-15→18 changes — archived** (all in [log.md](log.md) / [part 1](log-archive-btc-postreset-part1.md)
  + Status/Verification below): SELECTION-LEARNING prereg + 4h slices; B-1 horizontal-structure & behaviour/context
  studies **NULL/CLOSED**; Fib→Genesis V2 Phase 2/2.5 **PASS/CLOSED**; MTF confluence CP1–CP3 **CLOSED**; #32 tooling DONE.

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
- **2026-06-24 Fib SELECTION-LEARNING artifact-MECHANICS + snapping-FLIP — BUILT + RUN (descriptive,
  NO verdict; full detail in [log.md](log.md)).** Two sibling runs (`70174df`) on
  `research/selection_learning_artifact_mechanics.py` (+`--artifact-mechanics`, +10 tests): **(M1)** the
  4H "reached less clean" gap is a **span/duration confound** (Spearman −0.69; gap vanishes conditioning
  on span). **(M3)** snapping deflates because pivots sit outside human anchors → span extends; the **1D
  flip** is TF-dependent geometry, a **net-vs-path channel reversal** consistent with candle granularity
  (4H path-dominated → clean down; 1D net-dominated → clean up). **No verdict, no lock change; crux OPEN.**
  No matched-null/universe/Genesis/1H/ETH/refresh.
  [Mechanics](reviews/btc-fib-selection-learning-artifact-mechanics-20260624.md) ·
  [Flip](reviews/btc-fib-selection-learning-artifact-mechanics-flip-20260624.md).

**Next work requires a separate explicit GO. No W/gap, no Stage 1, no new sensitivity, and no Genesis
may be started automatically.** Parked (test-only, separate GO): lock the facit-discipline refusal
branches in `selection_learning.py:118-142` (currently uncovered — see audit).

## Verification Snapshot

Counts re-verified 2026-07-20 and locked in
[`data/labels/human_fib/MANIFEST.json`](../../data/labels/human_fib/MANIFEST.json)
(`corpus_manifest --verify`). **Total 484 base `fib_*.json`** (all log scale):

- **1M = 13** (9 @06-09 reset + 4 @06-26 nesting cohort v2) · **1w = 24** (20 @06-11 + 4 nesting;
  older docs say 21 — ±1 in Open Questions) · **1d = 76** (67 @06-11 + 4 nesting + 5 grow-facit
  06-30) · **4h = 371** (365 + 6 grow-facit 06-30; 20250506 dedup superseded-by-deletion).
- **Snapshot discipline (audit 2026-07-20):** selection results signed off before 2026-06-26 are
  bound to the pre-growth corpus (`FROZEN_FACIT_COUNT` 9/21/67/365); the W-gap preflight now FAILS
  on all TFs by design and other harnesses have none. Never compare a fresh re-run against those
  numbers; new preregs must pin a manifest snapshot.
- `experiments/review/weekly_source_fib_map/` and `…/weekly_source_fib_zoom/` —
  generated charts (gitignored; regenerate via the two new CLIs).
- `data/raw/bitfinex/BTC-USD/1M/limit_500.csv` — 115 bars (2016-12 .. 2026-06),
  fetched with `--config config/settings.expansion.yaml` to cover old anchors.
- `experiments/review/fib_level_events/` — active 1M pack `human_fib_review_20260609T135548Z`.
- Pre-reset archive (local disk; git tracks manifest only):
  [MANIFEST.md](../../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/MANIFEST.md)

## Open Questions

- Minimum monthly fib count before 1W mapping?
- ~~1w base batch: 20 vs 21?~~ **SOLVED + RESOLVED 2026-07-21:** silent filename-collision
  overwrite of `1w_20170316` by nesting-cohort v2. **Decision (owner-delegated, agent chose):
  KEEP the nesting version** — latest deliberate human drawing wins; all signed 2026-07-21
  results are computed on this snapshot; the base leg (985.55→2444.9) stays recoverable forever
  via `git show d1d98b3:…/fib_BTC-USD_1w_20170316T000000.json`. The tool now refuses silent
  overwrites ([log 2026-07-21](log.md)). No corpus change, no manifest relock needed.
- ~~7 degenerate same-candle fibs — intentional or misclicks?~~ **ANSWERED 2026-07-21: misclicks**
  — fix worklist in Next Step (home GUI); corpus counts will change when fixed. (Candle-verified
  2026-07-21: all 7 anchors == exact candle high/low — wick-to-wick single-candle drags.)

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

Full checklist (git pull / uv sync / candle-cache fetch / labeling preflight / SEP notes /
per-TF resume points) moved to
[reference/startup-checklist.md](reference/startup-checklist.md) (repo-bounds §2B, 2026-07-20).
Standing rules: do not auto-fib, do not infer anchors, keep the four flows distinct
(1M source / 1M→1W projection / true 1W source / true 1D source fibs).

## Links

- [BTC-first protocol](../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)
- [Research wiki index](index.md)
- [Human fib annotation](../labeling/HUMAN_FIB_ANNOTATION.md)
- [Archive manifest](../../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/MANIFEST.md)
