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

## [2026-06-15] fix | 20171228 source fib corrected (preview-first flow)

`fib_BTC-USD_4h_20171228T200000` corrected via preview-first flow: machine rendered 3
candidate anchor_a moves (gitignored previews), Chamoun chose `candidate_1`, then only the
real source JSON's anchor_a was edited 2017-12-28T20:00 @ 13611 → **2017-12-28T08:00 @
13145** (captures the full local low→high leg from the structural bottom; original was a
one-bar leg). anchor_b/direction/profile/scale/fib_id unchanged; levels recomputed via
`compute_levels` (log) and match the preview (0.382/0.5/0.618 = 14227.06/14013.79/
13803.71). Structural guard PASS via `fourh_source_fib_zoom --fib-id`. Ledger updated
candidate → corrected (verdict suspicious→ok-with-note, status correction-candidate→
corrected, new source_hash). Only this one fib_*.json changed; no artifacts committed.
Report: [`reviews/btc-4h-fib-20171228-correction-20260615.md`](reviews/btc-4h-fib-20171228-correction-20260615.md).
This closes the declutter → correction → ledger track.

## [2026-06-15] feat | Single-fib declutter edit-mode (labeling tool)

Added `--edit-fib-id` to `labeling/tool.py`: opens exactly one saved human source fib,
hides HTF overlays (the main lower-TF clutter), auto-fits the display window to the fib's
A→B span, and preloads its anchors as active high/low picks for assessment. Read-only on
load (nothing saved unless `w`); fail-closed on unknown/ambiguous fib-id or wrong
symbol/timeframe via new `human_fib.find_annotation`. Default behavior unchanged when the
flag is absent (all new paths gated). Level fidelity verified: pick-derived ladder ==
stored `ann.levels`. 10 tests (`tests/labeling/test_single_fib_edit_mode.py`); ruff + full
suite green (371 passed, 75.11% cov). No source labels changed; no new deps. This is the
tool support for the deferred `fib_BTC-USD_4h_20171228T200000` correction (correction
itself not done). Target command:
`python -m fibengine.labeling.tool --symbol BTC/USD --timeframe 4h --edit-fib-id fib_BTC-USD_4h_20171228T200000 --config config/settings.expansion.yaml`.

## [2026-06-15] decision | Milestone — Issue #32 top-3 complete; next track locked

Closing the Issue #32 tooling phase. Top-3 shipped and pushed on `feature/research-fib`:
`8f1e7a8` static HTML artifact gallery · `d6ab9ec` source-quality review ledger ·
`84b42db` overlap/dedup detector + anchor-convention doc. local == origin, working tree
clean, source-fib JSON unchanged, no new dependencies, no artifacts committed.

