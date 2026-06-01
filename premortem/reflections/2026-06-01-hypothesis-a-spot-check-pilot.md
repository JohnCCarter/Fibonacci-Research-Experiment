# Hypothesis A — first bounded spot-check pilot (2026-06-01)

## What we did

- Generated review package `review_20260601T152524Z` (BTC/USD 1d, walk-forward, 40 events, seed 7).
- Checkpoint batch: `experiments/label_review/batches/2026-06-01_hypothesis-a-btc-1d/`.
- CLI: `--symbol`, `--timeframe`, `--exchange` on `human_review_level_events`.

## Outcome

- **Human labels:** see `review_sample.csv` in review run dir; summarize with `scripts/summarize_human_review.py`.
- **Not evidence yet** until `human_label` is filled on the sample (not bulk `auto_candidate` copy).

## Interpretation (update after labels)

- If agree rate is high on clear types (rej/cont) but low on reaction/failure → tighten rules for ambiguous classes first.
- If many `missed_context` → detector ignores HTF leg / swing context (expected gap vs manual facit legs).

## Next

1. Copy filled `review_sample.csv` into label_review batch when done.
2. Post summary on GitHub #12.
3. Optional second sample on recent bars only (filter by `event_time`).
