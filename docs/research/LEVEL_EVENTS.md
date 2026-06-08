# Fibonacci Level Interaction Events (research-only)

Status: **RESEARCH** â€” implements issue #8.

Where a swing previously carried a single behavior label per Fibonacci level, this
overlay records **an event stream per level**: every time price interacts with a level
it emits a *candidate* event with a timestamp and supporting evidence, for human review.

> To human-validate these candidates on a phone, see
> [LEVEL_EVENT_HUMAN_REVIEW.md](LEVEL_EVENT_HUMAN_REVIEW.md).

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

- **Candidates, never facts.** The `*_candidate` naming is deliberate â€” events are inputs
  to human review, never auto-accepted.
- **Look-ahead is intentional.** Classification inspects a forward window of bars after a
  touch, so this is strictly **post-hoc annotation, never a live trading signal**.
- **Additive only.** It does not change swing selection, fib anchors/prices, evaluation,
  recall or promotion. Output goes to a new file; no existing artifacts are mutated.

## Configuration (`config/settings.yaml` â†’ `level_events`)

| key                        | default | meaning                                                       |
|----------------------------|---------|---------------------------------------------------------------|
| `levels`                   | `[]`    | fib ratios to scan; empty inherits `fib.levels`               |
| `touch_tolerance_atr`      | `0.10`  | band half-width around a level = this Ã— ATR at the bar         |
| `forward_window`           | `5`     | bars after a touch used for classification                    |
| `acceptance_closes`        | `2`     | closes beyond the level required to count as "accepted"       |
| `immediate_rejection_bars` | `2`     | window for a quick close back to the approach side            |
| `debounce_bars`            | `3`     | bars price must leave the band before a new event is counted  |

## Run

```sh
uv run python -m fibengine.research.level_events                 # single snapshot
uv run python -m fibengine.research.level_events --mode walk-forward
uv run python -m fibengine.research.level_events --mode walk-forward --dedupe
```

**`single`** selects one swing on the full series and detects events after its leg.
Appends a record to `experiments/results/level_events.jsonl` (`run_id`, config/symbol
metadata, the selected `swing`, the per-level event streams, and `n_events`).

Note: a single live "as-of-now" run usually picks a leg ending at the present, leaving no
forward window â€” so it often reports **0 events**. The interactions the issue cares about
require a leg that has had time to "live". That is what walk-forward mode provides.

## Walk-forward mode (answers research Q4)

**`walk-forward`** steps the cursor through history (`backtest.warmup_bars` / `backtest.step`),
selecting swings *causally* (no future leaks into selection), and aggregates level events
across every distinct **confirmed** leg via `walk_forward_level_events()`. It reuses
`backtest.stability.walk_forward_selection()`. Output goes to
`experiments/results/level_events_walkforward.jsonl`:

```json
{
  "n_legs": 224, "n_events": 4835, "events_per_leg": 21.58,
  "per_level": [{"level": "0.382", "events": 964,
                 "by_candidate": {"continuation": 308, "failure": 113,
                                  "reaction": 214, "rejection": 329}}, ...],
  "legs": [{"first_confirmed_t": ..., "start_bar": ..., "end_bar": ...,
            "direction": ..., "n_events": ...}, ...]
}
```

**Caveat â€” overlapping legs inflate absolute totals.** With `step=1` nearly every bar
yields a (slightly drifted) confirmed leg, and in the default (`forward`) attribution each
leg's events are counted over the full forward history, so the same price action is counted
under many overlapping legs. The absolute `n_events` is then sensitive to `step`.

**Use `--dedupe` (non-overlapping attribution) for the trustworthy census.** Each bar is
attributed to exactly one leg â€” the one that was the live confirmed selection at that bar
(window `[confirmation cursor t, next leg's t)`) â€” so no event is double-counted. This
matters: on Kraken BTC/USD daily the `forward` mode shows a misleadingly *flat* per-level
distribution (~19-22% each, 4835 events), while `--dedupe` reveals the real gradient â€”
shallow levels dominate (0.236/0.382 â‰ˆ 28% each) and deep levels are rare
(0.786 â‰ˆ 10%), across 142 distinct interactions. Prefer `--dedupe` when answering
"how many events per level".

## Data / running

Candles are fetched on demand and cached locally by `load_candles()` (under `data/raw/`,
which is **not** versioned â€” see the repo data policy). The first run for a symbol/timeframe
needs network; subsequent runs read the local cache. Point the config at any symbol:

```python
from fibengine.core.config import load_settings
from fibengine.research.level_events import run_walk_forward_level_events

s = load_settings()
s = s.model_copy(update={"data": s.data.model_copy(update={
    "exchange": "kraken", "symbol": "BTC/USD", "timeframe": "1d"})})
run_walk_forward_level_events(s, non_overlapping=True)
```

Config is supplied via `LevelEventConfig` (defaults are used unless you pass your own);
it is intentionally **not** part of canonical `Settings`, so `Settings.config_hash()` and
the Promotion surface stay untouched.

Note: the repo default exchange is Bitfinex, which is geo-restricted from some hosted
sandboxes (HTTP 451); Kraken/Coinbase/Bitstamp/Bitfinex are reachable alternatives there.
On a normal machine the Bitfinex default works as usual. Tests rely only on synthetic data,
so they need no network.

