# Research Wiki Log — BTC post-reset archive (part 1)

Archived entries from [log.md](log.md) to keep the active log within its size bound.
Covers the **2026-06-11 → 2026-06-12** source-fib completion milestones (1M reaction-review,
1W, 1D, 4H source phases + 4H Tier 1 design/maps). Append-only; do not edit.

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
