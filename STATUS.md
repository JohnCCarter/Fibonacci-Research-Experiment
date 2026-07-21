# STATUS — fibengine research

At-a-glance snapshot. **Last swept: 2026-07-20.** Full per-line detail + doc pointers:
[docs/research_wiki/reference/research-line-status.md](docs/research_wiki/reference/research-line-status.md).
Current working context: [handoff.md](docs/research_wiki/handoff.md). Why the project exists:
[north-star.md](docs/research_wiki/north-star.md).

## North star

Teach the machine to **select Fib legs (A→B) like the human** (facit = manual source-fibs). This is
**step 1** of a staged path: selection → descriptive level-reads → edge/backtest → **Genesis-V2**.
"No edge claim" = *not yet / not from this sub-study* (a validity gate), **not** a cap.

## Where we are

Step 1 is **not in goal**: the model ranks human legs above chance (AUC ~0.91) but does **not**
reproduce the selection (AP 0.057 vs 0.83 ceiling) — a modest single-feature (`cleanliness`) lead.
Controls are done, enrichment closed, the learning-curve is saturated → **more 4h data is low-leverage;
the lever is a richer notion of what makes a leg "yours"**. The context-free axis is exhausted;
**first positive on the sequential axis (2026-07-20): the previous fib's endpoint predicts the next
origin** (`sequential_origin_signal`, 4h: 0.256 vs 0.005 null — a component, not the selector;
advisory pending sign-off). Current bet: **contrastive capture (#42) + sequential conditioning**.

## Line status

| Line | Status |
|------|--------|
| Selection-learning (model selects legs like the human) | 🔬 active |
| Top-down "sniper" MTF nesting (1M→1W→1D) | ⏳ pending — user redraws fibs |
| BTC source-fib labeling 1M→4H | ✅ complete (1H deferred) |
| Corpus integrity / dedup / corrections | ✅ complete |
| Selection-learning controls (w-gap, stage-1, artifact) | ✅ complete |
| Tooling / ecosystem (#25, #30, #32) | ✅ complete |
| Fib behaviour (B-1) + context-conditioned | ⛔ closed (null) |
| Horizontal-structure event study | ⛔ closed (null) |
| Enrichment (`exclusivity`) | ⛔ closed (worse) |
| `cleanliness` matched-null crux | ⛔ closed (rejected — A8/A11/A9) |
| MTF confluence atlas | ⏸ parked (geometry, not edge) |
| Selection-learning mechanics (snapping / net-path) | ⏸ parked |
| Fib → Genesis-V2 (phase 0/1/2) | 💤 dormant (docs-only prereg) |
| Chart regression strategy | ⏸ deferred (#F) |

## Open issues

None — all research/tooling issues closed as of 2026-07-02 (**#31** answered: detection recall 0.902,
detection is not the bottleneck — selection is; see
[research-line-status](docs/research_wiki/reference/research-line-status.md)).

*(#37 closed 2026-06-25 as a verbatim duplicate of #35 — the principle is in AGENTS.md.)*

## Immediate next action

1. **Owner: sign off the cascade-probe results** — RAN 2026-07-20 → **`sequential_origin_signal`**
   on 4h (H1a 0.256 vs null 0.005, p<0.0005; ~all EXACT chains; advisory until signed).
   [Results](docs/research_wiki/reviews/btc-fib-cascade-conditioning-probe-results-20260720.md).
2. **User:** resume contrastive capture toward ≥30 windows (`scratchpad/annotation_batch1.md`) —
   prioritize 4h/1d windows early so track B overlaps the powered facit corpus.
3. **User:** classify the 7 degenerate same-candle fibs (handoff Open Questions, audit 2026-07-20).

Facit corpus: **484** base fibs (1M=13, 1w=24, 1d=76, 4h=371), locked in
[`data/labels/human_fib/MANIFEST.json`](data/labels/human_fib/MANIFEST.json)
(`corpus_manifest --verify`).
