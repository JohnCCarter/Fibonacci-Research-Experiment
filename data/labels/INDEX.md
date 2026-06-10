# Label index

Oversikt over golden set (`data/labels/`).

**Status (2026-06-10):** BTC monthly-first protocol — active human fib facit below.
Counts reflect base `fib_*.json` on disk. Prior mixed-symbol facit **and** the
pre-reset 1w/1d/4h labels are archived under
`archive/research_superseded/2026-06-08_pre_btc_monthly_reset/data/` and
`archive/research_superseded/2026-06-09_pre_log_fib_profile_reset/` — **not** current.

## Active human fib (BTC/USD)

| symbol | timeframe | count | notes |
|--------|-----------|------:|-------|
| BTC/USD | 1M | 9 | monthly anchors (facit, log scale) — review in progress |
| BTC/USD | 1w | 0 | pending re-draw (blocked on 1M sign-off) |
| BTC/USD | 1d | 0 | pending re-draw |
| BTC/USD | 4h | 0 | pending re-draw |

1w/1d/4h directories are absent on disk; prior counts (pre-reset) are archived,
not current evidence. See [handoff.md](../../docs/research_wiki/handoff.md).

Base files: `human_fib/bitfinex/BTC-USD/{timeframe}/fib_*.json`  
Regenerable sidecars (not versioned): `*_events.json`, `*_interactions.csv`

Swing golden set (`bitfinex/BTC-USD/{timeframe}.json`): none yet.

Legacy: `archive/data_labels_Bitfinex/labels/` · superseded reset archive above.

Human-fib schema: [HUMAN_FIB_ANNOTATION.md](../../docs/labeling/HUMAN_FIB_ANNOTATION.md)
