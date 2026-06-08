# 2026-06-04 Fib-aware Review

## Decision

Improve the existing review rendering around human-fib context before building a
new production UI.

## Why

Issue #15 showed that generic movement markers were not enough for human fib
review. The chart needs to show:

- H/L anchors.
- all calculated fib levels.
- raw event relation.
- behavior candidate.
- `fib_id` or source context.

Issue #16 asked for a tooling spike, but explicitly did not require replacing
the labeling tool or building a full platform.

## Chosen Path

- Keep human-drawn fib as source of truth.
- Render review charts from existing JSON-first artifacts.
- Keep relation and candidate separate in labels.
- Defer Dash, Panel, React, and TradingView decisions until the review contract
  proves useful.

## Source Links

- [Fib-aware tooling spike](../../FIB_AWARE_TOOLING_SPIKE.md)
- [Level event human review](../../LEVEL_EVENT_HUMAN_REVIEW.md)
- [Relation vs candidate](../concepts/relation-vs-candidate.md)
