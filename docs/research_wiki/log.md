# Research Wiki Log

Append-only trail of wiki ingests, decisions, and review sessions.

Use headings like:

```text
## [YYYY-MM-DD] type | Short title
```

Types: `ingest`, `decision`, `review`, `question`, `maintenance`.


> Older entries (2026-06-11→06-12 source-fib milestones):
> [post-reset part 1](log-archive-btc-postreset-part1.md).
> Pre-reset (2026-06-10 and earlier): [part 3](log-archive-pre-btc-reset-part3.md) →
> [part 2](log-archive-pre-btc-reset-part2.md) → [part 1](log-archive-pre-btc-reset-part1.md)

## [2026-06-25] maintenance | Consolidated the A/B next-step into a handoff `## Next Step` block

Docs-only. The next step (the enrichment-lock GO-fork: **A** = build/run the `exclusivity` Commit 2,
**B** = grow the facit) was spread across several handoff bullets without one clear record. Added a
single `## Next Step` block (fork + discriminator + recommendation "A first, then B" + "requires
explicit GO"); trimmed the enrichment-lock and checkpoint bullets to absorb it under the 400-line
bound. **No new claim, no code, no direction chosen — GO stays with the user.**

## [2026-06-24] decision | Fib SELECTION-LEARNING — line PAUSED at model-enrichment lock

Checkpoint for the selection-learning side-quest. After the Stage-2 headline (modest single-feature
`cleanliness` lead, 4h), the line ran a chain of **controls** — prominence-family + k-sweep
(`k_stable_live_selection_signal`), W-gap (`no_causal_gap`), Stage-1 per-pivot
(`no_pivot_signal_above_prominence`), the `cleanliness` artifact-probe (inflationary detector-artifact
**unsupported** on 4h; direction guards → investigate), and a descriptive mechanics + snapping-flip pass
(span/duration confound + net-vs-path/candle-granularity). A **main-quest reset** then stopped the
mechanics drift and re-anchored the north star (*learn how the human selects meaningful fib legs/ranges;
facit = truth*) with a binding no-drift guardrail. The single open crux (`cleanliness` genuine vs
artifact) stays **OPEN**.

**Now PAUSED** at the **model-enrichment LOCK** (`bc85a69`, blind Commit-1): one lean shot — does a
single causal **leg-completeness / `exclusivity`** feature raise pooled OOS AP **over the current
Stage-2 model** (nested baseline) on 4h live k=3? Verdict `enrichment_helps` / `no_enrichment_signal →
park modeling + grow facit`; honest prior **low**. **Resume = GO Commit 2 (build/run) or route to
labeling (§E8).** No code started; matched-null/new-universe/Genesis/1H/ETH/refresh all out.
[Enrichment LOCK](reviews/btc-fib-selection-learning-enrichment-lock-20260624.md).

## [2026-06-22] decision | Fib SELECTION-LEARNING retrospective W / causal-availability-gap LOCK (docs-only, gated)

Commit-1 lock for side-quest #1, **blind** (no retrospective model built, no gap value ever
computed). Reuses §A5 pins (4h `W=180`, cells `{0,3,6,12}`, primary `k=3`, pooled AP, ε, §6 family;
`recency` viewport-relative). **New locks:** gap(k) = `AP(retro W) − AP(live k)` on the **identical
live-at-`k` rows** (same-row parity → isolates *feature availability*, not universe size); **common
embargo = `W`** for both models (leakage-safe parity); decision-point cluster bootstrap 2000×, seed
20260618; verdict `no_causal_gap` / `gap_closes_with_buffer` / `gap_persists` / `inconclusive` /
`artifact_check_needed` (4h primary; gap cells `{3,6,12}`, k=0 degenerate-excluded). **Secondary /
sensitivity**, descriptive with CIs — **not** in the Holm headline family, **no** new positive claim.
Non-claims binding: not a reproduction; no edge/behaviour/PnL/Genesis/auto-fib/1H/ETH; cleanliness-
artifact stays open. Execution (Commit 2) needs a **separate explicit GO**.
[Lock doc](reviews/btc-fib-selection-learning-w-gap-lock-20260622.md).

## [2026-06-17] decision | New line pre-registered — Fib SELECTION-LEARNING (docs-only, gated)

A genuinely different question from the closed behaviour/B-1 lines: not "do fib levels repel price"
(closed NULL) but **"can a model reproduce how the human selects swings/ranges"** — selection
learning, labels as facit, **no edge/backtest/Genesis claim**. Target = **Stage 2 leg/range gestalt**
(5 components: scale, pairing, direction, exclusivity, context/HTF; structure first, levels second);
Stage 1 per-pivot = diagnostic floor (Stage 2 ≤ Stage 1 recall). Two viewports — live-equivalent
(`anchor_b+k`) vs **bounded** retrospective (`anchor_b+W`, finite, not omniscient) — and the
**causal-availability gap** attributed per feature-group, `k`-sweep mandatory. Binding
**feature-provenance rule** (every feature tagged left-available/right-edge-sensitive, fail-closed,
structurally enforced). One pre-registered **primary cell** (forking-paths defence) + candidate
**coverage ceiling** (B-1 power-honesty parallel). Docs-only, two-step gate: feature/param addendum
(blind) then separate go. Designed collaboratively with Chamoun (the labeler is facit on his own
process). [Prereg](reviews/btc-fib-selection-learning-prereg-20260617.md). **Next: addendum tomorrow.**

