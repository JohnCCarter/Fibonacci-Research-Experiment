# BTC/USD MTF Confluence Atlas — CP3 capstone (first pack, 2026-06-15)

Closes the **first CP3 visual-atlas pack**. CP1 enumerated cross-TF level clusters and CP2
tested epsilon sensitivity + clustering method; CP3 renders a small, deliberately-chosen set
of **visual cards** so a human can inspect the *geometry* of multi-timeframe Fibonacci
confluence on a real candle backdrop — one card per structural archetype, nothing more.

**Status: first pack complete — all cards human-approved (2026-06-15).**

## Purpose of CP3

Turn the CP1/CP2 cluster tables into human-readable charts that show **what a confluence
actually looks like** across timeframes, and make the *structural distinctions* from CP2
visible rather than tabular:

- a **tight, method-stable** 4-TF confluence (survives the strict definition),
- a **chaining-dependent** cluster that only exists under single-linkage (the contrast), and
- **zero-span exact-price** coincidences where several human-drawn levels land on one price.

CP3 is descriptive geometry only. It asserts **no** edge, signal, support/resistance, or
predictive claim.

## Cards built (first pack)

| Card | Archetype | Method | Span | TFs | Human status |
|------|-----------|--------|-----:|----:|--------------|
| **c001** | robust tight confluence | `fixed_band` | 0.00123 (≤ ε) | 4 | **approved** |
| **c002** | chaining-dependent contrast | `single_linkage` | 0.00627 (> ε) | 4 | **approved** |
| **c004** | zero-span exact-price | `fixed_band` | 0.0 | 3 | **approved** |
| **c006** | zero-span exact-price | `fixed_band` | 0.0 | 3 | **approved** |
| **c007** | zero-span exact-price | `fixed_band` | 0.0 | 3 | **approved** |

`epsilon_log = 0.005`, backdrop = **1d** candles (log y-axis) for all cards.

### What each card means

- **c001 — robust fixed-band 4-TF.** Four timeframes (1M/1w/1d/4h) inside a $36 band
  (~$29 274). Survives the strict complete-linkage (fixed-band) definition; the band width
  the eye cannot resolve is carried in the metadata box. The canonical "real" confluence.
- **c002 — chaining-dependent single-linkage contrast, NOT a tight fixed-band 4-TF.**
  Exists *only* under single-linkage: `price_span_log = 0.00627 > ε`, so it holds together by
  chaining and **dissolves entirely under fixed-band**. Headline discipline enforced — the
  chart never calls it a tight 4-TF; title reads *chaining-dependent 4-TF (single-linkage,
  span>ε)*, metadata adds *NOT tight fixed-band 4-TF*.
- **c004 / c006 / c007 — zero-span exact-price 3-TF.** `price_span_log == 0`: several
  human-drawn fib levels from three timeframes on the *identical* price (~$64 829 / $13 764 /
  $9 085). Immune to both epsilon and chaining — the structural opposite of c002. The
  degenerate `[min,max]` band (min==max) renders as a single exact-price line; the member
  table keeps every level individually source-traceable.

## Human inspection status

All five cards inspected on a 1d candle backdrop and **approved 2026-06-15**:

- **c001 approved** — robust fixed-band 4-TF.
- **c002 approved** — chaining-dependent single-linkage contrast; confirmed it is *not*
  presented as a tight fixed-band 4-TF.
- **c004 / c006 / c007 approved** — zero-span exact-price 3-TF; repr lines on-axis at the
  expected prices, no false band width when min==max, repeated-TF rows read as expected (not
  as errors), member tables legible, clean.png candle context reasonable.

Per-slice review pages:
[slice 1 / c001](btc-mtf-confluence-atlas-cp3-c001-20260615.md) ·
[slice 2 / c002](btc-mtf-confluence-atlas-cp3-c002-20260615.md) ·
[slice 3 / zero-span](btc-mtf-confluence-atlas-cp3-zero-span-20260615.md).

## Output paths (gitignored — no PNGs committed)

```
experiments/review/mtf_confluence_atlas/fixed_band/c001/{clean,levels}.png
experiments/review/mtf_confluence_atlas/single_linkage/c002/{clean,levels}.png
experiments/review/mtf_confluence_atlas/fixed_band/c004/{clean,levels}.png
experiments/review/mtf_confluence_atlas/fixed_band/c006/{clean,levels}.png
experiments/review/mtf_confluence_atlas/fixed_band/c007/{clean,levels}.png
```

`experiments/review/**` is gitignored; **no PNGs are committed**. Cards regenerate via
`python -m fibengine.research.mtf_confluence_atlas --cluster c001|c002|c004|c006|c007`.

## Known caveats

- **Cluster ids are positional.** `order_clusters` re-numbers clusters by sort key as the
  corpus or method changes, so a numeric id is *not* a stable handle. CP2's c004/c006/c007
  resolve to c002/c003/c004 under the current corpus.
- **Signatures are the stable selection mechanism.** Every card is resolved by a structural
  `ClusterSignature` (tf_count, exact timeframe set, repr price ± tol, `price_span_log` range,
  window-year range), never by a hard-coded id; resolution is **fail-closed** (exactly one
  match required). Output dirs are keyed on the **stable label**; titles show
  `label (cluster_id)` for traceability.
- **Charts show geometry, not edge.** A confluence here is a coincidence of human-drawn fib
  endpoints across timeframes. No support/resistance, signal, or predictive meaning is implied
  by any card.
- **Pack scope is deliberately small.** Five cards across three archetypes — not an
  exhaustive atlas of all clusters.

## Next decision

The first atlas pack is complete. Two options, **neither started without an explicit
decision**:

1. **Stop CP3 here** as the first (and possibly only) atlas pack — the three archetypes are
   now documented and approved.
2. **Later expand** with additional **fixed-band** clusters only (no single-linkage harvesting,
   no 1H, no reaction-review, no auto-fib, no signal/edge), one card per explicit selection.

No further atlas slices will be started without an explicit go decision.

## Verification (this capstone is docs-only)

No new card render, implementation, or cluster selection. Gates at close: `ruff check`,
`ruff format --check`, `scripts/check_repo_bounds.py`, full `pytest` — all green (406 passed).
No PNGs staged.
