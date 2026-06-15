# BTC/USD MTF Confluence Atlas — CP3 slice 1 (c001 card, 2026-06-15)

First visual-atlas slice. Renders **one** confluence card for the single robust 4-TF
cluster (c001) under the **fixed-band** method at the primary `epsilon_log = 0.005`, on a
**1d** candle backdrop. This is the CP2-corrected, method-stable confluence.

**Status: generated — pending human visual inspection.** This page does **not** assert the
card design is approved. Next decision: approve the card design or adjust it (see
*Candidate adjustments*), then proceed to the c002 chaining-dependent **contrast** card.

**Scope honored:** fixed-band first, c001 only; no c002, no side-by-side, no full atlas, no
1H, no reaction-review, no auto-fib, no trading/signal/edge, no new deps, no committed PNG.

Helper: [`research/mtf_confluence_atlas.py`](../../../src/fibengine/research/mtf_confluence_atlas.py)
(stdlib + existing matplotlib stack). Summary contract: `render_summary.cluster_atlas_summary`
+ golden snapshot `tests/research/snapshots/cluster_atlas_summary.json`.

---

## Resolved cluster

Resolved by **structural signature** (not a hard-coded id): `tf_count == 4`, timeframes
exactly `{1M, 1w, 1d, 4h}`, `representative_price ≈ 29274 ± 200`, `price_span_log ≤ 0.005`,
window year 2021. Exactly **one** fixed-band cluster matches → fail-closed resolution OK.

| Field | Value |
|-------|-------|
| cluster_id (fixed-band) | `c001` |
| method | `fixed_band` |
| epsilon_log | `0.005` |
| backdrop | `1d` candles, log y-axis |
| representative_price | 29274 |
| band (min–max) | 29247 – 29283 |
| **price_span_log** | **0.00123** (≈0.12%) |
| tf_count | 4 |
| ratios | 0.0, 1.0 (anchor endpoints) |
| window | 2021-01-21 → 2021-06-01 |

### Members (source-traceable)

| TF | ratio | price | fib_id |
|----|------:|------:|--------|
| 1M | 0.0 | 29247 | `fib_BTC-USD_1M_20210401T000000` |
| 1w | 1.0 | 29283 | `fib_BTC-USD_1w_20210121T000000` |
| 1d | 1.0 | 29283 | `fib_BTC-USD_1d_20210127T000000` |
| 4h | 0.0 | 29283 | `fib_BTC-USD_4h_20210126T200000` |

Superseded `20250506T080000` **absent** (fail-closed guard active). No 1H member.

## Card layers

- 1d candles (log y-axis), window `[cluster window ± 30 bars]`.
- Shaded `[min, max]` confluence band + representative-price line.
- (levels view) one horizontal line per member level, coloured by timeframe, labelled
  `TF ratio @ price  fib_id`; legend lists member TFs.
- Metadata box: `method=fixed_band`, `epsilon_log=0.005`, `price_span_log=0.00123`,
  `tf_count=4`, band, repr — the CP2-corrected headline.

Output (gitignored): `experiments/review/mtf_confluence_atlas/fixed_band/c001/{clean,levels}.png`.

## Observed

- The four member levels sit within $36 (29247–29283), so on the 1d log axis the band is a
  near-single line — exactly as the 0.12% span predicts. The **metadata box carries the
  width** the eye cannot resolve.

## Candidate adjustments (for the human inspection decision)

- **Member-label stacking:** because all four members are within $36, their per-line labels
  overlap and only the topmost is individually legible. The legend still distinguishes the
  TFs. Options if this matters: stagger labels vertically, or move them to a side table.
  Deferred to the inspection decision — not changed in slice 1.

## What this is NOT

No support/resistance, edge, or predictive claim — a geometric coincidence of human-drawn
levels. Not human-approved yet. Not a full atlas. c002 is **not** rendered here (it is
chaining-dependent, not a tight 4-TF confluence — a future contrast card).

## Verification

- Signature resolves to exactly one fixed-band cluster on the real corpus (462 fibs, 2772
  level rows); members reconstructed in-process from `LevelRow` (not the truncated CSV).
- 10 unit tests (signature unique/zero/ambiguous/wrong-year/over-span, band reconstruction,
  superseded + off-protocol guards, full render + summary contract + golden snapshot,
  fail-closed on absent signature). No PNG baselines.
- PNGs confirmed gitignored (`git check-ignore`); none staged.

## Next step

1. **Human visual inspection of the c001 card** → approve card design or adjust.
2. Only after approval: **c002 chaining-dependent contrast card** (single-linkage, labelled
   `span > ε`), then zero-span 3-TF cards (c004/c006/c007).
