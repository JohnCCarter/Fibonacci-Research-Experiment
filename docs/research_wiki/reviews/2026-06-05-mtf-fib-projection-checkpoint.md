# Checkpoint — MTF fib level projection (1W → 1D slice)

Date: 2026-06-05 · Run: `mtf_proj_20260605T122401Z` ·
Runner: [`fibengine.research.mtf_fib_level_projection`](../../research/MTF_FIB_LEVEL_PROJECTION.md)

> Research checkpoint + light triage. Descriptive only. Not an edge, not a signal,
> not a strategy. Human fib stays the locked source-of-truth.

## 1. What was proven

- **MTF projection runner exists** (`detect_ltf_level_interactions` + glue to the
  existing fingerprint/outcome/join layers).
- **HTF human fib levels are reused verbatim** — anchors not moved, not relabeled;
  level prices are read straight from the base human fib JSON.
- **1W human fib → 1D candles works** end-to-end (no network).
  Source fib: `fib_BTC-USD_1w_20250116T000000`.
- **42 LTF interactions** found (6 projected levels scanned from the leg end).
- **42 fingerprints** created (one per interaction).
- **168 outcome rows joined** (42 events × 4 horizons: 5/10/20/50).
- **0 unmatched, 0 skipped** (no missing-cache, no out-of-range events).
- **Existing fingerprint/outcome/toplist stack is reusable** as-is —
  `fib_toplist --run-dir <mtf_run>` ran directly on the MTF output and produced
  `toplist.csv` + `TOPLIST_NOTES.md` (116 buckets).

## 2. What was not proven

- **No edge.**
- **No trading signal.**
- **No stable behavior claim yet** — all 116 candidate buckets are `LOW SAMPLE`
  (`n_events < 5`); most are n=1–2.
- **No cross-timeframe comparison yet** — only one LTF (1D) has run.
- **4H/1H not tested** — caches are missing/shallow (ETH/SOL have no 4h/1h; BTC 4h is
  recent-only), so this was deferred, not attempted.

The Spearman hints in `TOPLIST_NOTES.md` (e.g. `post_remained_near_level_rate`,
`post_retest_count`, `pre_distance_atr_norm` flagged *watch*) are **single-fib,
low-N co-occurrences**, not evidence. They only mark fields *worth more data*.

## 3. Research interpretation

This **technically validates the original MTF idea**:

```
HTF fib    = map / source-of-truth   (locked human 1W fib)
LTF candles = behavior around levels  (measured 1D interactions)
```

The pipeline can take a locked HTF human fib and produce deterministic,
reproducible LTF interaction → fingerprint → outcome rows, with the layers kept
separate. What it has **not** shown is whether LTF behavior carries any stable
structure — that needs more fibs and more than one LTF.

The next useful test is **1W → 4H** and/or **1D → 4H**, once 4H data exists, to see
whether a finer timeframe reveals interaction structure that 1D-only missed.

## 4. Next recommended step

- **Do not change logic yet.**
- **Prepare 4H data later** (`fibengine.data.fetch --timeframes 4h`; ETH/SOL need a
  first fetch, BTC 4h needs deeper history).
- Then run the **same** projection pipeline:
  - `1W → 4H`
  - `1D → 4H`
- Compare whether LTF candle interaction reveals structure that 1D-only missed.
- Keep it descriptive: triage with `fib_toplist`, no tuning, no edge claims.

If a multi-fib / multi-LTF run still shows only LOW SAMPLE or unstable buckets, mark
the MTF track the same way as the 1D-only track: *working pipeline, no stable
evidence yet*.

## Layer separation (held this run)

| Layer | This run |
|---|---|
| `human_fib` | locked 1W BTC fib JSON, untouched |
| `projected_level` | `fib_level` + `fib_price` + `projected_from_timeframe=1w` |
| `relation` | `classify_candle` on each 1D bar |
| `fingerprint` | `pre_*` / `at_*` / `post_*` on 1D |
| `outcome` | `forward_return` / `mfe` / `mae` / … per horizon on 1D |

