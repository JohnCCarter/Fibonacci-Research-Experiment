# Fib Level Candidate — Forward Outcome Analysis (#22)

Research-only check: do machine-generated ``*_candidate`` labels from human-fib
event JSON correlate with measurable forward price behavior?

**Not** a trading strategy. **Not** an edge claim.

## Semantics (keep layers separate)

| Layer | Role |
|-------|------|
| Human fib | Locked source-of-truth (H/L, levels, direction) |
| `relation` | Deterministic geometry (`touch`, `cross`, …) |
| `auto_candidate` | Machine hypothesis (`*_candidate`) |
| Outcome metrics | Empirical forward behavior over N bars |

## CLI

```bash
# Single human-fib events file
uv run python -m fibengine.research.fib_candidate_outcomes \
  --events data/labels/human_fib/bitfinex/BTC-USD/1d/fib_BTC-USD_1d_20260526T000000_events.json \
  --horizons 5,10,20,50

# All saved human-fib event files
uv run python -m fibengine.research.fib_candidate_outcomes --all-human-fib-events
```

Requires cached candles under `data/raw/` (same as review workflow).

## Per-event metrics (each horizon)

- `forward_return` — from event close to horizon close
- `mfe` / `mae` — max favorable / adverse excursion (direction from candidate + `approach_side` when inferable)
- `close_on_approach_side` / `close_on_break_side`
- `crossed_back` — any close crossed to the other side of the level during the window
- `stayed_on_break_side` — when event started on break side, still there at horizon
- `distance_from_level` — absolute close distance from fib price at horizon
- `direction_inferred` — `false` for ambiguous candidates (e.g. `reaction_candidate`)

## Output

```
experiments/runs/fib_candidate_outcomes/<YYYY-MM-DD>/<run_id>/
    config.json
    event_outcomes.jsonl    # one row per event × horizon
    skipped_events.jsonl
    summary.json / summary.csv   # grouped by candidate, relation, level, symbol, TF, horizon
    run_summary.json

experiments/results/fib_candidate_outcomes.jsonl   # append-only run index
```

## Related

- [LEVEL_EVENTS.md](LEVEL_EVENTS.md) — candidate taxonomy
- [LEVEL_EVENT_HUMAN_REVIEW.md](LEVEL_EVENT_HUMAN_REVIEW.md) — manual chart review
- [Relation vs candidate](research_wiki/concepts/relation-vs-candidate.md)
