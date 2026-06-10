# Label index

Oversikt over golden set (`data/labels/`).

**Status (2026-06-09):** BTC monthly-first protocol — active human fib facit below.
Prior mixed-symbol facit archived under
`archive/research_superseded/2026-06-08_pre_btc_monthly_reset/data/`.

## Active human fib (BTC/USD)

| symbol | timeframe | count | notes |
|--------|-----------|------:|-------|
| BTC/USD | 1M | 6 | monthly anchors (facit) |
| BTC/USD | 1w | 10 | weekly facit |
| BTC/USD | 1d | 60 | daily facit |
| BTC/USD | 4h | 75 | 4h facit (in progress / review) |

Base files: `human_fib/bitfinex/BTC-USD/{timeframe}/fib_*.json`  
Regenerable sidecars (not versioned): `*_events.json`, `*_interactions.csv`

Swing golden set (`bitfinex/BTC-USD/{timeframe}.json`): none yet.

Legacy: `archive/data_labels_Bitfinex/labels/` · superseded reset archive above.

Human-fib schema: [HUMAN_FIB_ANNOTATION.md](../../docs/labeling/HUMAN_FIB_ANNOTATION.md)
