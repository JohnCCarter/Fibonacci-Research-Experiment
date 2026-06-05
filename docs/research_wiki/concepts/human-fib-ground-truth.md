# Human Fib Ground Truth

Human fib means the human draws the anchors. The machine may calculate levels,
classify candle geometry, and propose candidates, but it does not choose the fib
range.

## Data Shape

A human-fib annotation stores:

- `fib_id`
- market context: symbol, timeframe, exchange
- `anchor_a` and `anchor_b`
- direction
- derived levels

Files live under:

```text
data/labels/human_fib/{exchange}/{symbol}/{timeframe}/{fib_id}.json
```

Candidate events live beside them as:

```text
{fib_id}_events.json
```

## Bridge To Event Detection

The human-fib event layer builds a `Swing` from the human annotation:

```text
swing.start = anchor_a
swing.end = anchor_b
```

That makes `fib_levels(swing)` reproduce the saved human levels. The detector
then scans bars after the drawn leg and emits `*_candidate` events.

## Source Links

- [Human fib annotation](../../HUMAN_FIB_ANNOTATION.md)
- [Level event human review](../../LEVEL_EVENT_HUMAN_REVIEW.md)
- [human_fib.py](../../../src/fibengine/labeling/human_fib.py)
- [human_fib_events.py](../../../src/fibengine/labeling/human_fib_events.py)