## [2026-06-18] review | Fib SELECTION-LEARNING k-sweep {0,3,6,12} (4h) → k_stable_live_selection_signal

Mandatory confirmation-buffer sweep (addendum §A5), live-only, so the headline `k=3` is not a
forking-paths artifact. **Verdict rule locked before the run:** a `k` cell survives only if powered
**and** its model AP-lift CI excludes 0 vs **every** causally-allowed §6 baseline (the locked
prominence-FAMILY criterion — magnitude + prominence A/B); cross-k verdict
`k_stable_live_selection_signal` iff ≥2 cells survive. Result: **k=0 degenerate** (0 candidates,
`reachable_fraction=0.0`, unpowered — *not interpretable*, excluded); **k=3/6/12 all powered and
survive** (`p_one_sided lift≤0 = 0/2000` throughout; lowest CI floor k=12 vs prom-sum 0.025). 3/3
powered cells survive → **`k_stable_live_selection_signal`**: the lead is not a narrow-buffer
artifact. Modest framing intact — `cleanliness` dominates (~0.20) at every powered k; k=12
`scale_confluence` (~0.13) is a **secondary hint** once causally available, not a second pillar; AP
0.057→0.066 (far under 0.83 ceiling); **single-feature, not a reproduction, no edge/behaviour/Genesis
claim**; 1M/1w/1d underpowered, not refuted. Code+tests committed `ea6c2ea` (ruff/format/bounds/544
pytest green, cov 75.52%); artifacts gitignored/regenerable. Next candidate tracks (NONE started,
separate GO each): retrospective `W`/causal-availability gap; Stage-1 per-pivot diagnostic.
[Results](reviews/btc-fib-selection-learning-results-20260618.md).

## [2026-06-18] review | Fib SELECTION-LEARNING prominence-baseline sensitivity (4h) → survives_prominence_family

Scoped sensitivity (4h only): does the cleanliness-driven AP-lift survive the stronger §6
prominence baseline? **Both instantiations + the verdict rule locked before the run** (not chosen
after): A = summed endpoint prominence (= `prominence` feature col, rank-equiv to raw sum), B = max
endpoint prominence. Same candidate universe / viewport / `k=3` / ε / purged split / held-fixed
model — only the baseline ranking differs. Decision-point cluster bootstrap (2000×). Result: model
AP-lift robust vs **all three** §6 baselines — magnitude +0.052 [0.023,0.120], prominence-A +0.043
[0.018,0.104], prominence-B +0.049 [0.021,0.116]; every CI excludes 0, 0/2000 ≤ 0. Sanity: both
prominence baselines (0.0138 / 0.0079) beat magnitude (0.0051) as expected; model beats both.
**Pre-committed verdict = `survives_prominence_family`.** Weights unchanged → **`cleanliness` still
carries the lift** (0.20), structure_alignment ≈ 0. So the lead is **not** a magnitude- or
prominence-artifact — but still single-feature, low absolute AP (0.057 vs 0.83 coverage ceiling),
**not a reproduction of human selection, no edge/behaviour claim**; 1M/1w/1d underpowered. Open
interpretive question: is `cleanliness` a detection/anchoring artifact? +1 test (19 total).
[Results](reviews/btc-fib-selection-learning-results-20260618.md).

## [2026-06-18] review | Fib SELECTION-LEARNING AP-lift inference (4h) → MODEST single-feature lead

Inference slice (scoped: 4h AP-lift only). Decision-point cluster bootstrap (2000 resamples by
`anchor_b` group, model held fixed): lift +0.052, **95% CI [0.023, 0.120] excludes 0**, 0/2000
resamples ≤ 0 — the 4h AP-lift is **robustly positive vs the magnitude baseline, OOS** (a
bootstrap-stability statement, not a permutation-null p). **But** the §10 interpretable weights show
it is **carried almost entirely by `cleanliness`** (std weight 0.20 vs prominence 0.07,
structure_alignment ≈ 0): human-marked legs are *cleaner/more efficient* than magnitude predicts —
a single coherent correlate, **not** a multi-feature reproduction of human selection. Scope limits:
beats **magnitude only** (§6 most-prominent baseline untested; prominence carries weight so the lift
may shrink against it); AP 0.057 capped by 0.83 coverage ceiling (human not reproduced); 1M/1w/1d
**underpowered, not refuted**. **No edge/behaviour claim.** Recommended next (separate go):
prominence-baseline sensitivity on 4h. [Results](reviews/btc-fib-selection-learning-results-20260618.md).

## [2026-06-18] review | Fib SELECTION-LEARNING Stage-2 headline built + run → POINT ESTIMATE (no claim)

