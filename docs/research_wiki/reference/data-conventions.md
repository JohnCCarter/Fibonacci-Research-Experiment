# Data Conventions

Common data paths and meanings. Source docs remain authoritative.

## Swing Labels

```text
data/labels/{exchange}/{symbol}/{timeframe}.json
```

Used for swing facit and machine/human label workflows. `symbol` uses dash form
such as `BTC-USD`.

## Human Fib

```text
data/labels/human_fib/{exchange}/{symbol}/{timeframe}/{fib_id}.json
data/labels/human_fib/{exchange}/{symbol}/{timeframe}/{fib_id}_events.json
data/labels/human_fib/{exchange}/{symbol}/{timeframe}/{fib_id}_interactions.csv
```

The annotation JSON stores anchors and levels. The events JSON stores
`*_candidate` streams. The interactions CSV stores per-candle raw relations.

## Research Behavior Facit

```text
data/labels/research/
```

This is schema v3 behavior research data. `human_label` is facit; `auto_candidate`
is only a proposal.

## Experiment Outputs

```text
experiments/results/*.jsonl
experiments/runs/{kind}/{date}/{run_id}/
experiments/review/fib_level_events/{run_id}/
```

Review packs contain `review_sample.csv`, `review_sample.jsonl`,
`REVIEW_INDEX.md`, and chart PNGs.

## Source Links

- [Human fib annotation](../../HUMAN_FIB_ANNOTATION.md)
- [Behavior facit](../../BEHAVIOR_FACIT.md)
- [Level event human review](../../LEVEL_EVENT_HUMAN_REVIEW.md)
- [data labels README](../../../data/labels/README.md)
