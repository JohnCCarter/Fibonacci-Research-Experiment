# BTC/USD MTF Confluence Atlas — CP3 slice 3 (zero-span 3-TF cards, 2026-06-15)

Third visual-atlas slice. Renders **three** *exact-price* confluence cards under the
**fixed-band** method at `epsilon_log = 0.005`, on a **1d** candle backdrop. Each is a
**zero-span** cluster (`price_span_log == 0`): several human-drawn fib levels from three
timeframes landing on the *identical* price. Zero-span coincidences are immune to both epsilon
and chaining and survive trivially — the structural opposite of the c002 chaining card.

**Status: human-approved (2026-06-15).** All three zero-span cards approved after visual
inspection. Pack closed in the [CP3 capstone](btc-mtf-confluence-atlas-cp3-20260615.md).

## Label ↔ id mapping (read this first)

The labels **c004 / c006 / c007** are CP2's stable labels (see
[CP2 sensitivity](btc-mtf-confluence-sensitivity-20260615.md) line ~132: "*c004/c006/c007 at
\$64829/\$13764/\$9085*"). Cluster ids are **positional** (`order_clusters` re-numbers as the
corpus changes), so under the *current* corpus these resolve to **different** ids. Resolution
is by **structural signature**, never by id; the chart title shows both as `label (cluster_id)`.

| Label (CP2) | Current id | repr price | timeframes | levels | window |
|-------------|-----------|-----------|-----------|-------:|--------|
| **c004** | `c002` | 64,829 | 1M, 1w, 1d | 5 | 2020-03-12 → 2021-06-01 |
| **c006** | `c003` | 13,764 | 1w, 1d, 4h | 4 | 2019-05-12 → 2020-03-12 |
| **c007** | `c004` | 9,084.7 | 1w, 1d, 4h | 4 | 2019-07-04 → 2019-07-17 |

Each signature matches **exactly one** fixed-band cluster (`tf_count == 3`, exact timeframe
set, `repr ≈ price ± 50`, `price_span_log == 0`, window-year range) → fail-closed resolution OK.

## Members (source-traceable)

**c004** (5 levels @ 64,829): `1M_20201001` (r0), `1M_20210401` (r1), `1w_20200312` (r0),
`1w_20210121` (r0), `1d_20210414` (r1) — repeated-TF rows are expected (5 distinct fibs, 3 TFs).
**c006** (4 @ 13,764): `1w_20190620` (r1), `1d_20190610` (r0), `4h_20190512` (r0), `4h_20190626` (r1).
**c007** (4 @ 9,085): `1w_20190704` (r0), `1d_20190710` (r0), `4h_20190710` (r0), `4h_20190716` (r0).

Superseded `20250506T080000` **absent** in all three (fail-closed guard). No 1H member.
Member reconstruction == `level_count` for each (fail-closed cross-check; 5/4/4).

## Card layers

- 1d candles (log y-axis), window `[cluster window ± 30 bars]`.
- The `[min, max]` band is **degenerate** (min == max), so no shaded band — the
  representative line **is** the confluence (the exact price). Member level lines coincide on
  it; the member table keeps each individually source-traceable.
- Title descriptor: `zero-span N-TF (fixed-band, exact-price)` — never "tight"/"robust".
- Metadata box adds: `zero-span (exact-price coincidence)` + `N levels share one price across
  M TFs`.

Output (gitignored): `experiments/review/mtf_confluence_atlas/fixed_band/{c004,c006,c007}/{clean,levels}.png`.

## Observed (visual)

All three representative lines are **on-axis** (the exact price intersects the candle range in
the window): c004 at the Apr-2021 top (~64.8k), c006 at the Jun-2019 high (~13.8k), c007 at
the Jun/Jul-2019 ~9.1k level the price revisited several times. The exact-price story renders
honestly — N levels on one line, no artificial band width.

## What this is NOT

No support/resistance, robust confluence, edge, or predictive claim. A zero-span cluster is a
geometric coincidence of human-drawn fib endpoints at one price across three timeframes —
nothing about price behaviour is asserted. Not human-approved yet. Not a full atlas.

## Verification

- 3 signatures resolve to exactly one fixed-band cluster each on the real corpus; band
  reconstruction == level_count (5/4/4) via the fail-closed cross-check.
- c001 re-rendered identically (out_dir keyed on the stable signature label; label == id for
  c001/c002 so their dirs/golden snapshot are unchanged).
- +2 unit tests (`test_mtf_confluence_atlas_zero_span.py`: span-0 matches, nonzero fails-closed).
  Full suite green. No new golden snapshots for the three cards (synthetic zero-span corpus
  would exceed the test-file line bound — scope cut, logged).
- PNGs gitignored; none staged.

## Next step

Approved. First CP3 atlas pack closed — see the
[CP3 capstone](btc-mtf-confluence-atlas-cp3-20260615.md). No further atlas slices without an
explicit go decision.