§12.3 go granted. Built `research/selection_learning.py` (+15 tests) and ran the single
pre-registered headline cell (Stage 2, live-equivalent `k=3`, pooled-AP per A5.1). Causal by
construction: features computed on a frame **truncated at `anchor_b+k`** with the `k*≤3` whitelist
(`{magnitude,cleanliness,duration,prominence,structure_alignment}`), candidate universe re-detected
on the truncated frame, ε-match to human legs (A4), purged split (embargo = reach `k`), numpy
logistic regression (zero new deps, §10) vs §6 magnitude baseline. **Only 4h powered** (65 test
pos): AP model 0.057 vs base 0.005 (≈11×, ≈22× base rate), secondary AUC 0.914; AUC≈0.88–0.91 on
1M/1d too (1w 0 test pos). **STATUS: point estimate, inference PENDING** — `lift_pos_powered` is a
flag, not a significance test; no CI/p-value on the AP-lift yet → **no finding claimed**. Next:
inference on the AP-lift resampled by decision point, then k-sweep/W/gap/Stage-1. Artifacts
gitignored. [Results](reviews/btc-fib-selection-learning-results-20260618.md).

## [2026-06-18] decision | Fib SELECTION-LEARNING §12 addendum frozen (docs-only, blind)

Step-2 of the two-step gate, blind to output. Reuses the engine's **8 existing interpretable
features** (`core/features.py`) — no new ones — and tags each with a **minimum confirmation buffer
`k*`** (magnitude/cleanliness/duration/round_number=0; prominence/structure_alignment=3;
scale_confluence=12; recency=∞). This refines §5's binary left/right tag: a bare binary + mechanical
exclusion would freeze the live model at every `k`, making the mandatory `k`-sweep (§8) **vacuous**
(advisor catch) — `k*` makes the sweep admit features as the buffer grows, so the causal-availability
gap is empirical not a tagging artifact. `recency` dropped from the live model (dataset-end ref);
exclusivity #4 operationalized set-level over `structure_window=6` base-pivot chunks (`k*=3`, no
parent-degree boundaries); ε **reused** from `EvaluationConfig` (`time_tol=3`, `price_tol=0.5` ATR —
blindness defense). `k`-sweep {0,3,6,12}, `W` per TF (1M=24/1w=52/1d=120/4h=180 bars), **single
primary cell = Stage 2 + live-equivalent + `k=3`** (base detector confirmation), all else secondary.
Pinned to `settings.expansion.yaml`. **Still gated:** §12.3 separate explicit go before any build/run.
[Addendum](reviews/btc-fib-selection-learning-addendum-20260618.md).

## [2026-06-17] review | B-1 horizontal-structure study — RUN, result NULL (§12 go granted)

Built then ran (prereg §12 path (a)). Commits `474f320` (SENARE-1 e-value) → `edcc87c` (slice) →
`92a0cdf` (ROUND); all prereg pins (§4 RW-null, §8 e-value, §3/§4 ROUND) locked **before** the run.
**Result: `any_robust = False`** across all 12 subject×TF cells — no generic horizontal level
(SWING / 1-2-5 ROUND / PRIOR-EXTREME) repels BTC more than its matched random-walk null under the
anytime-valid e-Holm test. Powered cells (N≥30 both sides): swing-4h/1d, prior_extreme-4h, round-4h.
Only SWING shows a directional edge (4h 0.841 vs 0.780) but it is **not even individually marginal**
(e=1.70, p≈0.59); e-Holm needed E≈240 at 12-way multiplicity, so **low power for subtle effects**.
Reject ~0.76–0.84 across **all** sources incl. RW-null = generic mean-reversion / spontaneous RW
structure, not a mechanism. **Extends the closed fib-null** (fib not special vs swing → generic
structure not special vs a random walk). §10 strategy sanity-check **not run**. No trading claim,
no fib JSON read, no label/corpus mutation; artifact gitignored.
[Results](reviews/btc-horizontal-structure-event-study-results-20260617.md) ·
[prereg](reviews/btc-horizontal-structure-event-study-prereg-20260617.md).

## [2026-06-17] maintenance | S-3: viz/plot.py routed through shared candle helper

`viz/plot.py:plot_prediction` drew its own black close-line; it now routes through the shared
`research/human_review_candles.draw_review_candles` (same palette/path as the review charts). New
keyword args `candlestick=False` (default — close-line, needs only `close`) / `dark_theme`;
`candlestick=True` renders mplfinance candles (needs full OHLCV), so the function finally matches
its "plotta candles" docstring. **No layering inversion:** `plot.py` already imports
`labeling.store`, so it is application-tier like `labeling/tool.py` (which imports the same helper).
Parametrised test added (both paths render a non-empty PNG); ruff + 486 pytest (`viz/plot.py` 100 %)
+ bounds green. SENARE-3 done. Working-tree only (not committed).

## [2026-06-17] decision | B-1 horizontal-structure study pre-registered (docs-only, gated)

