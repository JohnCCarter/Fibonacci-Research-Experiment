# Research reset manifest — 2026-06-08 (pre BTC monthly-first)

**Reason:** Full fresh start before the **BTC/USD top-down** protocol
(1M → 1W → 1D → 4H → 1H). Code, tests, and tooling docs unchanged; prior
labels, human fib, candle cache, and screenshots moved here.

**Active protocol:** [docs/BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md](../../../docs/BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)

## Moved here (archive/superseded)

| Path | Files | Notes |
|------|------:|-------|
| `experiments/runs/` | 200 | MTF projection (12 runs), fingerprint/outcome runs, experiment 2026-06-02 |
| `experiments/results/` | 22 | All `*.jsonl` + MTF compare JSON snapshots |
| `experiments/review/` | 251 | Level-event + human-fib review packs (BTC/ETH/SOL mixed) |
| `experiments/label_review/batches/` | 4 | `2026-06-01_hypothesis-a-btc-1d` checkpoint |
| `wiki_reviews/` | 5 | Wiki review summaries (n≥20, MTF, fingerprint checkpoints) |
| `data/labels/bitfinex/` | 6 | Swing golden set (BTC/ETH/SOL 1d+1w) |
| `data/labels/human_fib/` | 247 | Human fib + events (BTC/ETH/SOL) |
| `data/raw/` | 22 | Bitfinex OHLCV CSV caches |
| `data/screenshots/` | 4 | Manual TV reference PNGs |

**Total archived files:** ~759 (this tree).

## Classification summary

| Category | Treatment |
|----------|-----------|
| `experiments/runs/*` | **archive/superseded** — old runner outputs |
| `experiments/results/*` | **archive/superseded** — append-only ledgers from prior track |
| `experiments/review/*` | **archive/superseded** — generated PNG/CSV/JSONL packs |
| `wiki_reviews/*` | **archive/superseded** — descriptive reads, no facit promotion |
| `archive/experiments/*` | **already archived** — left in place (May 2026 spot-check era) |
| `src/`, `tests/`, `config/` | **keep active** |
| `docs/research/*`, `docs/labeling/*` | **keep active** — protocol/tooling reference |
| `data/labels/`, `data/raw/`, `data/screenshots/` | **archive/superseded** — prior facit/cache/screenshots under `data/` |

## Superseded research themes (do not treat as current evidence)

- 1D-only fingerprint × outcome bucket reads (mixed symbols)
- MTF fib level projection (1W→1D, 1W→4H, clean-forward vs cross-era cohorts)
- Multi-symbol toplists (BTC/ETH/SOL combined)
- Pre-`history_start` (2022-10-31) cross-era projection noise

## Restore

To inspect a superseded pack, use paths under this folder verbatim. Do not merge
back into `experiments/` without an explicit new protocol decision.
