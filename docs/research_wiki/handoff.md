# Current Handoff

This page is the current working context for future agents. It is editable; the
append-only trail lives in [log.md](log.md).

## Current Focus

**BTC monthly-first top-down protocol** — reset all prior generated research
results; start fresh on BTC/USD only.

**Canonical protocol:** [BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md](../../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)

| Step | Timeframe | Status |
|------|-----------|--------|
| 1 | **1M** | **Start here** — human fib facit for monthly range |
| 2 | 1W | Map monthly levels to weekly (after 1M approved) |
| 3 | 1D | Daily behavior vs locked human levels |
| 4 | 4H | Finer resolution (after 1D stable) |
| 5 | 1H | Deferred |

**ETH/USD:** blocked until BTC protocol approved.

## Recent Changes

- **2026-06-08 reset** — experiments + `data/` (labels, human_fib, raw, screenshots)
  archived to `archive/research_superseded/2026-06-08_pre_btc_monthly_reset/`.
  Code/tests/tooling unchanged.
- **2026-06-08 agent shell** — constitution + `.cursor` alignment on
  `feature/research-fib` (see log).

## Verification Snapshot

- `experiments/runs/`, `experiments/results/`, `experiments/review/` — **empty**
  (README stubs only); fresh ledgers start on next runner use.
- `data/labels/`, `data/raw/`, `data/screenshots/` — **empty** (prior facit in archive).
- Pre-reset archive manifest:
  [MANIFEST.md](../../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/MANIFEST.md)

## Open Questions

- Minimum monthly fib count before 1W mapping?

## Next Useful Action

1. Fetch BTC 1M/1w/1d candles if cache stale.
2. Label or validate **BTC/USD 1M** human fib in `labeling.tool`.
3. First BTC-only review pack after new human-fib events exist.

## Guardrails

- Do not treat archived ledgers/reviews as current evidence.
- Do not treat `*_candidate` as facit.
- No ETH/SOL analysis until BTC protocol sign-off.
- No auto-fib or trading signals.

## Links

- [BTC-first protocol](../../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)
- [Research wiki index](index.md)
- [Human fib annotation](../labeling/HUMAN_FIB_ANNOTATION.md)
- [Archive manifest](../../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/MANIFEST.md)
