# Fibonacci Level Interaction Events (research-only)

Status: **RESEARCH** — implements issue #8.

Where a swing previously carried a single behavior label per Fibonacci level, this
overlay records **an event stream per level**: every time price interacts with a level
it emits a *candidate* event with a timestamp and supporting evidence, for human review.

## What it does

For a selected swing, `detect_level_events()` scans the bars **after the leg's end**
(the retracement window) and, for each Fibonacci level, emits events classified as:

| candidate                | meaning                                                  |
|--------------------------|----------------------------------------------------------|
| `continuation_candidate` | broke through the level and continued                    |
| `rejection_candidate`    | touched the level and rejected back to the approach side |
| `failure_candidate`      | accepted beyond the level, then reversed back across it  |
| `reaction_candidate`     | reacted at the level without a clear breakout/rejection  |

Each event records `touch_type` (`wick_below` / `wick_above` / `close_above` /
`close_below`), `approach_side` (`above` / `below`), and `evidence`
(`forward_bars`, `closes_beyond`, `closes_back`, `max_penetration_atr`).

## Guardrails

- **Candidates, never facts.** The `*_candidate` naming is deliberate — events are inputs
  to human review, never auto-accepted.
- **Look-ahead is intentional.** Classification inspects a forward window of bars after a
  touch, so this is strictly **post-hoc annotation, never a live trading signal**.
- **Additive only.** It does not change swing selection, fib anchors/prices, evaluation,
  recall or promotion. Output goes to a new file; no existing artifacts are mutated.

## Configuration (`config/settings.yaml` → `level_events`)

| key                        | default | meaning                                                       |
|----------------------------|---------|---------------------------------------------------------------|
| `levels`                   | `[]`    | fib ratios to scan; empty inherits `fib.levels`               |
| `touch_tolerance_atr`      | `0.10`  | band half-width around a level = this × ATR at the bar         |
| `forward_window`           | `5`     | bars after a touch used for classification                    |
| `acceptance_closes`        | `2`     | closes beyond the level required to count as "accepted"       |
| `immediate_rejection_bars` | `2`     | window for a quick close back to the approach side            |
| `debounce_bars`            | `3`     | bars price must leave the band before a new event is counted  |

## Run

```sh
uv run python -m fibengine.research.level_events
```

Appends one JSONL record per run to `experiments/results/level_events.jsonl`
(`run_id`, config/symbol metadata, the selected `swing`, the per-level `levels` streams,
and `n_events`).

## Running offline (no network)

A small cached dataset is committed so the pipeline can run without an exchange:
`data/raw/kraken/BTC-USD/1d/limit_1000.csv` (Kraken BTC/USD daily). Point the config at
it and `load_candles()` reads the cache instead of fetching:

```python
from fibengine.core.config import load_settings
from fibengine.research.level_events import run_level_events

s = load_settings()
s = s.model_copy(update={"data": s.data.model_copy(update={
    "exchange": "kraken", "symbol": "BTC/USD", "timeframe": "1d"})})
run_level_events(s)
```

Note: the repo default exchange is Binance, which is geo-restricted from some hosted
sandboxes (HTTP 451); Kraken/Coinbase/Bitstamp/Bitfinex are reachable alternatives there.
On a normal machine the Binance default works as usual.
