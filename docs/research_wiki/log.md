# Research Wiki Log

Append-only trail of wiki ingests, decisions, and review sessions.

Use headings like:

```text
## [YYYY-MM-DD] type | Short title
```

Types: `ingest`, `decision`, `review`, `question`, `maintenance`.


> Older entries (2026-06-10 and earlier): [part 3](log-archive-pre-btc-reset-part3.md) →
> [part 2](log-archive-pre-btc-reset-part2.md) → [part 1](log-archive-pre-btc-reset-part1.md)

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

## [2026-06-12] review | BTC/USD 4H visual confirmation Tier 1 — annual source-fib maps built

Implemented `research/fourh_source_fib_map.py` (Tier 1 of the locked design): annual
combined 4H source-fib maps, fibs grouped by `anchor_a` year, dense years (>60 fibs)
split into calendar half-years. Reuses `_draw_map` / `_load_fibs` / `_nearest_pos` /
`_short_id` from `monthly_fib_map` unchanged; no snap (source TF == chart TF == 4h);
each group windowed by its fib span `[min(anchor_a) − pad, max(anchor_b) + pad]` (not
calendar boundaries, so a December fib whose anchor_b crosses into the next year still
renders). Fail-closed guard adapted to `SOURCE_TF="4h"` (timeframe/profile/scale/0.236/
human-manual/no candidate-auto-inferred). 14 tests in `tests/research/test_fourh_source_fib_map.py`;
ruff + repo-bounds + full suite pass (one pre-existing flaky `test_synthetic_ohlcv_high_ge_low`,
untouched).

**Run finding (real facit + cache, expansion config):** all **366/366 fibs drawn, 0
skipped**, across **11 groups** — 2017 split 13 (h1) / **103 (h2)**, 2018=33, 2019=26,
2020=31, 2021=55, 2022=24, 2023=17, 2024=22, 2025=34, 2026=8. Mid-density maps (e.g.
2022, 2019) are cleanly scannable. **2017_h2 (~103 fibs, the Sep–Dec parabolic run)
exceeds map-reviewable density → flags 2017 for Tier 2 `fourh_source_fib_zoom`.** That
is the Tier-1 deliverable's signal (per design: build Tier 2 only where Tier 1 shows
per-fib zoom is needed). No reaction-review, no events, no trading conclusions. Output
under `experiments/review/fourh_source_fib_map/` (gitignored).

## [2026-06-12] decision | BTC/USD 4H visual confirmation / source-quality review — design locked

4H is the lowest active timeframe (1H paused). 4H source-facit locked (366 fibs,
2017-01-05 → 2026-06-05, up=169/down=197, log scale, `tradingview_log_chamoun`,
`[0, 0.382, 0.5, 0.618, 0.786, 1]`, no 0.236, human/manual). Next phase: **4H visual
confirmation / source-quality review** — not reaction-review, not 1H.

**Tier 1 (first implementation):** `fourh_source_fib_map.py` — annual combined 4H candle
maps, fibs grouped by `anchor_a` year; ~10 charts (~20 PNGs); fast source-quality scan
over 366 fibs without per-fib overhead. Fail-closed: `timeframe==4h`, log,
`tradingview_log_chamoun`, no 0.236, human/manual, no candidate/auto/inferred.
**Tier 2 (on-demand, after Tier 1):** `fourh_source_fib_zoom.py` — per-fib windowed 4H
charts. Build only if Tier 1 shows per-fib zoom is needed.

Reactive modules (`source_fib_projection_review`, `source_fib_projection_chart`) are NOT
used — no events, no `review_sample.csv`, no interactions, no trading conclusions. Full
design:
[btc-4h-visual-confirmation-design-20260612.md](reviews/btc-4h-visual-confirmation-design-20260612.md).

## [2026-06-12] review | BTC/USD 4H source-fib phase complete — 366 fibs

366 manual 4H source fibs drawn and verified: timeframe `4h`, log scale,
`tradingview_log_chamoun`, levels `[0, 0.382, 0.5, 0.618, 0.786, 1]`, no 0.236,
endpoint mapping (ratio 0.0=anchor_b / 1.0=anchor_a), anchor direction, log-spacing,
human/manual only. Coverage **2017-01-05 → 2026-06-05**; **up=169 / down=197**.
366/366 schema verification PASS (0 failures). This is **source-labeling completion,
not reaction-review** — visual confirmation / reaction-review is a later, separate
decision. No auto-fib, no trading conclusions. Separation preserved across 1M source /
1M→1W projection / true 1W source / true 1D source / true 4H source fibs.

## [2026-06-11] review | BTC/USD 1D source-fib labeling complete (source-facit) — 67 fibs

67 manual 1D source fibs drawn and verified: timeframe `1d`, log scale,
`tradingview_log_chamoun`, levels `[0, 0.382, 0.5, 0.618, 0.786, 1]`, no 0.236,
endpoint mapping (ratio 0.0=anchor_b / 1.0=anchor_a), anchor direction, log-spacing,
human/manual only. Coverage **2017-01-05 → 2024-12-20**; **34 down / 33 up**. This is
**source-labeling completion, not reaction-review** — reaction-review / visual
confirmation is a later, separate phase (not required for source completion). No
auto-fib, no trading conclusions. Separation preserved across 1M source / 1M→1W
projection / true 1W source / true 1D source fibs.

## [2026-06-11] review | BTC/USD 1W source-fib phase complete — 21 fibs, map + per-fib 4H zoom

21/21 manual 1W source fibs drawn (log scale, `tradingview_log_chamoun`) and verified
(profile, scale, levels `[0, 0.382, 0.5, 0.618, 0.786, 1]`, no 0.236, anchor direction,
human/manual only). Added `research/weekly_source_fib_map` (combined 1W/1D/4H — 1W/1D
usable, combined 4H too compressed) and `research/weekly_source_fib_zoom` (per-fib
windowed 4H — usable). Strict separation kept between 1M source, 1M→1W projection
(`weekly_projection_map`), and true 1W source fibs; fail-closed guards reject non-1W /
non-log / wrong-profile / 0.236 / non-human fibs. No auto-fib, no trading conclusions.
Commits `4eb2f4b`, `939de97`, `e379fae`.

## [2026-06-11] review | BTC/USD 1M reaction-review cycle complete — all 9 source fibs

All 9 human-drawn 1M source fibs reviewed through 1D + 4H using
`source_fib_projection_review` + `source_fib_projection_chart` (log scale,
`tradingview_log_chamoun`). Review windows confirmed in `review_windows.yaml`
(anchor_b → next macro boundary; 20260101 window extends to latest cache 2026-06-08).
Total: 62 1D events, 127 4H events across the full set.
Summary artifact: [reviews/btc-1m-reaction-review-cycle-20260611.md](reviews/btc-1m-reaction-review-cycle-20260611.md).

