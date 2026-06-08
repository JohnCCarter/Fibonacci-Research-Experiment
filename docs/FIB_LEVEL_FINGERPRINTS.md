# Fib Level Interaction Fingerprints (#23)

Research-only deterministic features describing how price approached, contacted,
and behaved after each human-fib level event. Complements
[FIB_CANDIDATE_OUTCOMES.md](FIB_CANDIDATE_OUTCOMES.md) (candidate → outcome).

**Not** trading logic. **Not** edge claims. **Not** ML.

## Layering

| Layer | Role |
|-------|------|
| Human fib | Locked map (H/L, levels, direction) |
| `relation` | Geometry at level (`touch`, `cross`, …) |
| `auto_candidate` | Current machine hypothesis |
| **Fingerprint** | Measurable pre/at/post behavior |
| Outcome (#22) | Forward empirical result |

## CLI

```bash
uv run python -m fibengine.research.fib_level_fingerprints \
  --events data/labels/human_fib/bitfinex/BTC-USD/1d/fib_BTC-USD_1d_20260526T000000_events.json \
  --pre-bars 20 --post-bars 50

uv run python -m fibengine.research.fib_level_fingerprints --all-human-fib-events
```

`--all-human-fib-events` skips files whose anchors/events predate the loaded
candle cache (logged in `skipped_events.jsonl` as `anchors_outside_candle_cache`).
To include old fibs, refresh history first:
`python -m fibengine.data.fetch --symbols BTC/USD --timeframes 1d --refresh`

## Feature groups

**Pre-level (`pre_*`):** approach side/direction, bars approaching, distance
traveled, slope, choppiness, ATR-normalized distance, body expansion, impulse-like flag.

**At-level (`at_*`):** relation, touch type, wick/body touch, open/close side,
body vs recent mean, wick through level, close distance (ATR-norm), intrabar cross
without close acceptance.

**Post-level (`post_*`):** bars on break/approach side, first return to level,
max extension away, max adverse through level, retest count, range ATR-norm,
remained-near-level rate, close vs event.

## Output

```
experiments/runs/fib_level_fingerprints/<YYYY-MM-DD>/<run_id>/
    fingerprints.jsonl
    skipped_events.jsonl
    summary.json / summary.csv
    config.json, run_summary.json

experiments/results/fib_level_fingerprints.jsonl
```

## MTF note

Each row uses the event file's timeframe (`1d`, `4h`, …). Run per TF or
`--all-human-fib-events` to compare fingerprints across timeframes for the same
human fib map. No aggregation layer yet (#23 scope).

## Related

- [LEVEL_EVENTS.md](LEVEL_EVENTS.md)
- [FIB_CANDIDATE_OUTCOMES.md](FIB_CANDIDATE_OUTCOMES.md)
- [Relation vs candidate](research_wiki/concepts/relation-vs-candidate.md)