Post-fib-null follow-up registered, **not run**:
[btc-horizontal-structure-event-study-prereg-20260617.md](reviews/btc-horizontal-structure-event-study-prereg-20260617.md).
Question: do *generic* horizontal levels (swing / 1-2-5 round ladder / prior-period extremes) repel
BTC more than a matched **random-walk null** (`synthetic_baseline` — the unseen quantity that makes
the question legitimate post-fib-null)? Shuffle-placebo demoted to descriptive (already seen).
Satisfies NU-1..NU-3; as the **3rd look at the same OOS window**, execution **requires** anytime-
valid inference (e-values / e-Holm = SENARE-1, unbuilt), so a fixed-horizon permutation is
forbidden here. Unblock: (a) build SENARE-1 + wire DELAR-1, or (b) fresh data. All subject
parameters frozen in the prereg before any result.

## [2026-06-17] maintenance | feature/research-fib promoted to main; PR review fixes + dep bump

Branch promoted to `main` via **PR #33** (89-commit fast-forward; **merge-commit** to keep the
wiki's commit-hash citations valid — squash/rebase would have orphaned them). Two PR-review
fixes (Codex) landed on the branch first:
- **P1** (`labeling/tool.py`): a windowed editing session now keeps out-of-window legs in memory
  and merges them on save — pressing `s` no longer silently deletes saved legs (facit-safety).
- **P2** (`research/level_events.py` + `human_review_rows.py`): level-event detection now threads
  `fib.scale_mode` (= **log** per protocol) instead of defaulting to linear, so level-event
  prices/rows match the log charts. **Behaviour change:** older level-event outputs were linear;
  new ones are log.

**PR #34** (security): bumped `cryptography` 48.0.0 → 49.0.0 (Dependabot `GHSA-537c-gmf6-5ccf`,
High — vulnerable OpenSSL in wheels; transitive via ccxt, no upper bound). Lockfile-only;
ccxt imports clean, gates green. Dependabot alert auto-closed.

## [2026-06-17] decision | Standing prereg addendum for future horizontal-structure studies

NU block of the external pattern scan, docs-only:
[horizontal-structure-prereg-addendum-20260617.md](reviews/horizontal-structure-prereg-addendum-20260617.md)
(NU-1 random-walk control; NU-2 anytime-valid/e-Holm re-looks; NU-3 name embargo as purged-CV).
DELAR-1/2/3 since implemented (commits `ca5ae73`/`0b380e6`/`7b03837`): synthetic random-walk
baseline (`research/synthetic_baseline.py`), uncertainty-ordered labeling worklist
(`labeling/worklist.py --by-uncertainty`), fail-closed swing-label JSON validation
(`validation/schemas.py`). SENARE still gated (`clever-yawning-catmull.md`).

## [2026-06-16] decision | BTC/Fib behaviour/backtest line — PAUSED / CLOSED (reviewed PASS)

Commit `f4e96f1` reviewed **PASS / CLOSED**. Final conclusion across both pre-registered studies:
unconditioned Behaviour Event Study = **no signal**; Context-Conditioned Study = **no candidate**.
**Fib does not beat the placebo/swing baselines** on the current BTC corpus; the **swing baseline
matches or beats fib**, so the weak level reaction is **generic horizontal structure, not
Fibonacci-specific**. Strategy sanity-check **not authorised / not run**. The BTC/Fib
behaviour/backtest line is **paused/closed**. **Discipline:** do **not** re-run these studies on the
same BTC data with tweaked parameters; any future behaviour test must be a **new prereg on fresh
data** or a **materially different question**; **no active next implementation is authorised**.
Future possible tracks (listed only, none started): fresh-data validation on other symbols/TFs
(new prereg); source-label quality / correction-candidate cleanup; non-fib horizontal-structure
research; separate visual/research tooling; Genesis/Fib remains paused unless explicitly reopened.

## [2026-06-16] review | BTC/Fib Context-Conditioned Study — NO CANDIDATE (reviewed PASS / CLOSED)

Second Lean Fib question, opened after the unconditioned null: do fib levels react differently
than placebo/swing **only in specific causal contexts**? Advisor flagged the prior `reject_rate`
as saturated → switched primary to a **continuous** metric `reaction_asym_atr = MFE−MAE`,
rank-permutation test, **Holm** across K=2 frozen confirmatory contexts (**trend regime**, **deep
0.618/0.786**), MDE pre-registered, confirmatory TF=4h. Disclosed second-look (same OOS window
reused; power pre-flight peeked) → train-sign is the guard, ceiling = candidate not confirmation.
**Result: no confirmatory context passes.** Fib beats *random placebo* in the predicted direction
(trend gap +0.64, deep +0.46 ATR; train-sign consistent) but only **nominally** (p=0.042/0.056,
**fails Holm**) and **never beats the swing baseline** (swing reacts ≥ fib in both). Gaps ≪ MDE
(~1.3–1.9). 1d underpowered (N<30, train sign flips). Insight: faint level-reaction = generic
horizontal structure, not Fibonacci. Gate fails → **no strategy work.** New
`research/fib_context_conditioned_study.py` (17 tests), reuses the event-study engine; artifact
gitignored. No Genesis/1H/ML/export/label change.
[Prereg](reviews/btc-fib-context-conditioned-study-prereg-20260616.md) /
[results](reviews/btc-fib-context-conditioned-study-results-20260616.md).

