# Label index

Översikt över golden set (`data/labels/`). Counts reflect **base** `fib_*.json` on disk
(excluding regenerable `*_events.json` / `*_interactions.csv` sidecars).

**Status (2026-06-15):** BTC monthly-first protocol — active human fib facit below.
Authority for phase status is [handoff.md](../../docs/research_wiki/handoff.md); this file
indexes on-disk label counts. Prior mixed-symbol facit **and** the pre-reset 1w/1d/4h
labels are archived under
`archive/research_superseded/2026-06-08_pre_btc_monthly_reset/data/` and
`archive/research_superseded/2026-06-09_pre_log_fib_profile_reset/` — **not** current.

## Active human fib (BTC/USD)

| symbol | timeframe | count | up/down | notes |
|--------|-----------|------:|---------|-------|
| BTC/USD | 1M | 9 | 5 / 4 | monthly anchors (log scale); 1D+4H reaction review approved |
| BTC/USD | 1w | 21 | 13 / 8 | source-facit complete |
| BTC/USD | 1d | 67 | 33 / 34 | source-facit complete |
| BTC/USD | 4h | 365 | 168 / 197 | source-facit complete; 366 drawn, 1 superseded (20250506 dedup) |

All BTC/USD ladders use log scale + `tradingview_log_chamoun` (no 0.236), human/manual
origin. The 4H `20250506` dedup (08:00 fib superseded in favour of 12:00 fib) is recorded
in [reviews/btc-4h-fib-20250506-dedup-20260615.md](../../docs/research_wiki/reviews/btc-4h-fib-20250506-dedup-20260615.md)
and the [source-quality ledger](../../docs/research_wiki/reviews/ledgers/btc-4h-source-quality-ledger.csv).

Base files: `human_fib/bitfinex/BTC-USD/{timeframe}/fib_*.json`
Regenerable sidecars (not versioned): `*_events.json`, `*_interactions.csv`

Swing golden set (`bitfinex/BTC-USD/{timeframe}.json`): none yet.

Legacy: `archive/data_labels_Bitfinex/labels/` · superseded reset archive above.

Human-fib schema: [HUMAN_FIB_ANNOTATION.md](../../docs/labeling/HUMAN_FIB_ANNOTATION.md)
