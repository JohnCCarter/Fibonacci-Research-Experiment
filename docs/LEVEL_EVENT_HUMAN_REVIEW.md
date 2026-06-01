# Fibonacci Level Event — Human Review (v1)

Research-only workflow that turns the auto-detected Fibonacci *level event
candidates* (see [LEVEL_EVENTS.md](LEVEL_EVENTS.md)) into a small, mobile-friendly
package a human can review — including from an iPhone.

## Purpose

The level-event detector emits *candidates*, never facts. Before any of that
work could ever inform anything downstream, a human needs to confirm: **does the
auto-detected event actually match what the chart shows?** This workflow makes
that confirmation cheap. It samples a bounded set of candidates, renders one
chart per event, and writes a review sheet with blank columns the reviewer fills
in. No TradingView, no manual chart hunting.

## Interactive review (recommended on desktop)

Same candlestick chart feel as the labeling tool — pan/zoom, hover OHLC:

```bash
uv run python -m fibengine.research.level_event_review_tool \
  --run-dir experiments/review/fib_level_events/review_20260601T152524Z
```

| Key | Action |
|-----|--------|
| `1`–`5` | `agree`, `wrong_type`, `missed_context`, `noise`, `unclear` |
| `h` / `m` / `l` | confidence high / medium / low |
| `n` or `→` | next event |
| `p` or `←` | previous event |
| `s` | save `review_sample.csv` + `.jsonl` |
| `z` | zoom back to current event |
| `q` | save and quit |

Use the matplotlib toolbar to pan/zoom like `fibengine.labeling.tool`.

## Mobile-friendly workflow (PNG + CSV)

Each run produces a self-contained folder of PNG charts plus a markdown index
and a review sheet (CSV + JSONL). The reviewer:

1. Opens `REVIEW_INDEX.md` on their phone — it embeds every chart inline.
2. For each event, looks at the chart and decides whether the auto label is right.
3. Fills in three columns for that `review_id` in `review_sample.csv` (or the
   JSONL): `human_label`, `human_confidence`, `human_note`.

Charts are intentionally simple (close-line by default, ~7×5in, dpi 130) so they
load fast and read well on a small screen.

## CLI usage

```bash
# BTC 1d spot-check (Hypothesis A default sample):
uv run python -m fibengine.research.human_review_level_events \
  --symbol BTC/USD --timeframe 1d --max-events 40 --seed 7 --line

# Default config TF (often 1h): balanced sample across candidate types & levels.
uv run python -m fibengine.research.human_review_level_events --max-events 40 --seed 7

# Single currently-selected swing instead of all walk-forward legs:
uv run python -m fibengine.research.human_review_level_events --mode single

# Non-overlapping attribution (each bar counted under one leg):
uv run python -m fibengine.research.human_review_level_events --dedupe

# Caps & filters:
uv run python -m fibengine.research.human_review_level_events \
  --max-per-candidate 10 --max-per-level 8 \
  --candidate-type continuation_candidate --candidate-type rejection_candidate \
  --level 0.5 --level 0.618 --seed 7

# Candlesticks instead of close-line:
uv run python -m fibengine.research.human_review_level_events --candlestick
```

Flags:

| Flag | Meaning | Default |
|------|---------|---------|
| `--mode` | `single` (one selected swing) or `walk-forward` (all confirmed legs) | `walk-forward` |
| `--dedupe` | Walk-forward non-overlapping attribution | off |
| `--max-events` | Max sampled events total | `40` |
| `--max-per-candidate` | Cap per candidate type | none |
| `--max-per-level` | Cap per fib level | none |
| `--candidate-type` | Filter to a candidate type (repeatable) | all |
| `--level` | Filter to a fib level e.g. `0.5` (repeatable) | all |
| `--seed` | Random seed → reproducible sample | none |
| `--candlestick` | Candlesticks instead of close-line | off |
| `--context-before` / `--context-after` | Bars shown around the event | `30` / `15` |

## Artifact structure

```
experiments/review/fib_level_events/<run_id>/
    review_sample.csv      # one row per sampled candidate (+ blank human_* cols)
    review_sample.jsonl    # same rows, one JSON object per line
    REVIEW_INDEX.md        # instructions + summary + one chart block per event
    charts/<review_id>.png # one chart per sampled event
```

`<run_id>` is `review_<UTC timestamp>`. The whole `experiments/review/` tree is
git-ignored: these are generated artifacts, not committed repo data.

Each review row contains: `review_id, symbol, timeframe, exchange, fib_level,
fib_price, event_bar, event_time, auto_candidate, touch_type, approach_side,
note, evidence_forward_bars, evidence_closes_beyond, evidence_closes_back,
evidence_max_penetration_atr, swing_start_time, swing_end_time, swing_direction,
swing_start_bar, swing_end_bar, chart_path, human_label, human_confidence,
human_note`.

## Label schema

`human_label` — pick exactly one:

- `agree` — the `auto_candidate` type matches what the chart shows.
- `wrong_type` — there is an event here, but it is a different candidate type.
- `missed_context` — technically a touch, but trend/structure makes it misleading.
- `noise` — not a meaningful interaction with the level.
- `unclear` — cannot tell from the chart / ambiguous.

`human_confidence` — pick exactly one: `high`, `medium`, `low`.

`human_note` — free text (optional).

## How to read a chart

- **Dashed blue line** — the fib level price.
- **Orange marker / vertical line** — the event bar (the touch being judged).
- **Purple ▲ / ▼** — swing start / end (the leg the fib is drawn from), when in view.
- **Title** — symbol, timeframe, fib level, `auto_candidate`, event time.

## What this validates

- Whether the detector's per-event classification matches a human's read of the
  chart, broken down by candidate type and fib level.
- A labeled dataset of human agreement for later qualitative analysis.

## What this does NOT validate

- Any trading edge, profitability, or signal quality — there is none here.
- Anything live: the detector looks at a forward window, so labels are strictly
  **post-hoc annotation**, never a real-time signal.
- It does not promote, accept, or feed any candidate back into swing selection,
  fib prices, evaluation, recall, or the canonical config. Purely research.