## [2026-06-16] review | BTC/Fib Behaviour Event Study — NO SIGNAL (reviewed PASS / CLOSED)

First Lean Fib Research question, run end-to-end. Causal event study on the locked corpus
(1M/1w/1d/4h, no 1H): fresh touches of causally-known fib **interior retracements** vs two
baselines — **matched deterministic placebo** (same count/time, random causal-range price) and
**causal fractal swing** highs/lows. OOS 70/30 + embargo; permutation test on test-window
reject_rate. **Result: fib levels are not measurably different from placebo/swing.** At the only
powered TF (4h, N≥138/source) fib reject 0.78 ≈ placebo 0.80 ≈ swing 0.84 (p=0.63/0.19); 1d
nominal-only (not sig, N<30); 1w/1M too sparse (N≤2). High ~0.8 reject across *all* sources =
generic mean-reversion, not a fib property. Gate fails on every TF →
**strategy sanity-check NOT run** (Phase 0 §8 placebo stop). Code
`fib_behaviour_event_study.py` (19 tests); artifact gitignored. No Genesis/1H/ML/export/label
change. [Prereg](reviews/btc-fib-behaviour-event-study-prereg-20260616.md) /
[results](reviews/btc-fib-behaviour-event-study-results-20260616.md).

## [2026-06-16] decision | BTC/Fib — post-Phase-2.5 fork decision (docs-only)

Clean decision point after Phase 2.5 closed. Compares 4 next-step options (A pause / B new
falsifiable question / C conceptual Genesis prep / D BTC-Fib quality, not 1H) with
observed/inferred/unverified kept separate. **Rec: A (pause) primary; D the only no-new-risk
continuation.** B's real value needs code/export (breaches scope, trends to Phase 3) and its
docs form duplicates Phase 0; C is redundant with Phase 1 + risks Genesis drift. Builds
nothing; no Phase 3, no export, no Genesis touch, no 1H, no ML/backtest/signal. Choice is the
human's. [Note](reviews/btc-fib-post-phase25-fork-decision-20260616.md).

## [2026-06-16] review | Fib → Genesis V2 — Phase 2.5 reviewed PASS / closed

Human review of commit `4599819` — **verdict PASS**, Phase 2.5 closed. Confirmed docs-only:
3-state separation (no zone known / nearby / ATR-warmup not-applicable), per-column nullability,
distance-null as empty CSV field (not 0/inf), empty-meta ⇔ no-known-zone invariant, Genesis
read-only consumer rules (dense table, no imputation across `known_after_ts`, meta never a
feature). **Non-blocking pre-export note:** decide whether `has_robust_4tf_zone_nearby` is
log-price- or ATR-thresholded (ATR ⇒ warmup-null or a separate availability flag). No Phase 3,
no real export, no Genesis touch, no ML/backtest/signal.

## [2026-06-16] decision | Fib → Genesis V2 — Phase 2.5 feature nullability policy (docs-only)

Docs-only policy pinning how the future bar feature table represents empty values — the
precondition flagged by the Phase 2 review. Defines **three** states (no zone known / no zone
nearby / not-applicable ATR-warmup), per-column nullability (join keys + bools + ATR-free count
+ meta always non-null; the 7 non-ATR `nearest_*` null only when no zone known; ATR-denominated
columns null during warmup), distances as **null not 0/inf**, the empty-meta ⇔ no-known-zone
invariant, and read-only Genesis consumer rules (dense table, no imputation across
`known_after_ts`). No code, no export, no Genesis touch, no ML/backtest/signal. Not Phase 3.
[Policy](reviews/btc-fib-to-genesis-v2-feature-nullability-policy-20260616.md).

## [2026-06-16] review | Fib → Genesis V2 — Phase 2 reviewed PASS / closed

Human review of commit `68dc006` — **verdict PASS**, Phase 2 closed. Confirmed: contract-test
only inside Fib, no Genesis coupling, no real export, no feature recomputation, schema/join/
causality validated mechanically, fail-closed cases covered, `confirmation_buffer_hours` pins
the unit. **Follow-up (not now):** before any real export, define a **nullability policy** for
feature columns. No Phase 3, no real export, no Genesis touch, no ML/backtest/signal.

## [2026-06-16] feat | Fib → Genesis V2 — Phase 2 dummy contract test (narrow slice)

Mechanical contract/dummy test **inside the Fib repo only** — not export, not Genesis
integration. New stdlib-only `research/feature_contract.py` validates two synthetic dummy CSVs
(committed under `reviews/contracts/phase2_dummy/`: 3 zones, 4 bars incl. a multi-zone row)
against the Phase 1 schema: exact-header schema, join keys `(symbol,timeframe,timestamp)`
non-null + unique, causality `known_after_ts <= timestamp` over the whole reference set,
knowability floor `known_after_ts >= max(anchor_b)+buffer`, 1H fail-closed, feature/metadata
boundary asserted at import. No fib computation, no Genesis import, no pipeline/ML/backtest/
signal/edge. 20 tests; ruff + 426 passed (76%) + repo-bounds green; CLI smoke OK. **Stop after
this.** [Report](reviews/btc-fib-to-genesis-v2-phase2-dummy-contract-20260616.md).