## Artifacts

- Run dir: `experiments/runs/mtf_fib_level_projection/2026-06-05/mtf_proj_20260605T122401Z/`
  - `interactions.jsonl`, `fingerprint_outcomes.jsonl`, `summary.json/csv`,
    `run_summary.json`, `toplist.csv`, `TOPLIST_NOTES.md`
- Results trail: `experiments/results/mtf_fib_level_projection.jsonl`

## 4H follow-up (same day) — structural, still low sample

Fetched BTC/USD 4h (7882 bars, 2022-10-31 → 2026-06-05; `limit_8000.csv`). ETH/SOL 4h
still absent (deferred). Ran the **same** pipeline on 4h, no logic/threshold changes.

| mapping | fib | LTF interactions | joined rows | unmatched | skipped | buckets (LOW SAMPLE) |
|---|---|---|---|---|---|---|
| 1W → 1D | `fib_BTC-USD_1w_20250116T000000` | 42 | 168 | 0 | 0 | 116 / 116 |
| 1W → 4H | same 1W fib | **87** | 348 | 0 | 0 | 184 (168 LOW SAMPLE; 16 reached n≥5) |
| 1D → 4H | `fib_BTC-USD_1d_20260407T000000` | 23 | 92 | 0 | 0 | 60 / 60 |

Runs: `mtf_proj_20260605T123339Z` (1W→4H), `mtf_proj_20260605T123413Z` (1D→4H).

**Does 4H reveal more detail than 1D?** Structurally yes — on the *same* 1W fib, 4H
finds ~2× more distinct level interactions (87 vs 42), so finer touches/retests that
1D-only collapses are now visible. The 16 n≥5 buckets are the first to clear LOW SAMPLE
on this track.

