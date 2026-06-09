# Fibonacci Level Event — Human Review

> **Research-only.** These are auto-detected *candidates*, **not facts** and 
> **not trading signals**. The detector inspects a forward window after each 
> touch, so every label is **post-hoc annotation**, never a live signal. Your 
> job is only to judge whether each auto label matches the chart.

## How to review (mobile-friendly)

For each event below, look at the chart, then fill in three columns in 
`review_sample.csv` (or `review_sample.jsonl`) for the matching `review_id`:

- **human_label** — one of: `agree`, `wrong_type`, `missed_context`, `noise`, `unclear`
- **human_confidence** — one of: `high`, `medium`, `low`
- **human_note** — free text (optional)

### What each human_label means

- `agree` — The auto_candidate type matches what the chart shows.
- `wrong_type` — There is an event here, but it is a different candidate type.
- `missed_context` — Technically a touch, but context (trend/structure) makes it misleading.
- `noise` — Not a meaningful interaction with the level — noise.
- `unclear` — Cannot tell from the chart / ambiguous.

### How to read the chart

- **Blue dashed lines** = calculated fib levels from the same saved fib context.
- **Orange marker / vertical line** = the event bar being judged.
- **Purple H/L anchor labels** = the high/low anchors, with timeframe and price.
- Event labels keep raw relation and candidate separate: `relation -> candidate`.

## Summary

- Total candidates available: **1**
- Total sampled: **1**
- Sampled by candidate type: `{'rejection_candidate': 1}`
- Sampled by fib level: `{'0.236': 1}`
- Output dir: `C:\Users\fa06662\Projects\Fibonacci-Research-Experiment-main\experiments\review\fib_level_events\human_fib_review_20260605T110848Z`

## Events

### `BTC-USD_1d_L0p236_s1303_e1306_b1307_rej`

![BTC-USD_1d_L0p236_s1303_e1306_b1307_rej](charts/BTC-USD_1d_L0p236_s1303_e1306_b1307_rej.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 73818.512 | fib_id: `fib_BTC-USD_1d_20260526T000000`
- relation: **cross** | auto_candidate: **rejection_candidate** | touch_type: wick_below | approach_side: below
- event_time: 2026-05-30T00:00:00+00:00 (bar 1307)
- evidence: forward_bars=3, closes_beyond=0, closes_back=2, max_penetration_atr=0.0533
- anchors: H/L shown on chart | direction down | anchor_a 2026-05-26T00:00:00+00:00 -> anchor_b 2026-05-29T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____
