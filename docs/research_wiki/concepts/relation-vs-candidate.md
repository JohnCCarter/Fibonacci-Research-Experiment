# Relation vs Candidate

This distinction is one of the main safety rails in the repo.

## Raw Relation

A relation is deterministic candle geometry against one fib level:

- `above` — the whole candle is above the level.
- `below` — the whole candle is below the level.
- `cross` — open and close are on strictly opposite sides.
- `touch` — the level is inside the candle range without a strict cross.

Relations are atoms. They do not say whether the behavior was useful,
predictive, or correct.

## Behavior Candidate

A candidate is a machine hypothesis about the path around a level:

- `rejection_candidate`
- `continuation_candidate`
- `failure_candidate`
- `reaction_candidate`

Candidates are never facit. They are proposed labels for bounded human review.

## Review Label Pattern

Correct chart language:

```text
0.618 touch -> rejection_candidate
```

This keeps the raw relation (`touch`) separate from the hypothesis
(`rejection_candidate`).

## Source Links

- [Human fib annotation](../../HUMAN_FIB_ANNOTATION.md)
- [Level events](../../LEVEL_EVENTS.md)
- [Level event human review](../../LEVEL_EVENT_HUMAN_REVIEW.md)
