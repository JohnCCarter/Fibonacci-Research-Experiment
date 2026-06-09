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

- **Dashed blue line** = the fib level price.
- **Orange marker / vertical line** = the event bar (the touch being judged).
- **Purple ▲ / ▼** = swing start / end (the leg the fib is drawn from), when in view.
- The title shows symbol, timeframe, fib level, auto_candidate and event time.

## Summary

- Total candidates available: **51**
- Total sampled: **51**
- Sampled by candidate type: `{'continuation_candidate': 23, 'failure_candidate': 4, 'reaction_candidate': 11, 'rejection_candidate': 13}`
- Sampled by fib level: `{'0.236': 11, '0.382': 10, '0.5': 9, '0.618': 8, '0.786': 7, '1': 6}`
- Output dir: `experiments\review\fib_level_events\review_human_fib_btc_2026_20260602T134417Z`

## Events

### `fib_BTC-USD_1d_20260407T000000_L0p618_b944_rejection`

![fib_BTC-USD_1d_20260407T000000_L0p618_b944_rejection](charts/fib_BTC-USD_1d_20260407T000000_L0p618_b944_rejection.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 70847.294
- auto_candidate: **rejection_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-04-08T00:00:00+00:00 (bar 944)
- evidence: forward_bars=5, closes_beyond=0, closes_back=4, max_penetration_atr=0.0545
- swing: down | start 2026-04-07T00:00:00+00:00 → end 2026-04-07T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260407T000000_L0p786_b944_failure`

![fib_BTC-USD_1d_20260407T000000_L0p786_b944_failure](charts/fib_BTC-USD_1d_20260407T000000_L0p786_b944_failure.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 71701.238
- auto_candidate: **failure_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-04-08T00:00:00+00:00 (bar 944)
- evidence: forward_bars=5, closes_beyond=2, closes_back=3, max_penetration_atr=0.3859
- swing: down | start 2026-04-07T00:00:00+00:00 → end 2026-04-07T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260407T000000_L1_b944_continuation`

![fib_BTC-USD_1d_20260407T000000_L1_b944_continuation](charts/fib_BTC-USD_1d_20260407T000000_L1_b944_continuation.png)

- BTC/USD 1d (bitfinex) | fib **1** @ 72789.0
- auto_candidate: **continuation_candidate** | touch_type: close_below | approach_side: below
- event_time: 2026-04-08T00:00:00+00:00 (bar 944)
- evidence: forward_bars=5, closes_beyond=2, closes_back=3, max_penetration_atr=0.6164
- swing: down | start 2026-04-07T00:00:00+00:00 → end 2026-04-07T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260407T000000_L0p5_b945_rejection`

![fib_BTC-USD_1d_20260407T000000_L0p5_b945_rejection](charts/fib_BTC-USD_1d_20260407T000000_L0p5_b945_rejection.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 70247.5
- auto_candidate: **rejection_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-04-09T00:00:00+00:00 (bar 945)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- swing: down | start 2026-04-07T00:00:00+00:00 → end 2026-04-07T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260413T000000_L0p236_b954_failure`

![fib_BTC-USD_1d_20260413T000000_L0p236_b954_failure](charts/fib_BTC-USD_1d_20260413T000000_L0p236_b954_failure.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 76486.964
- auto_candidate: **failure_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-04-18T00:00:00+00:00 (bar 954)
- evidence: forward_bars=5, closes_beyond=3, closes_back=2, max_penetration_atr=1.05
- swing: up | start 2026-04-13T00:00:00+00:00 → end 2026-04-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260413T000000_L0p382_b954_rejection`

![fib_BTC-USD_1d_20260413T000000_L0p382_b954_rejection](charts/fib_BTC-USD_1d_20260413T000000_L0p382_b954_rejection.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 75348.018
- auto_candidate: **rejection_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-04-18T00:00:00+00:00 (bar 954)
- evidence: forward_bars=5, closes_beyond=1, closes_back=5, max_penetration_atr=0.6052
- swing: up | start 2026-04-13T00:00:00+00:00 → end 2026-04-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260413T000000_L0p5_b955_failure`

![fib_BTC-USD_1d_20260413T000000_L0p5_b955_failure](charts/fib_BTC-USD_1d_20260413T000000_L0p5_b955_failure.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 74427.5
- auto_candidate: **failure_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-04-19T00:00:00+00:00 (bar 955)
- evidence: forward_bars=5, closes_beyond=1, closes_back=5, max_penetration_atr=0.2463
- swing: up | start 2026-04-13T00:00:00+00:00 → end 2026-04-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260413T000000_L0p618_b955_rejection`

![fib_BTC-USD_1d_20260413T000000_L0p618_b955_rejection](charts/fib_BTC-USD_1d_20260413T000000_L0p618_b955_rejection.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 73506.982
- auto_candidate: **rejection_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-04-19T00:00:00+00:00 (bar 955)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- swing: up | start 2026-04-13T00:00:00+00:00 → end 2026-04-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L0p236_b959_continuation`

![fib_BTC-USD_1d_20260420T000000_L0p236_b959_continuation](charts/fib_BTC-USD_1d_20260420T000000_L0p236_b959_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 78119.46
- auto_candidate: **continuation_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-04-23T00:00:00+00:00 (bar 959)
- evidence: forward_bars=5, closes_beyond=4, closes_back=1, max_penetration_atr=0.6771
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L0p382_b959_reaction`

![fib_BTC-USD_1d_20260420T000000_L0p382_b959_reaction](charts/fib_BTC-USD_1d_20260420T000000_L0p382_b959_reaction.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 77277.77
- auto_candidate: **reaction_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-04-23T00:00:00+00:00 (bar 959)
- evidence: forward_bars=5, closes_beyond=1, closes_back=3, max_penetration_atr=0.3464
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260413T000000_L0p236_b963_reaction`

![fib_BTC-USD_1d_20260413T000000_L0p236_b963_reaction](charts/fib_BTC-USD_1d_20260413T000000_L0p236_b963_reaction.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 76486.964
- auto_candidate: **reaction_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-04-27T00:00:00+00:00 (bar 963)
- evidence: forward_bars=5, closes_beyond=1, closes_back=3, max_penetration_atr=0.301
- swing: up | start 2026-04-13T00:00:00+00:00 → end 2026-04-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L0p5_b963_failure`

![fib_BTC-USD_1d_20260420T000000_L0p5_b963_failure](charts/fib_BTC-USD_1d_20260420T000000_L0p5_b963_failure.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 76597.5
- auto_candidate: **failure_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-04-27T00:00:00+00:00 (bar 963)
- evidence: forward_bars=5, closes_beyond=2, closes_back=3, max_penetration_atr=0.3482
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L0p618_b964_rejection`

![fib_BTC-USD_1d_20260420T000000_L0p618_b964_rejection](charts/fib_BTC-USD_1d_20260420T000000_L0p618_b964_rejection.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 75917.23
- auto_candidate: **rejection_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-04-28T00:00:00+00:00 (bar 964)
- evidence: forward_bars=5, closes_beyond=0, closes_back=5, max_penetration_atr=0.0586
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260413T000000_L0p382_b965_rejection`

![fib_BTC-USD_1d_20260413T000000_L0p382_b965_rejection](charts/fib_BTC-USD_1d_20260413T000000_L0p382_b965_rejection.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 75348.018
- auto_candidate: **rejection_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-04-29T00:00:00+00:00 (bar 965)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- swing: up | start 2026-04-13T00:00:00+00:00 → end 2026-04-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L0p786_b965_rejection`

![fib_BTC-USD_1d_20260420T000000_L0p786_b965_rejection](charts/fib_BTC-USD_1d_20260420T000000_L0p786_b965_rejection.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 74948.71
- auto_candidate: **rejection_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-04-29T00:00:00+00:00 (bar 965)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260429T000000_L0p236_b973_continuation`

![fib_BTC-USD_1d_20260429T000000_L0p236_b973_continuation](charts/fib_BTC-USD_1d_20260429T000000_L0p236_b973_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 80963.04
- auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-05-07T00:00:00+00:00 (bar 973)
- evidence: forward_bars=5, closes_beyond=4, closes_back=2, max_penetration_atr=0.4525
- swing: up | start 2026-04-29T00:00:00+00:00 → end 2026-05-06T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260429T000000_L0p382_b973_rejection`

![fib_BTC-USD_1d_20260429T000000_L0p382_b973_rejection](charts/fib_BTC-USD_1d_20260429T000000_L0p382_b973_rejection.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 79815.48
- auto_candidate: **rejection_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-05-07T00:00:00+00:00 (bar 973)
- evidence: forward_bars=5, closes_beyond=0, closes_back=5, max_penetration_atr=0.0
- swing: up | start 2026-04-29T00:00:00+00:00 → end 2026-05-06T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260429T000000_L0p382_b978_continuation`

![fib_BTC-USD_1d_20260429T000000_L0p382_b978_continuation](charts/fib_BTC-USD_1d_20260429T000000_L0p382_b978_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 79815.48
- auto_candidate: **continuation_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-05-12T00:00:00+00:00 (bar 978)
- evidence: forward_bars=5, closes_beyond=4, closes_back=2, max_penetration_atr=1.1747
- swing: up | start 2026-04-29T00:00:00+00:00 → end 2026-05-06T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260429T000000_L0p5_b979_continuation`

![fib_BTC-USD_1d_20260429T000000_L0p5_b979_continuation](charts/fib_BTC-USD_1d_20260429T000000_L0p5_b979_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 78888.0
- auto_candidate: **continuation_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-05-13T00:00:00+00:00 (bar 979)
- evidence: forward_bars=5, closes_beyond=3, closes_back=2, max_penetration_atr=0.8991
- swing: up | start 2026-04-29T00:00:00+00:00 → end 2026-05-06T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L0p236_b982_continuation`

![fib_BTC-USD_1d_20260420T000000_L0p236_b982_continuation](charts/fib_BTC-USD_1d_20260420T000000_L0p236_b982_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 78119.46
- auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-05-16T00:00:00+00:00 (bar 982)
- evidence: forward_bars=5, closes_beyond=5, closes_back=0, max_penetration_atr=0.5749
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260429T000000_L0p618_b982_continuation`

![fib_BTC-USD_1d_20260429T000000_L0p618_b982_continuation](charts/fib_BTC-USD_1d_20260429T000000_L0p618_b982_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 77960.52
- auto_candidate: **continuation_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-05-16T00:00:00+00:00 (bar 982)
- evidence: forward_bars=5, closes_beyond=5, closes_back=0, max_penetration_atr=0.5016
- swing: up | start 2026-04-29T00:00:00+00:00 → end 2026-05-06T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260413T000000_L0p236_b983_reaction`

![fib_BTC-USD_1d_20260413T000000_L0p236_b983_reaction](charts/fib_BTC-USD_1d_20260413T000000_L0p236_b983_reaction.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 76486.964
- auto_candidate: **reaction_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-05-17T00:00:00+00:00 (bar 983)
- evidence: forward_bars=5, closes_beyond=1, closes_back=5, max_penetration_atr=0.4361
- swing: up | start 2026-04-13T00:00:00+00:00 → end 2026-04-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L0p382_b983_continuation`

![fib_BTC-USD_1d_20260420T000000_L0p382_b983_continuation](charts/fib_BTC-USD_1d_20260420T000000_L0p382_b983_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 77277.77
- auto_candidate: **continuation_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-05-17T00:00:00+00:00 (bar 983)
- evidence: forward_bars=5, closes_beyond=3, closes_back=2, max_penetration_atr=0.8026
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L0p5_b983_reaction`

![fib_BTC-USD_1d_20260420T000000_L0p5_b983_reaction](charts/fib_BTC-USD_1d_20260420T000000_L0p5_b983_reaction.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 76597.5
- auto_candidate: **reaction_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-05-17T00:00:00+00:00 (bar 983)
- evidence: forward_bars=5, closes_beyond=1, closes_back=5, max_penetration_atr=0.4873
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260429T000000_L0p786_b983_reaction`

![fib_BTC-USD_1d_20260429T000000_L0p786_b983_reaction](charts/fib_BTC-USD_1d_20260429T000000_L0p786_b983_reaction.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 76640.04
- auto_candidate: **reaction_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-05-17T00:00:00+00:00 (bar 983)
- evidence: forward_bars=5, closes_beyond=1, closes_back=5, max_penetration_atr=0.507
- swing: up | start 2026-04-29T00:00:00+00:00 → end 2026-05-06T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L0p618_b984_reaction`

![fib_BTC-USD_1d_20260420T000000_L0p618_b984_reaction](charts/fib_BTC-USD_1d_20260420T000000_L0p618_b984_reaction.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 75917.23
- auto_candidate: **reaction_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-05-18T00:00:00+00:00 (bar 984)
- evidence: forward_bars=5, closes_beyond=1, closes_back=5, max_penetration_atr=0.1744
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L0p236_b987_rejection`

![fib_BTC-USD_1d_20260420T000000_L0p236_b987_rejection](charts/fib_BTC-USD_1d_20260420T000000_L0p236_b987_rejection.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 78119.46
- auto_candidate: **rejection_candidate** | touch_type: close_below | approach_side: below
- event_time: 2026-05-21T00:00:00+00:00 (bar 987)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260413T000000_L0p382_b988_reaction`

![fib_BTC-USD_1d_20260413T000000_L0p382_b988_reaction](charts/fib_BTC-USD_1d_20260413T000000_L0p382_b988_reaction.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 75348.018
- auto_candidate: **reaction_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-05-22T00:00:00+00:00 (bar 988)
- evidence: forward_bars=5, closes_beyond=1, closes_back=4, max_penetration_atr=0.4246
- swing: up | start 2026-04-13T00:00:00+00:00 → end 2026-04-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L0p618_b988_continuation`

![fib_BTC-USD_1d_20260420T000000_L0p618_b988_continuation](charts/fib_BTC-USD_1d_20260420T000000_L0p618_b988_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 75917.23
- auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-05-22T00:00:00+00:00 (bar 988)
- evidence: forward_bars=5, closes_beyond=2, closes_back=3, max_penetration_atr=0.7062
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260413T000000_L0p5_b989_reaction`

![fib_BTC-USD_1d_20260413T000000_L0p5_b989_reaction](charts/fib_BTC-USD_1d_20260413T000000_L0p5_b989_reaction.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 74427.5
- auto_candidate: **reaction_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-05-23T00:00:00+00:00 (bar 989)
- evidence: forward_bars=5, closes_beyond=1, closes_back=4, max_penetration_atr=0.3883
- swing: up | start 2026-04-13T00:00:00+00:00 → end 2026-04-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L0p786_b989_continuation`

![fib_BTC-USD_1d_20260420T000000_L0p786_b989_continuation](charts/fib_BTC-USD_1d_20260420T000000_L0p786_b989_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 74948.71
- auto_candidate: **continuation_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-05-23T00:00:00+00:00 (bar 989)
- evidence: forward_bars=5, closes_beyond=2, closes_back=4, max_penetration_atr=0.634
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260429T000000_L1_b989_continuation`

![fib_BTC-USD_1d_20260429T000000_L1_b989_continuation](charts/fib_BTC-USD_1d_20260429T000000_L1_b989_continuation.png)

- BTC/USD 1d (bitfinex) | fib **1** @ 74958.0
- auto_candidate: **continuation_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-05-23T00:00:00+00:00 (bar 989)
- evidence: forward_bars=5, closes_beyond=2, closes_back=4, max_penetration_atr=0.6384
- swing: up | start 2026-04-29T00:00:00+00:00 → end 2026-05-06T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260514T000000_L0p382_b990_rejection`

![fib_BTC-USD_1d_20260514T000000_L0p382_b990_rejection](charts/fib_BTC-USD_1d_20260514T000000_L0p382_b990_rejection.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 77076.506
- auto_candidate: **rejection_candidate** | touch_type: wick_below | approach_side: below
- event_time: 2026-05-24T00:00:00+00:00 (bar 990)
- evidence: forward_bars=5, closes_beyond=1, closes_back=4, max_penetration_atr=0.147
- swing: down | start 2026-05-14T00:00:00+00:00 → end 2026-05-23T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L0p236_b991_rejection`

![fib_BTC-USD_1d_20260420T000000_L0p236_b991_rejection](charts/fib_BTC-USD_1d_20260420T000000_L0p236_b991_rejection.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 78119.46
- auto_candidate: **rejection_candidate** | touch_type: close_below | approach_side: below
- event_time: 2026-05-25T00:00:00+00:00 (bar 991)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260514T000000_L0p5_b991_rejection`

![fib_BTC-USD_1d_20260514T000000_L0p5_b991_rejection](charts/fib_BTC-USD_1d_20260514T000000_L0p5_b991_rejection.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 78018.5
- auto_candidate: **rejection_candidate** | touch_type: close_below | approach_side: below
- event_time: 2026-05-25T00:00:00+00:00 (bar 991)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- swing: down | start 2026-05-14T00:00:00+00:00 → end 2026-05-23T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260514T000000_L0p236_b992_continuation`

![fib_BTC-USD_1d_20260514T000000_L0p236_b992_continuation](charts/fib_BTC-USD_1d_20260514T000000_L0p236_b992_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 75910.988
- auto_candidate: **continuation_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-05-26T00:00:00+00:00 (bar 992)
- evidence: forward_bars=5, closes_beyond=5, closes_back=0, max_penetration_atr=1.2019
- swing: down | start 2026-05-14T00:00:00+00:00 → end 2026-05-23T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260413T000000_L0p382_b993_continuation`

![fib_BTC-USD_1d_20260413T000000_L0p382_b993_continuation](charts/fib_BTC-USD_1d_20260413T000000_L0p382_b993_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 75348.018
- auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-05-27T00:00:00+00:00 (bar 993)
- evidence: forward_bars=5, closes_beyond=6, closes_back=0, max_penetration_atr=1.9525
- swing: up | start 2026-04-13T00:00:00+00:00 → end 2026-04-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260413T000000_L0p5_b993_continuation`

![fib_BTC-USD_1d_20260413T000000_L0p5_b993_continuation](charts/fib_BTC-USD_1d_20260413T000000_L0p5_b993_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 74427.5
- auto_candidate: **continuation_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-05-27T00:00:00+00:00 (bar 993)
- evidence: forward_bars=5, closes_beyond=5, closes_back=0, max_penetration_atr=1.4973
- swing: up | start 2026-04-13T00:00:00+00:00 → end 2026-04-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L0p786_b993_continuation`

![fib_BTC-USD_1d_20260420T000000_L0p786_b993_continuation](charts/fib_BTC-USD_1d_20260420T000000_L0p786_b993_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 74948.71
- auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-05-27T00:00:00+00:00 (bar 993)
- evidence: forward_bars=5, closes_beyond=6, closes_back=0, max_penetration_atr=1.755
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260429T000000_L1_b993_continuation`

![fib_BTC-USD_1d_20260429T000000_L1_b993_continuation](charts/fib_BTC-USD_1d_20260429T000000_L1_b993_continuation.png)

- BTC/USD 1d (bitfinex) | fib **1** @ 74958.0
- auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-05-27T00:00:00+00:00 (bar 993)
- evidence: forward_bars=5, closes_beyond=6, closes_back=0, max_penetration_atr=1.7596
- swing: up | start 2026-04-29T00:00:00+00:00 → end 2026-05-06T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260413T000000_L0p618_b994_continuation`

![fib_BTC-USD_1d_20260413T000000_L0p618_b994_continuation](charts/fib_BTC-USD_1d_20260413T000000_L0p618_b994_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 73506.982
- auto_candidate: **continuation_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-05-28T00:00:00+00:00 (bar 994)
- evidence: forward_bars=5, closes_beyond=2, closes_back=2, max_penetration_atr=2.1568
- swing: up | start 2026-04-13T00:00:00+00:00 → end 2026-04-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260407T000000_L1_b994_continuation`

![fib_BTC-USD_1d_20260407T000000_L1_b994_continuation](charts/fib_BTC-USD_1d_20260407T000000_L1_b994_continuation.png)

- BTC/USD 1d (bitfinex) | fib **1** @ 72789.0
- auto_candidate: **continuation_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-05-28T00:00:00+00:00 (bar 994)
- evidence: forward_bars=5, closes_beyond=2, closes_back=4, max_penetration_atr=1.8022
- swing: down | start 2026-04-07T00:00:00+00:00 → end 2026-04-07T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260420T000000_L1_b994_continuation`

![fib_BTC-USD_1d_20260420T000000_L1_b994_continuation](charts/fib_BTC-USD_1d_20260420T000000_L1_b994_continuation.png)

- BTC/USD 1d (bitfinex) | fib **1** @ 73715.0
- auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-05-28T00:00:00+00:00 (bar 994)
- evidence: forward_bars=5, closes_beyond=3, closes_back=1, max_penetration_atr=2.2595
- swing: up | start 2026-04-20T00:00:00+00:00 → end 2026-04-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260526T000000_L0p236_b996_rejection`

![fib_BTC-USD_1d_20260526T000000_L0p236_b996_rejection](charts/fib_BTC-USD_1d_20260526T000000_L0p236_b996_rejection.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 73818.512
- auto_candidate: **rejection_candidate** | touch_type: wick_below | approach_side: below
- event_time: 2026-05-30T00:00:00+00:00 (bar 996)
- evidence: forward_bars=3, closes_beyond=0, closes_back=2, max_penetration_atr=0.0533
- swing: down | start 2026-05-26T00:00:00+00:00 → end 2026-05-29T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260407T000000_L0p618_b998_reaction`

![fib_BTC-USD_1d_20260407T000000_L0p618_b998_reaction](charts/fib_BTC-USD_1d_20260407T000000_L0p618_b998_reaction.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 70847.294
- auto_candidate: **reaction_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-06-01T00:00:00+00:00 (bar 998)
- evidence: forward_bars=1, closes_beyond=1, closes_back=1, max_penetration_atr=0.8621
- swing: down | start 2026-04-07T00:00:00+00:00 → end 2026-04-07T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260407T000000_L0p786_b998_continuation`

![fib_BTC-USD_1d_20260407T000000_L0p786_b998_continuation](charts/fib_BTC-USD_1d_20260407T000000_L0p786_b998_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 71701.238
- auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-06-01T00:00:00+00:00 (bar 998)
- evidence: forward_bars=1, closes_beyond=2, closes_back=0, max_penetration_atr=1.2933
- swing: down | start 2026-04-07T00:00:00+00:00 → end 2026-04-07T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260413T000000_L0p786_b998_continuation`

![fib_BTC-USD_1d_20260413T000000_L0p786_b998_continuation](charts/fib_BTC-USD_1d_20260413T000000_L0p786_b998_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 72196.414
- auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-06-01T00:00:00+00:00 (bar 998)
- evidence: forward_bars=1, closes_beyond=2, closes_back=0, max_penetration_atr=1.5433
- swing: up | start 2026-04-13T00:00:00+00:00 → end 2026-04-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260413T000000_L1_b998_reaction`

![fib_BTC-USD_1d_20260413T000000_L1_b998_reaction](charts/fib_BTC-USD_1d_20260413T000000_L1_b998_reaction.png)

- BTC/USD 1d (bitfinex) | fib **1** @ 70527.0
- auto_candidate: **reaction_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-06-01T00:00:00+00:00 (bar 998)
- evidence: forward_bars=1, closes_beyond=1, closes_back=1, max_penetration_atr=0.7004
- swing: up | start 2026-04-13T00:00:00+00:00 → end 2026-04-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260407T000000_L0p236_b999_reaction`

![fib_BTC-USD_1d_20260407T000000_L0p236_b999_reaction](charts/fib_BTC-USD_1d_20260407T000000_L0p236_b999_reaction.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 68905.588
- auto_candidate: **reaction_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-06-02T00:00:00+00:00 (bar 999)
- evidence: forward_bars=0, closes_beyond=0, closes_back=1, max_penetration_atr=0.0
- swing: down | start 2026-04-07T00:00:00+00:00 → end 2026-04-07T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260407T000000_L0p382_b999_continuation`

![fib_BTC-USD_1d_20260407T000000_L0p382_b999_continuation](charts/fib_BTC-USD_1d_20260407T000000_L0p382_b999_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 69647.706
- auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-06-02T00:00:00+00:00 (bar 999)
- evidence: forward_bars=0, closes_beyond=1, closes_back=0, max_penetration_atr=0.2534
- swing: down | start 2026-04-07T00:00:00+00:00 → end 2026-04-07T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `fib_BTC-USD_1d_20260407T000000_L0p5_b999_continuation`

![fib_BTC-USD_1d_20260407T000000_L0p5_b999_continuation](charts/fib_BTC-USD_1d_20260407T000000_L0p5_b999_continuation.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 70247.5
- auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-06-02T00:00:00+00:00 (bar 999)
- evidence: forward_bars=0, closes_beyond=1, closes_back=0, max_penetration_atr=0.5527
- swing: down | start 2026-04-07T00:00:00+00:00 → end 2026-04-07T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____