**Stable evidence?** No. The `fib_toplist` *watch* field sets differ across all three
runs (1W→1D, 1W→4H, 1D→4H don't agree), which is the expected signature of low-N
artifacts, not a stable relationship. 1D→4H is only ~2 months of 4h forward bars (a
2026 fib), so all 60 buckets are LOW SAMPLE.

**Read:** 4H adds interaction *resolution* (more structure observed), not *evidence*.
Next would be more BTC 1w/1d fibs projected to 4h (and ETH/SOL 4h once fetched) to grow
per-bucket N before any behavior is worth reading. Still descriptive — no edge claims.

## 4H sample-growth run (all human fibs → 4H)

Fetched ETH/USD + SOL/USD 4h (7881 bars each, 2022-10-31 → 2026-06-05); BTC 4h already
present. Ran the **same** pipeline (no logic/threshold changes) over every base human
fib per symbol×HTF → 4H, then `fib_toplist` per run, plus one combined run.
0 unmatched / 0 skipped everywhere.

| group | fibs | interactions | joined rows | buckets | n≥5 | n≥10 | n≥20 | max n |
|---|---|---|---|---|---|---|---|---|
| BTC 1W→4H | 12 | 507 | 2028 | 300 | 144 | 80 | 16 | 32 |
| BTC 1D→4H | 41 | 107 | 428 | 184 | 24 | 0 | 0 | 6 |
| ETH 1W→4H | 7 | 667 | 2668 | 316 | 164 | 104 | 36 | 36 |
| ETH 1D→4H | 44 | 76 | 304 | 132 | 12 | 4 | 0 | 10 |
| SOL 1W→4H | 7 | 681 | 2724 | 340 | 168 | 108 | 36 | 34 |
| SOL 1D→4H | 25 | 5415 | 21660 | 384 | 356 | 336 | 260 | 226 |
| **Combined** | **136** | **7453** | **29812** | **384** | **360** | **336** | **332** | **299** |

Combined toplist triage: `watch=[]`; weak = `post_retest_count`,
`post_remained_near_level_rate`; everything else noise-like. (Descriptive, not edge.)

### Sample-size answer

**Yes — 4H sample size is now sufficient for descriptive review.** Combined,
**332 / 384** buckets reach n≥20 (up from 0 at n≥20 in the single-fib 1W→1D slice).

### Important caveat (validity, not edge)

Volume is uneven and partly **cross-era**. The 4h cache starts 2022-10-31, but many
1D fibs are from 2017–2022 (anchor_b before the cache). For those, the scan start
clamps to the cache start, so the runner measures 2022–2026 4h candles against
historically-drawn level *prices*. This is geometrically valid (a level is just a
price line) but mixes eras. It explains **SOL 1D→4H = 5415 interactions** (old SOL
2021 levels repeatedly intersected by the 2022–2026 range) — that single group
dominates the combined n≥20 count. BTC 1D→4H stays small because pre-2022 BTC levels
($1k–20k) sit far below the 2022–2026 range, so they are simply not touched.

So for a *clean forward-window* descriptive review, prefer fibs whose `anchor_b`
≥ 2022-10-31 (e.g. BTC/ETH/SOL 1W from 2022+, the 2026 1D fibs). For a *historical
level memory* question (does price still react at old HTF levels years later?), the
cross-era projections are themselves the sample. Both are descriptive only.

Combined run: `mtf_proj_20260605T124041Z`. Per-group run dirs under
`experiments/runs/mtf_fib_level_projection/2026-06-05/`.

## Cohort split — clean-forward vs cross-era (4H)

Split the 4H inputs by `anchor_b` vs the 4h cache start (2022-10-31). Selection only —
no logic/threshold change; same pipeline + `fib_toplist` per cohort. 0 unmatched /
0 skipped both cohorts.

- **clean-forward** = `anchor_b ≥ 2022-10-31` (the fib's forward window is inside the 4h
  cache, so 4h candles are the actual post-leg behavior).
- **cross-era** = `anchor_b < 2022-10-31` (historical levels measured against the
  2022–2026 4h window → "historical level revisit analysis", not clean forward behavior).

| cohort | fibs | interactions | joined rows | buckets | n≥5 | n≥10 | n≥20 | max n |
|---|---|---|---|---|---|---|---|---|
| clean-forward | 14 | 617 | 2468 | 336 | 144 | 104 | 32 | 32 |
| cross-era | 122 | 6836 | 27344 | 384 | 360 | 336 | 308 | 276 |

Run dirs (2026-06-05): clean-forward `mtf_proj_20260605T124444Z`,
cross-era `mtf_proj_20260605T124448Z` (each with `toplist.csv` + `TOPLIST_NOTES.md`).

**Composition note:** clean-forward is **BTC + SOL only** — every ETH human fib is
pre-2022 (all 51 ETH fibs are cross-era). Clean-forward 1W fibs: BTC 4, SOL 3;
clean-forward 1D fibs: BTC 6 (all 2026), SOL 0. cross-era is dominated by SOL/ETH 1D.

**Read (descriptive, no edge):**
- *clean-forward* is the honest MTF-forward sample: 14 fibs give 617 interactions and
  32 buckets at n≥20 — enough for a first descriptive read, but thin per
  candidate×level×horizon and BTC/SOL-skewed (no ETH, no clean 1D except recent BTC).
- *cross-era* is large (6836) but is a different question (do old HTF level *prices*
  still get touched years later); its size mostly reflects historical levels sitting
  inside the later range, not forward reaction. Keep it separate; do not pool the two.
- toplist `watch=[]` in both cohorts → still no stable field; cohorts disagree on the
  weak set, consistent with low-N / different-question noise.

## Related

- [MTF_FIB_LEVEL_PROJECTION.md](../../research/MTF_FIB_LEVEL_PROJECTION.md) — design + run
- [2026-06-05 fingerprint/outcome checkpoint](2026-06-05-fib-fingerprint-outcome-checkpoint.md)
- [2026-06-05 n≥20 bucket review](2026-06-05-fib-n20-bucket-review.md) (1D-only track)
