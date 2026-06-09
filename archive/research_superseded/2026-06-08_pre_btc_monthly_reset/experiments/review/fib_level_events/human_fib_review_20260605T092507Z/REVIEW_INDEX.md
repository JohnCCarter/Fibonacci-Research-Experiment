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

- Total candidates available: **35**
- Total sampled: **2**
- Sampled by candidate type: `{'continuation_candidate': 1, 'rejection_candidate': 1}`
- Sampled by fib level: `{'0.236': 2}`
- Output dir: `C:\Users\fa06662\Projects\Fibonacci-Research-Experiment-main\experiments\review\fib_level_events\human_fib_review_20260605T092507Z`

## Events

### `ETH-USD_1d_L0p236_s225_e225_b301_cont`

![ETH-USD_1d_L0p236_s225_e225_b301_cont](charts/ETH-USD_1d_L0p236_s225_e225_b301_cont.png)

- ETH/USD 1d (bitfinex) | fib **0.236** @ 346.4645 | fib_id: `fib_ETH-USD_1d_20170618T000000`
- relation: **cross** | auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2017-09-02T00:00:00+00:00 (bar 301)
- evidence: forward_bars=5, closes_beyond=4, closes_back=1, max_penetration_atr=2.0773
- anchors: H/L shown on chart | direction down | anchor_a 2017-06-18T00:00:00+00:00 -> anchor_b 2017-06-18T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `ETH-USD_1d_L0p236_s225_e225_b342_rej`

![ETH-USD_1d_L0p236_s225_e225_b342_rej](charts/ETH-USD_1d_L0p236_s225_e225_b342_rej.png)

- ETH/USD 1d (bitfinex) | fib **0.236** @ 346.4645 | fib_id: `fib_ETH-USD_1d_20170618T000000`
- relation: **touch** | auto_candidate: **rejection_candidate** | touch_type: wick_above | approach_side: below
- event_time: 2017-10-13T00:00:00+00:00 (bar 342)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- anchors: H/L shown on chart | direction down | anchor_a 2017-06-18T00:00:00+00:00 -> anchor_b 2017-06-18T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____