## [2026-06-15] review | Fib → Genesis V2 — Phase 1 closed (PASS)

Phase 1 feature-export spec reviewed — **verdict: PASS**; **closed as a docs-only contract**.
Remaining risk (causal features **non-empty** after all rules) is **empirical, belongs to Phase
2**. **Phase 2 still requires explicit GO.**

## [2026-06-15] question | Fib → Genesis V2 — Phase 1 feature-export spec

Docs-only **data-contract** spec (builds nothing) for a future causally-safe feature export Fib →
Genesis V2, gated by the Phase 0 question. Defines a **zone registry** + **bar feature table** with
binding rules `known_after_ts = max(anchor_b)+buffer` and per-row `zone.known_after_ts ≤ timestamp`,
**3 baseline specs**, a **read-only CSV-first Genesis contract**, **9 causal invariants**, and a
**do-not-export list**.
[Spec](reviews/btc-fib-to-genesis-v2-phase1-feature-export-spec-20260615.md).

## [2026-06-15] question | Fib → Genesis V2 — Phase 0 pre-registration

Docs-only pre-registration of the one falsifiable behaviour question (does price react measurably
differently at causal robust fixed-band MTF confluence zones than at matched naïve/placebo levels,
OOS?) + why-not-anchor-first (selection leakage), causal feature rule, leakage manifest, ≥3
baselines (causal swing + shuffled/placebo = primary), time-split/embargo holdout, neutral success
metrics, stop/go. Authorises nothing beyond the note.
[Note](reviews/btc-fib-to-genesis-v2-phase0-prereg-20260615.md).

## [2026-06-15] decision | MTF confluence CP1–CP3 — interpretation & decision note

Docs-only synthesis closing the MTF-confluence track. **Observed:** 222 single-linkage
clusters @ε=0.005 (188 fixed-band); c001 robust tight 4-TF; c002 chaining-dependent (dissolves
under fixed-band); c004/c006/c007 zero-span; all 5 CP3 cards human-approved. **Inferred:** MTF
confluence exists as *geometry* — c001 shows tight method-stable confluence can exist, c002
shows single-linkage can overstate strength, zero-span shows exact-price coincidence; none of
it proves edge/support-resistance/predictive value. **Unverified:** price-behaviour effect,
vs-naïve-baseline usefulness, ETH generalisation, whether more cards inform or just confirm,
behaviour-study scope risk. **Decision options** (5) compared with value/risk/scope/smallest
slice. **Recommendation: STOP the MTF track here** — don't expand cards, don't start a
behaviour study without a pre-registered falsifiable question + naïve-level baseline; ETH gated
on BTC sign-off. Next active decision is a fork: **pause Fib, or open a new track with one
clear question.** [Note](reviews/btc-mtf-confluence-interpretation-decision-20260615.md).

## [2026-06-15] decision | MTF confluence atlas CP3 — first pack closed (all cards approved)

First CP3 visual-atlas pack **complete and human-approved (2026-06-15)**. Five cards across
three structural archetypes: **c001** robust fixed-band 4-TF (span 0.00123 ≤ ε); **c002**
chaining-dependent single-linkage contrast (span 0.00627 > ε, dissolves under fixed-band,
never presented as tight 4-TF); **c004/c006/c007** zero-span exact-price 3-TF (span = 0 at
~$64829/$13764/$9085). All resolved by structural signature (cluster ids are positional and
unstable), out_dir keyed on stable label, charts assert geometry only — no edge/signal/
support-resistance. PNGs gitignored, none committed. **Next decision (not started):** stop
here as the first pack, or later expand with fixed-band clusters only on an explicit go.
Docs-only close; gates green (406 passed). [Capstone](reviews/btc-mtf-confluence-atlas-cp3-20260615.md).

## [2026-06-15] feat | MTF confluence atlas CP3 slice 3 — zero-span 3-TF cards (generated)

c002 contrast card **human-approved**. Slice 3 adds three **zero-span** (exact-price) 3-TF
cards under **fixed-band**: `c004`/`c006`/`c007` at ~$64829/$13764/$9085, where
`price_span_log == 0` — several human-drawn fib levels from three timeframes on the
*identical* price (immune to epsilon and chaining; the structural opposite of c002). **Label
discipline:** c004/c006/c007 are CP2's stable labels; cluster ids are positional and have
since shifted (they resolve to c002/c003/c004 under the current corpus), so resolution is by
structural signature (`tf_count==3`, exact TF set, `repr ± 50`, `price_span_log == 0`,
window-year range) — each matches exactly one fixed-band cluster. Output dir is now keyed on
the **stable signature label** (not the positional id); titles show `label (cluster_id)`.
The degenerate `[min,max]` band (min==max) renders as the single exact-price line; metadata
says *zero-span (exact-price coincidence) / N levels share one price across M TFs*. Fail-closed
`len(band)==level_count` cross-check passed (5/4/4). c001 re-renders identically (label==id).
406 tests green (+2 zero-span resolution tests in a new file to respect the 300-line bound; no
golden snapshots for the three cards — synthetic zero-span corpus would exceed it). PNGs
gitignored, none committed. **Pending human inspection.**
[Report](reviews/btc-mtf-confluence-atlas-cp3-zero-span-20260615.md).

