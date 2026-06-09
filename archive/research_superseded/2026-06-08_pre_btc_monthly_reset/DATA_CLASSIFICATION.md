# `data/` classification — BTC monthly-first reset

**Moved** 2026-06-08 per explicit fresh-start decision. Active `data/` paths are
empty; rebuild under BTC-first protocol.

## Archived here (`data/`)

| Path | Files | Notes |
|------|------:|-------|
| `data/labels/bitfinex/BTC-USD/` | 2 | Swing facit 1d+1w |
| `data/labels/bitfinex/ETH-USD/` | 2 | Swing facit 1d+1w |
| `data/labels/bitfinex/SOL-USD/` | 2 | Swing facit 1d+1w |
| `data/labels/human_fib/bitfinex/BTC-USD/` | 95 | 1d: 83, 1w: 12 |
| `data/labels/human_fib/bitfinex/ETH-USD/` | 95 | |
| `data/labels/human_fib/bitfinex/SOL-USD/` | 57 | |
| `data/raw/bitfinex/` | 22 | BTC/ETH/SOL multi-TF CSV |
| `data/screenshots/` | 4 | Manual BTC-USDT PNGs + README |

## Active `data/` (after reset)

| Path | Status |
|------|--------|
| `data/labels/bitfinex/{BTC,ETH,SOL}-USD/` | Empty dirs — new swing facit via `labeling.tool` |
| `data/labels/human_fib/bitfinex/{BTC,ETH,SOL}-USD/` | Empty dirs — start **BTC/USD 1M** |
| `data/raw/` | Empty — refetch BTC only |
| `data/screenshots/` | Empty — optional new references |

## Rules

- Restore from this archive only for inspection; do not merge back without
  explicit protocol decision.
- New human fib = facit; `*_candidate` ≠ facit.
- ETH/SOL labeling blocked until BTC protocol approved.