**Next active track (in order):** (1) single-fib declutter edit-mode in `labeling/tool.py`
(evaluate-later from #32; motivated by `20171228` deferring on GUI clutter) → (2) isolated
correction-pass on `fib_BTC-USD_4h_20171228T200000` (still correction-candidate in the
ledger; anchor_a only, body/close convention) → (3) update ledger row candidate → corrected.
**Also evaluate-later:** chart-regression strategy (structural/hash vs pytest-mpl,
binary-baseline / anti-blob question). 1H source labeling remains deferred.

## [2026-06-15] feat | Overlap/dedup detector + anchor convention (Issue #32 top-ROI #3)

Added `research/overlap_detector.py` — stdlib-only, report-only detector. Each fib is a
box in (time, log-price) space; per pair it computes time/price/box IoU + shared-anchor.
Flags candidates (box_iou≥0.5 or shared anchor) for human review — never edits labels,
never says "wrong". Fail-closed timeframe guard. Real run on 366 4H fibs: **22 candidate
pairs, all sharing anchor_b** (no pure-geometric overlap ≥0.5) → dominant signal is
sub-legs ending on the same swing, not duplicates. 20210110 pair confirmed (box_iou 0.51);
2017_h2 cluster present; strongest near-dup 20250506 pair (box_iou 0.70); `20171228`
correctly absent (anchor-quality issue, not duplication). Report:
[`reviews/btc-4h-overlap-candidates-20260615.md`](reviews/btc-4h-overlap-candidates-20260615.md)
+ CSV. Anchor convention (body/close vs wick, observed not absolute) documented in
[`labeling/HUMAN_FIB_ANNOTATION.md`](../labeling/HUMAN_FIB_ANNOTATION.md). 9 tests; ruff +
full suite green (361 passed, 75.07% cov). No source labels changed; no new deps.

## [2026-06-15] feat | Source-quality review ledger (Issue #32 top-ROI #2)

Added `research/review_ledger.py` — stdlib-only helper (csv/hashlib/json; no new deps)
that makes source-fib review verdicts machine-trackable. Flat CSV, controlled vocab
(verdict ∈ ok/ok-with-note/watchlist/suspicious; status ∈ accepted/noted/open/
correction-candidate/deferred/corrected), with a deterministic `source_hash`
(`sha256:<16 hex>` of the fib JSON bytes) tying each verdict to the exact facit version.
Generated the first ledger for the 4H Tier 2 sample-pass (8 rows) at
[`reviews/ledgers/btc-4h-source-quality-ledger.csv`](reviews/ledgers/btc-4h-source-quality-ledger.csv);
`fib_BTC-USD_4h_20171228T200000` represented as suspicious / correction-candidate. Schema
doc: [`reviews/ledgers/README.md`](reviews/ledgers/README.md). 12 tests
(`tests/research/test_review_ledger.py`: hash determinism, vocab validation,
correction-candidate representable, roundtrip, header check); ruff + full suite green
(352 passed, 74.91% cov). No source labels changed; CSV is committed text under `docs/`.

## [2026-06-15] feat | Static HTML artifact gallery (Issue #32 top-ROI #1)

Added `research/artifact_gallery.py` — stdlib-only helper (no new deps) that scans a
review PNG directory and writes a self-contained `index.html` beside it (relative links,
inline CSS/JS-free, clean+levels paired per item). Auto-detects both layouts: flat **map**
output (`..._<label>_4h_<kind>.png`) and nested **zoom** output (`<scope>/<fib_id>/
4h_<kind>.png`). Standalone helper by design — does **not** touch the render modules or
the existing markdown `_write_index`. Output lands under `experiments/review/**`
(gitignored; HTML not committed). 9 tests in `tests/research/test_artifact_gallery.py`
(both layouts, relative-links-only, empty/missing dir, no-external-deps, markdown index
untouched); ruff + full suite green (340 passed, 74.77% cov). Real smoke run: zoom (140
items) + map galleries written; `git status` confirms `index.html` is ignored.

Build: `python -m fibengine.research.artifact_gallery --root experiments/review/fourh_source_fib_zoom`.

## [2026-06-15] review | BTC/USD 4H visual confirmation Tier 2 — first manual sample-pass

First manual sample-pass of `fourh_source_fib_zoom.py` zoom artifacts. Artifacts:
103/103 rendered (2017_h2), 37/37 rendered (2021_dec2020_mar2021), 0 skipped.
Full review: [btc-4h-tier2-sample-review-20260615.md](reviews/btc-4h-tier2-sample-review-20260615.md).

**Sample set:** 8 fibs (4 per scope). **Result:** 7 OK / OK-with-note, **1 correction-candidate**.

**Correction candidate (visual review 2026-06-15):**
- `fib_BTC-USD_4h_20171228T200000` — initially watchlist (short-span, span $1,329, ankare
  1 bar isär). Visual review in labeling tool found a candle adjacent to leg A that fits
  better as anchor_a → reclassified **suspicious / correction-candidate**. Deferred to a
  future correction-pass: direct manual correction attempted but the GUI view is too
  cluttered with fib levels to move anchor_a safely; needs an isolated single-fib view or
  the exact target candle timestamp. **No label changed; source JSON unchanged.**

**Watchlist (unchanged):**
- Body/close vs wick convention — Jan 10 2021 pair (`20210110T080000` and
  `20210110T200000`) share identical anchor_b at ~$30,500 (body/close, not wick extreme
  ~$28,500). Consistent local convention, not documented globally. Add note to labeling docs.

**No label changes made** by this sample-pass.

## [2026-06-15] review | BTC/USD 4H visual confirmation Tier 1 — map review complete

Reviewed all 11 groups from `fourh_source_fib_map.py` (maps regenerated 2026-06-15).
Full review: [btc-4h-tier1-map-review-20260615.md](reviews/btc-4h-tier1-map-review-20260615.md).

**Result:** 9 of 11 groups map-OK. 2 groups need Tier 2:

- **`2017_h2` (103 fibs) — full Tier 2:** Sep–Dec 2017 parabola; every zone globally
  unreadable on the annual map. Per-fib zoom needed for all 103 fibs.
- **`2021` (partial) — Tier 2 for Dec 2020 → Mar 2021 cluster:** Initial bull-leg
  zone (anchor_a in Jan–Mar 2021, ~37 fibs) is unreadable. Apr–Dec 2021 is map-OK.
  Scope: `anchor_a in [2021-01-01, 2021-04-01)`. Dec 2020 fibs are in the 2020 group
  (map-OK) and do not need Tier 2.

**Threshold rule confirmed:** local density per zone determines readability, not total
fib count. A 55-fib group (2021) can be mostly map-OK; a 103-fib group (2017_h2) over
4 months is globally unreadable.

**Chart quality:** y-axis log confirmed (`ax.set_yscale("log")` line 246 of
`monthly_fib_map.py`). X-axis label density is a display limitation of wide Tier 1
maps; Tier 2 per-fib zoom windows will be narrower and more readable.

**Next:** implement Tier 2 `fourh_source_fib_zoom.py`.

> **2026-06-11→06-12 entries** (1M reaction-review, 1W/1D/4H source phases, 4H Tier 1
> design/maps) archived to [post-reset part 1](log-archive-btc-postreset-part1.md).