## [2026-06-15] feat | MTF confluence atlas CP3 slice 2 — c002 contrast card (generated)

c001 card **human-approved** (title dedup + member-table polish). Slice 2 adds the
chaining-dependent **contrast** card: `mtf_confluence_atlas` is now method-aware
(`--cluster c001|c002` pairs a structural signature with its clustering method). c002
(~21167, 2022-12 → 2023-07) resolves only under **single-linkage** — `price_span_log`
0.006272 **> ε=0.005**, so it chains across log-price and **dissolves entirely under
fixed-band**. New signature fields `min_span_log` (= ε guarantees chaining; fail-closed if
tight) + `window_year_end` (multi-year window). Headline/metadata never say "tight 4-TF":
they state *chaining-dependent (span > epsilon) / NOT tight fixed-band 4-TF*. Fixed a shared
`band_member_rows` rounding bug (1M level on the rounded band edge dropped 4→3): added a
1-cent tolerance + a fail-closed `len(band)==level_count` check; **c001 re-renders
identically** (verified 4/4). 404 tests green (+1 resolution test); c001 golden unchanged.
PNGs gitignored, none committed. **Pending human inspection.**
[Report](reviews/btc-mtf-confluence-atlas-cp3-c002-20260615.md).

## [2026-06-15] feat | MTF confluence atlas CP3 slice 1 — c001 card (generated)

First visual-atlas slice. New `research/mtf_confluence_atlas.py` (stdlib + existing matplotlib
stack) renders one confluence card for the robust 4-TF cluster **c001** under **fixed-band** at
the primary `epsilon_log=0.005`, on a **1d** candle backdrop. Target resolved by **structural
signature** (tf_count==4, exactly {1M,1w,1d,4h}, repr≈29274±200, span≤0.005, window year 2021),
never a hard-coded id — exactly one fixed-band cluster matches. Fail-closed: zero/ambiguous
signature match, superseded `20250506T080000` in any member, off-protocol timeframe (no 1H),
and missing candle cache (no auto-fetch). Members reconstructed in-process from `LevelRow`
(not the truncated CSV); 4 members (1M/1w/1d/4h) at 29247–29283, `price_span_log=0.00123`
annotated in a metadata box (CP2-corrected headline). Card = candles + shaded [min,max] band +
representative line + per-TF member lines (levels view). `render_summary` gained
`cluster_atlas_summary` (includes the analytical numbers — `price_span_log` is the central CP2
metric) + golden snapshot. PNGs under `experiments/review/mtf_confluence_atlas/fixed_band/c001/`
(gitignored, none staged). 10 tests; no new deps; no source labels changed. **Generated,
pending human visual inspection** — observed: the four members within $36 render as a near-single
band (label stacking noted as a candidate adjustment). Next: approve card design or adjust, then
c002 chaining-dependent contrast card. No chart-as-signal, no edge.
[Report](reviews/btc-mtf-confluence-atlas-cp3-c001-20260615.md).

## [2026-06-15] review | MTF confluence CP2 — sensitivity / robustness

Robustness pass over CP1. Added stdlib `cluster_confluence_fixed_band` (complete-linkage in
price + single-linkage in time) + `run_sensitivity` (9 new tests). Predeclared epsilons
0.0025/0.005/0.01. Single-linkage total 173/222/266; chaining (span>ε) 12/30/70 = 7%/14%/26%.
Fixed-band 144/188/242 (0 over-ε by construction). **c001 (~29274) robust 4-TF** across
methods/epsilons (3-TF under fixed-band only at 0.01, a band-cut effect). **c002 (~21167)
chaining-dependent** — 4-TF only under single-linkage at ε≥0.005 with span 0.00627>ε; dissolves
to 2-TF fragments under fixed-band. Verdict: confluence is real but CP1 overstated c002.
Conditional GO to CP3 visual atlas (render fixed-band + annotate span). No chart, no tuning,
no source change. Full suite 394 passed, 75%. Report:
[`reviews/btc-mtf-confluence-sensitivity-20260615.md`](reviews/btc-mtf-confluence-sensitivity-20260615.md).

## [2026-06-15] review | MTF confluence atlas CP1 — confluence table

First analytical slice on the locked corpus. New stdlib module `research/mtf_confluence.py`
(10 tests): flattens 462 fibs → 2772 level rows, clusters by log-price proximity
(epsilon_log=0.005, chosen before results) + overlapping anchor windows, requires ≥2 TFs.
Result: **222 clusters** (2×4-TF, 24×3-TF; 1d,4h dominates 143). Chaining visible
(30/222 span>eps, reported). **Stop/go: GO** to CP2 (sensitivity/robustness, multi-eps +
complete-linkage). No chart, no trading conclusions, no tuning. Committed CSV under docs;
large levels CSV gitignored.
[Report](reviews/btc-mtf-confluence-table-20260615.md).

