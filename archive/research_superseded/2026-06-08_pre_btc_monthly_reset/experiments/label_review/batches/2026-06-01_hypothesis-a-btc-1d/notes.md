# Hypothesis A — BTC 1d spot-check (2026-06-01)

**Run:** `review_20260601T152524Z` (local: `experiments/review/…`, gitignored charts)

## Sample design

- 40 events, seed 7, balanced: 10 per `auto_candidate`, 8 per fib level (0.236–0.786)
- Walk-forward on Bitfinex BTC/USD 1d (motor swings, not manual `1d.json` legs)

## Findings (fill after review)

| human_label | count |
|-------------|------:|
| agree | |
| wrong_type | |
| missed_context | |
| noise | |
| unclear | |

**Agree rate (labeled only):** ___

### By candidate type

- continuation_candidate:
- rejection_candidate:
- reaction_candidate:
- failure_candidate:

### Rule / detector tweaks needed?

- 

## Commands

```powershell
uv run python scripts/summarize_human_review.py experiments/review/fib_level_events/review_20260601T152524Z
```
