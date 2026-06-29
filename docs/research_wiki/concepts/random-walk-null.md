# Random-walk null (the control that closed B-1)

**Query this before re-deriving why a level-reaction claim needs a random-walk control.**

## The idea

Support/resistance levels and chart formations emerge **spontaneously in pure random walks** — no
fundamentals, news, or order flow required. So a level repelling price is **only** evidence of a
mechanism if it beats a matched random-walk series. A shuffle-price placebo is not enough; the RW
null sets the correct null prior. Anchor: **Lo, Mamaysky & Wang (2000)**, *Journal of Finance*
55(4) (see [methodology-anchors.md](../sources/methodology-anchors.md)).

This is **NU-1** of the standing
[addendum](../reviews/horizontal-structure-prereg-addendum-20260617.md): any horizontal-structure
study must pre-register a deterministic, seeded, **causal** RW control run through the **same**
event/outcome machinery as the subjects.

## Where the repo implements it

[`src/fibengine/research/synthetic_baseline.py`](../../../src/fibengine/research/synthetic_baseline.py)
— `random_walk_swing_levels()` simulates a seeded GBM/block-bootstrap path calibrated **only** on
history before a level's `known_after_ts` (strictly causal, decoupled, deterministic via a passed
`rng`). The B-1 harness pairs one RW path per subject level (most-recent swing, matched
`known_after_ts`); see [B-1 prereg §4 amendment](../reviews/btc-horizontal-structure-event-study-prereg-20260617.md).

## What it found

B-1 result: generic structure (swing / 1-2-5 round / prior-extreme) does **not** beat the RW null
(`any_robust=False`). Reject rates ~0.76–0.84 across **all** sources incl. the RW null = generic
mean-reversion / spontaneous RW structure, not a mechanism. See
[closed-questions.md](../reference/closed-questions.md).

## Sources

[Source authority](../reference/source-authority.md): code + results docs win over this page.