## [2026-06-15] review | BTC source-fib corpus integrity report (capstone)

Read-only capstone locking the corpus before the MTF analytical pass. Re-derived on disk:
1M=9, 1w=21, 1d=67, 4h=365 (462 total; up=219/down=243), coverage (anchor-derived)
2016-12-29 → 2026-06-07, log scale + `tradingview_log_chamoun`, no 0.236. Source-quality:
Tier 1+2 done, 20171228 corrected, 20250506 superseded (1), ledger validates (10 rows).
Corpus declared clean. Next: #1 MTF confluence atlas (table-first). Docs-only.
[Report](reviews/btc-source-fib-corpus-integrity-20260615.md).

## [2026-06-15] decision | Next research-pass design — corpus integrity then MTF atlas

Read-only design comparing 5 candidate passes (5×8 sub-questions). Recommends corpus
integrity report (#2) now, MTF confluence atlas (#1) next; #5 visual companion to #1;
#3/#4 deferred. Docs-only.
[Report](reviews/btc-source-fib-next-research-plan-20260615.md).

## [2026-06-15] maintenance | Reconcile data/labels/INDEX.md with current facit

`data/labels/INDEX.md` was stale (2026-06-10: 1w/1d/4h listed absent/0). Reconciled to
on-disk base counts (excl. sidecars): 1M=9, 1w=21, 1d=67, 4h=365; authority pointed to
handoff.md. Docs-only. (Note: log.md near its size bound — archive old entries next.)

## [2026-06-15] fix | 20250506 dedup — fib A superseded, fib B retained

Resolved the strongest overlap-detector near-duplicate. `fib_BTC-USD_4h_20250506T080000`
and `…120000` are the same up-leg to the same high (shared anchor_b 97840; box_iou 0.70).
Candle data: 05-06 12:00 low (93663) is the true bottom = B's anchor_a; A's anchor_a
(08:00 @ 93988) is one bar early on a higher low — a redundant, worse version (not a
complementary sub-leg). Decision: **supersede A, retain B.** No retired-label pattern
exists, so A's `fib_*.json` was deleted from active facit and documented. Active 4H count
**366 → 365** (current-state docs updated; dated historical 366 entries kept). Ledger gained
a tested `superseded` status; both fibs now tracked (B ok/accepted, A suspicious/superseded
with provenance hash). fib B unchanged (verified no diff); only A deleted; no other source
JSON touched. Report:
[`reviews/btc-4h-fib-20250506-dedup-20260615.md`](reviews/btc-4h-fib-20250506-dedup-20260615.md).

## [2026-06-15] feat | Structural chart-contract + metadata snapshots (Issue #F)

Implemented the chart-regression spike's recommendation. Added `research/render_summary.py`
(stdlib-only, no deps): `map_summary` / `zoom_summary` / `gallery_summary` produce stable,
text-diffable dicts from existing render results/output dirs — repo-relative forward-slash
paths, no timestamps, no absolute paths, sorted order, no level prices (those stay in the
source JSON). Committed golden JSON snapshots under `tests/research/snapshots/` (text only,
no binary baselines); tests regenerate with `UPDATE_SNAPSHOTS=1`. Covers all three primary
flows (4H map, 4H zoom, artifact gallery) + a guard test that snapshots are JSON-only.
5 tests; ruff + full suite green (375 passed, 75.16% cov). No PNG baselines, no pixel diff,
no new deps. Automatic structural layer; HTML gallery + ledger remain the manual visual
layer. Closes the chart-regression follow-up (#F).

## [2026-06-15] decision | Chart regression strategy — structural-first (spike)

Design spike for Issue #32 evaluate-later. Recommendation: **structural chart-contract
tests + text/metadata snapshots first; defer pixel regression.** Grounded in the repo's
existing style (~170 structural assertions across 22 render test files) and the anti-blob
policy. Adopt now: extend structural assertions on render dataclasses + committed golden
JSON/markdown summaries (no blobs). Keep HTML gallery + ledger as the manual visual layer.
Defer `pytest-mpl`/`matplotlib.testing.compare` (need committed PNG baselines, flaky across
versions); reject image/perceptual hashing (new dep, version-sensitive). No binary
baselines committed. Follow-up issue #F drafted (render_summary + golden snapshots, stdlib).
Report: [`reviews/chart-regression-strategy-20260615.md`](reviews/chart-regression-strategy-20260615.md).
Docs-only; no code/deps/artifacts.

> **2026-06-11→06-12 entries** (1M reaction-review, 1W/1D/4H source phases, 4H Tier 1
> design/maps) **and the oldest 2026-06-15 tooling/correction entries** (4H Tier 1/Tier 2
> visual-review, Issue #32 gallery/ledger/overlap detector, single-fib edit-mode, 20171228
> correction, #32 milestone) archived to
> [post-reset part 1](log-archive-btc-postreset-part1.md).

