# BTC/USD MTF Confluence Table — Checkpoint 1 (2026-06-15)

Read-only confluence table. **First slice of the MTF confluence atlas (#1).** Answers one
structural question on the locked corpus: *do stored fib level prices from ≥2 timeframes
cluster together in log-price while their anchor time-windows overlap?*

**Scope honored:** read-only, no chart, no visual atlas, no trading/signal/edge
interpretation, no 1H, no reaction-review, no auto-fib, no source-label change, no epsilon
tuning, no new deps, no committed PNG/artifacts. New code is stdlib-only + tested.

Helper: [`research/mtf_confluence.py`](../../../src/fibengine/research/mtf_confluence.py)
(stdlib, 10 tests). Committed table: [btc-mtf-confluence-table-20260615.csv](btc-mtf-confluence-table-20260615.csv).

---

## Observed

- Active corpus flattened to level rows: **2772 level rows from 462 fibs** (1M=9, 1w=21,
  1d=67, 4h=365; each fib contributes its 6 stored levels). Superseded
  `20250506T080000` is absent (deleted) — not loaded.
- At the fixed primary threshold **epsilon_log = 0.005** (≈0.5% log-price), with the
  cross-TF (≥2 distinct timeframes) + overlapping-anchor-window requirement:
  **222 confluence clusters**.
- price_span_log distribution across clusters: min 0.0, median **0.00199**, max **0.01643**;
  **30/222** clusters exceed epsilon_log (single-linkage chaining — see Unverified).

## Inferred

- Multi-timeframe level confluence **does exist** in the corpus and is not rare: 222
  clusters, including **2 four-timeframe** clusters and **24 three-timeframe** clusters.
- The structure is dominated by the **denser timeframes**: `1d,4h` alone accounts for 143/222
  (64%). This is expected — 4h has 365 fibs and 1d has 67, so they produce the most level
  rows and the most chances to coincide. Higher-TF participation (1M/1w) is rarer and
  therefore more notable when it appears.
- Confluence concentrates around known structural inflections (2021 cycle top region
  ~29k; 2022–23 bottom region ~21k; 2017 early lows ~970), consistent with the corpus
  capturing the same swings at multiple resolutions.

## Unverified

- **Chaining:** clusters are connected components (single-linkage). 30/222 have
  price_span_log > epsilon_log because rows link transitively via intermediate members,
  so a cluster's full band can exceed 0.5%. This is reported (`price_span_log`), not hidden;
  whether to switch to a fixed-band (complete-linkage) definition is a **Checkpoint 2**
  sensitivity question, not a CP1 decision.
- **Robustness to epsilon:** whether the 222 count and the strong clusters survive at other
  epsilon values — deliberately deferred to CP2 (no tuning here).
- Whether high-TF clusters (1M present) are structurally meaningful vs coincidental — this
  is a confluence *count*, not a claim about price behavior.

---

## Confluence definition

For every active source fib, each of its 6 stored levels (`ratio ∈
{0, 0.382, 0.5, 0.618, 0.786, 1}`) becomes a **level row** at `log(price)`, with the fib's
anchor time-window `[min(anchor_a,anchor_b), max(...)]`. Two level rows are **connected**
iff `|Δlog_price| ≤ epsilon_log` **and** their anchor windows overlap. A **confluence
cluster** is a connected component spanning **≥2 distinct timeframes**. This is *not* the
segment IoU of [`overlap_detector`](btc-4h-overlap-candidates-20260615.md) — that boxes the
`anchor_a→anchor_b` segment; here we cluster the horizontal level prices.

## Epsilon policy

- Primary threshold **chosen before results: `epsilon_log = 0.005`** (≈0.5% in price),
  as specified for CP1. Not tuned to produce clusters.
- Multi-epsilon sensitivity is **Checkpoint 2**, deliberately excluded here.

## Count results

- Level rows: **2772** (from 462 fibs). Clusters (≥2 TF): **222**.

### Breakdown per timeframe combination

| Timeframes | Clusters |
|------------|---------:|
| 1d,4h | 143 |
| 1w,4h | 30 |
| 1w,1d,4h | 16 |
| 1M,4h | 13 |
| 1M,1w | 4 |
| 1w,1d | 4 |
| 1M,1w,4h | 4 |
| 1M,1d,4h | 3 |
| 1M,1d | 2 |
| **1M,1w,1d,4h** | **2** |
| 1M,1w,1d | 1 |
| **Total** | **222** |

By timeframe-count: 4-TF = **2**, 3-TF = **24**, 2-TF = **196**.

### Top clusters (deterministic order: tf_count desc, level_count desc, span asc, …)

| id | TFs | timeframes | levels | price band | span_log | time window |
|----|----:|-----------|------:|------------|---------:|-------------|
| c001 | 4 | 1M,1w,1d,4h | 4 | 29247–29283 | 0.00123 | 2021-01-21 → 2021-06-01 |
| c002 | 4 | 1M,1w,1d,4h | 4 | 21092–21225 | 0.00627 | 2022-12-29 → 2023-07-01 |
| c003 | 3 | 1w,1d,4h | 6 | 972–982 | 0.00975 | 2016-12-29 → 2017-03-04 |
| c004 | 3 | 1M,1w,1d | 5 | 64829 | 0.0 | 2020-03-12 → 2021-06-01 |
| c005 | 3 | 1M,1w,4h | 5 | 47638–48002 | 0.00762 | 2021-01-21 → 2021-06-01 |
| c006 | 3 | 1w,1d,4h | 4 | 13764 | 0.0 | 2019-05-12 → 2020-03-12 |
| c007 | 3 | 1w,1d,4h | 4 | 9085 | 0.0 | 2019-07-04 → 2019-07-17 |
| c008 | 3 | 1w,1d,4h | 4 | 11429–11430 | 0.00008 | 2019-07-04 → 2019-07-17 |
| c009 | 3 | 1M,1d,4h | 4 | 30998–31136 | 0.00445 | 2022-04-01 → 2022-11-01 |
| c010 | 3 | 1M,1w,4h | 4 | 39556–39791 | 0.00591 | 2021-01-21 → 2021-06-01 |

### Example rows (members)

- **c001** (4-TF, ~29274): `fib_..._1M_20210401T000000` · `_1w_20210121T000000` ·
  `_1d_20210127T000000` · `_4h_20210126T200000` (ratios 0.0/1.0 — anchor endpoints
  coinciding across all four TFs near $29.3k, Jan–Jun 2021).
- **c002** (4-TF, ~21167): `fib_..._1M_20230101T000000` · `_1w_20221229T000000` ·
  `_1d_20230107T000000` · `_4h_20230312T120000` (ratios 0.382/0.618, late-2022 bottom region).

Full member lists (summarized at 8 ids) in the committed CSV; unabridged level rows in the
gitignored `experiments/review/mtf_confluence/btc-mtf-levels.csv`.

---

## What this shows

- MTF level confluence **is present and structured**, not absent — the corpus is usable as
  a multi-resolution map at the structural level (counts only).
- The strongest confluences land at recognizable cycle inflections and include rare
  all-four-timeframe agreements (c001, c002).

## What this does NOT show

- **No** trading signal, edge, support/resistance strength, or predictive claim — these are
  geometric coincidences of human-drawn levels, nothing more.
- **No** robustness claim: the count is at a single epsilon; chaining inflates some bands.
- **No** visual confirmation (deferred to CP3, conditional).
- Confluence count is biased toward dense timeframes (1d/4h) by construction.

---

## Stop/Go → Checkpoint 2

**GO.** Meaningful multi-TF clusters exist (222; 2×4-TF, 24×3-TF) — well above the
"near-zero / all-noise → stop" bar. Proceed to **Checkpoint 2 (sensitivity/robustness)**:
re-run at 2–3 epsilon values + test a complete-linkage (fixed-band) cluster definition to
measure how cluster counts and the strong clusters move, and whether chaining (30/222 over
epsilon) materially changes the picture. Still no chart, no tuning-to-fit, no trading
conclusions. Visual atlas (CP3) remains conditional on CP2.

## Verification

- Counts re-derived on disk (sidecar-excluded); `flatten_levels` loads 462 fibs / 2772 rows.
- Superseded `fib_BTC-USD_4h_20250506T080000` absent on disk → not in level rows.
- New module stdlib-only; 10 unit tests (flatten, sidecar-exclusion, no-mutation, proximity,
  time-overlap, cross-TF requirement, deterministic ordering, CSV header stability).
- No source labels changed; committed table is text CSV under `docs/`; large levels CSV is
  gitignored under `experiments/review/mtf_confluence/`.

## Links

- [next-research-plan](btc-source-fib-next-research-plan-20260615.md) · [corpus-integrity](btc-source-fib-corpus-integrity-20260615.md)
- [committed confluence CSV](btc-mtf-confluence-table-20260615.csv)
- [overlap detector (segment-based, different question)](btc-4h-overlap-candidates-20260615.md)
