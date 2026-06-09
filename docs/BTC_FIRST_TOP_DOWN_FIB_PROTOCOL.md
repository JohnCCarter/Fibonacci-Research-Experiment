# BTC-first top-down Fib protocol

**Status:** Active research protocol (2026-06-08+). Supersedes mixed-symbol,
1D-first, and MTF-projection result reads archived under
`archive/research_superseded/2026-06-08_pre_btc_monthly_reset/`.

## Principles

1. **BTC/USD only** until monthly→weekly→daily mapping is approved.
2. **Human fib = facit** — manual anchors/levels; `*_candidate` ≠ facit.
3. **Top-down timeframe order:** `1M → 1W → 1D → 4H → 1H` (1H deferred until
   lower layers are stable).
4. **Machine work** measures interactions against **locked human levels** — no
   auto-fib as truth, no anchor moves, no optimization against facit.
5. **ETH/USD** starts only after BTC protocol sign-off.

## Layer map

| Layer | Timeframe | Human | Machine |
|-------|-----------|-------|---------|
| VAD (range) | 1M | Draw/save monthly swing fib | — |
| Context | 1W | Map monthly levels onto weekly structure | — |
| HUR (behavior) | 1D | Validate weekly levels on daily candles | Level interactions vs human prices |
| Resolution | 4H | Optional finer read (later) | MTF projection runner (when invoked) |
| Fine | 1H | Deferred | Deferred |

## Workflow

1. **Fetch** — `uv run python -m fibengine.data.fetch --symbols BTC/USD --timeframes 1M,1w,1d --refresh`
2. **Label facit** — `uv run python -m fibengine.labeling.tool --symbol BTC/USD --timeframe 1M` (then 1w, 1d)
3. **Human fib events** — `uv run python -m fibengine.labeling.human_fib_events --fib <fib_id>.json`
4. **Review** — `human_review_level_events` / `level_event_review_tool` on BTC packs only
5. **Analysis runners** (when scoped) — fingerprint, outcome, join, toplist, MTF projection — **BTC inputs only**

## Output layout (active)

```
experiments/
  runs/          # per-run audit dirs (new protocol only)
  results/       # append-only jsonl ledgers (fresh after reset)
  review/        # human review packs (BTC only)
data/labels/human_fib/bitfinex/BTC-USD/...
```

## `data/` policy (fresh start)

Prior labels, human fib, candle cache, and screenshots were **archived** with
`experiments/` under `archive/research_superseded/2026-06-08_pre_btc_monthly_reset/data/`.
Active paths are empty — rebuild BTC-only.

| Area | BTC protocol | ETH/SOL |
|------|--------------|---------|
| `data/labels/human_fib/` | **New** facit from 1M | Blocked until BTC approved |
| `data/labels/bitfinex/*.json` | New swing labels as needed | Blocked |
| `data/raw/` | Fetch BTC 1M/1w/1d | Do not fetch yet |
| `data/screenshots/` | Optional new references | — |

Detail: [DATA_CLASSIFICATION.md](../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/DATA_CLASSIFICATION.md)

## Out of scope (until BTC approved)

- ETH/SOL mixed toplists or bucket comparisons
- Cross-era cohorts (anchor_b before `history_start`)
- Promoting descriptive bucket reads to signals or facit
- Reusing pre-reset ledgers in `archive/research_superseded/` as current evidence

## Tooling (unchanged)

Runners and review code remain in `src/fibengine/research/` and
`src/fibengine/labeling/`. See [research/README.md](research/README.md) and
[LEVEL_EVENT_HUMAN_REVIEW.md](research/LEVEL_EVENT_HUMAN_REVIEW.md).

## Wiki

Current focus: [research_wiki/handoff.md](research_wiki/handoff.md)
