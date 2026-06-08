# 2026-06-05 ETH 1d Human-Fib Review Smoke

Smoke review for GitHub issue #15 (fib-aware visualization) and gate for #16
(tooling spike reassessment).

## Command

```bash
uv run python -m fibengine.research.human_review_level_events \
  --human-fib-events data/labels/human_fib/bitfinex/ETH-USD/1d/fib_ETH-USD_1d_20170618T000000_events.json \
  --max-events 10 --seed 7
```

## Output (local, gitignored)

- `run_id`: `human_fib_review_20260605T064610Z`
- `run_dir`: `experiments/review/fib_level_events/human_fib_review_20260605T064610Z/`
- 35 candidates available, 10 sampled (balanced across candidate types and levels
  0.236 / 0.382 / 0.5)

## Acceptance check (#15)

Manual inspection of PNG charts (e.g. `..._b576_rej.png`):

| Criterion | Pass |
|-----------|------|
| H/L anchor labels with timeframe + price | Yes — purple `H anchor 1d @ …` visible |
| All fib levels drawn and labeled (ratio + price + fib_id) | Yes — dashed blue lines, e.g. `0.236 @ 346.464 - fib_ETH-USD_1d_20170618T000000` |
| Raw relation shown (`touch` / `cross` / `above` / `below`) | Yes — legend and title use relation |
| Behavior candidate separate from relation | Yes — `above -> rejection_candidate` style labels |
| `fib_id` in title and row metadata | Yes |

## Tooling note (#16)

Matplotlib PNG workflow is **good enough** for bounded human review on this pack.
Pan/zoom for heavy desktop review remains in `level_event_review_tool` (not
re-tested in this smoke). Static HTML prototype deferred until a reviewer reports
Matplotlib as the main blocker.

## Next

1. Human fills `review_sample.csv` for the 10 sampled events.
2. Optional: interactive pass via `level_event_review_tool --run-dir <run_dir>`.
3. Close #15 with this smoke reference; close #16 with spike doc + this note.

## Links

- [Fib-aware review decision](../decisions/2026-06-04-fib-aware-review.md)
- [Fib-aware tooling spike](../../FIB_AWARE_TOOLING_SPIKE.md)
- [Level event human review](../../LEVEL_EVENT_HUMAN_REVIEW.md)
