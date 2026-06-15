# BTC/USD MTF Confluence Atlas — CP3 slice 2 (c002 contrast card, 2026-06-15)

Second visual-atlas slice. Renders **one** *contrast* card for the chaining-dependent 4-TF
cluster (c002, ~21167, 2022-12 → 2023-07) under the **single-linkage** method at
`epsilon_log = 0.005`, on a **1d** candle backdrop. It exists only under single-linkage:
its `price_span_log` exceeds epsilon, so it holds together purely by chaining and **dissolves
entirely under fixed-band**. The card is the deliberate counterpoint to the tight c001 card.

**Status: generated — pending human visual inspection.** This page does **not** assert the
card is approved.

**Headline discipline:** c002 is **never** presented as a tight 4-TF confluence. The chart
title reads *"chaining-dependent 4-TF (single-linkage, span>ε)"* and the metadata box states
`chaining-dependent (span > epsilon)` + `NOT tight fixed-band 4-TF`.

**Scope honored:** c002 contrast only; no zero-span / 3-TF cards, no full atlas, no
side-by-side, no fixed-band redesign, no 1H, no reaction-review, no auto-fib, no
trading/signal/edge, no new deps, no committed PNG.

Helper: [`research/mtf_confluence_atlas.py`](../../../src/fibengine/research/mtf_confluence_atlas.py)
— now method-aware (`--cluster c001|c002` pairs signature + method). Same summary contract
(`render_summary.cluster_atlas_summary`).

---

## Resolved cluster

Resolved by **structural signature** (not a hard-coded id): `tf_count == 4`, timeframes
exactly `{1M, 1w, 1d, 4h}`, `representative_price ≈ 21167 ± 200`, `price_span_log ∈
[0.005, 0.01]` (the `min_span_log = epsilon` lower bound *guarantees* chaining — resolution
fail-closes if the cluster were ever tight), window years 2022→2023. Exactly **one**
single-linkage cluster matches → fail-closed resolution OK.

| Field | Value |
|-------|-------|
| cluster_id (single-linkage) | `c002` |
| method | `single_linkage` |
| epsilon_log | `0.005` |
| backdrop | `1d` candles, log y-axis |
| representative_price | 21167 |
| band (min–max) | 21092 – 21225 |
| **price_span_log** | **0.006272** (> epsilon → chaining-dependent) |
| tf_count | 4 (under single-linkage only) |
| window | 2022-12-29 → 2023-07-01 |

### Members (source-traceable)

| TF | ratio | price | fib_id |
|----|------:|------:|--------|
| 1M | 0.618 | 21225 | `fib_BTC-USD_1M_20230101T000000` |
| 1w | 0.382 | 21092 | `fib_BTC-USD_1w_20221229T000000` |
| 1d | 0.382 | 21131 | `fib_BTC-USD_1d_20230107T000000` |
| 4h | 0.618 | 21221 | `fib_BTC-USD_4h_20230312T120000` |

Superseded `20250506T080000` **absent** (fail-closed guard active). No 1H member.

## Member-reconstruction fix (shared code)

The 1M member level (0.618 @ 21224.78) sits exactly on the rounded band maximum. Cluster
min/max are stored rounded to 2 decimals while level rows carry the raw price, so the raw
1M level read *just outside* the rounded band and the reconstruction dropped it (3 of 4).
`band_member_rows` now applies a 1-cent tolerance (covers the ≤0.005 rounding error), and
`render_confluence_card` **fail-closes** if the rebuilt row count ≠ `cluster.level_count`.
This is a bug fix in shared code, not a fixed-band redesign: the c001 card re-renders
**identically** (its members sit well inside the band; verified 4/4).

## What this is NOT

No support/resistance, robust confluence, edge, or predictive claim. c002 is a chaining
artifact of single-linkage — a geometric coincidence of human-drawn levels that does **not**
survive the complete-linkage (fixed-band) definition. Not human-approved yet. Not a full atlas.

## Verification

- Signature resolves to exactly one single-linkage cluster on the real corpus; members
  reconstructed in-process from `LevelRow` (4/4 after the tolerance fix).
- Full suite green (404 passed); +1 unit test for `min_span_log` + multi-year window
  resolution. c001 golden snapshot unchanged.
- PNGs gitignored; none staged.

## Next step

1. **Human visual inspection of the c002 contrast card** → approve or adjust.
2. Only after approval: zero-span 3-TF cards (c004/c006/c007).

Output (gitignored): `experiments/review/mtf_confluence_atlas/single_linkage/c002/{clean,levels}.png`.
