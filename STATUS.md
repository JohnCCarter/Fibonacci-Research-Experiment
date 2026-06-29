# STATUS — fibengine research

At-a-glance snapshot. **Last swept: 2026-06-25.** Full per-line detail + doc pointers:
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
the lever is a richer notion of what makes a leg "yours"**. Current bet: **top-down MTF nesting**
(model the same swing decomposed 1M→1W→1D), which needs **new deliberately-nested labels**.

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

| # | Title | Note |
|---|-------|------|
| **#31** | Investigate fractal-based anchor detection vs human source-fib labels | 🔬 open — now relevant (upstream of the ranking model: does the detector even propose the human's A/B?). |

*(#37 closed 2026-06-25 as a verbatim duplicate of #35 — the principle is in AGENTS.md.)*

## Immediate next action

1. **User:** redraw a small set of **deliberately-nested** fibs on one era (1M→1W→1D) — *tomorrow*.
2. **Prerequisite (code):** extend `RESOLUTION_TIMEFRAME` in
   [`same_candle_mtf_resolution.py`](src/fibengine/labeling/same_candle_mtf_resolution.py) to cover
   1M→1w (monthly anchors currently stay coarse). Continues **#31**.
