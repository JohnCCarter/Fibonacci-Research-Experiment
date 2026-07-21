# STATUS — fibengine research

At-a-glance snapshot. **Last swept: 2026-07-21.** Full per-line detail + doc pointers:
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
**first positive on the sequential axis (2026-07-20, signed off 2026-07-21): the previous fib's
endpoint predicts the next origin** (`sequential_origin_signal`, 4h: 0.256 vs 0.005 null — a
component, not the selector). Sequential follow-ups (2026-07-21): chaining is **not serially
clustered** (`no_chain_clustering`, confound-guarded) → per-leg feature, no regime model; and the
**implicit-negative audit** showed 75 % of 4h negatives are coverage-weak ("never reviewed" ≠
"rejected") — the low absolute AP is partly a passive-corpus artifact, which **raises** the
priority of contrastive capture. Current bet: **contrastive capture (#42, now with a
desert-targeted batch 2) + the per-leg sequential feature (prereg'd, run pending review)**.

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

1. **Owner: sign off two advisory results from the 2026-07-21 autonomous session** —
   [chain-clustering `no_chain_clustering`](docs/research_wiki/reviews/btc-fib-chain-clustering-probe-results-20260721.md)
   and (when run) the sequential-feature study
   ([prereg](docs/research_wiki/reviews/btc-fib-sequential-feature-prereg-20260721.md)).
2. **Owner (home GUI):** fix the 7 degenerate misclick fibs (worklist in
   [handoff](docs/research_wiki/handoff.md)) + decide the 1w `20170316` overwrite question
   (restore the lost base leg or keep the nesting redraw), then relock `MANIFEST.json`.
3. **User:** resume contrastive capture toward ≥30 windows — batch 1
   (`scratchpad/annotation_batch1.md`) + NEW desert-targeted batch 2
   (`scratchpad/annotation_batch2_deserts.md`, from the negative-audit).

*(Cascade-probe signed 2026-07-21; P3 cascade data model stays gated behind a separate GO.)*

Facit corpus: **484** base fibs (1M=13, 1w=24, 1d=76, 4h=371), locked in
[`data/labels/human_fib/MANIFEST.json`](data/labels/human_fib/MANIFEST.json)
(`corpus_manifest --verify`) — counts will change when the 7 misclick fibs are fixed.
