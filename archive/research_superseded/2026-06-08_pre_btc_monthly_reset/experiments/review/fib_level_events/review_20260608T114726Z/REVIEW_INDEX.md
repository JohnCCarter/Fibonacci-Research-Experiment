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

- Total candidates available: **3087**
- Total sampled: **40**
- Sampled by candidate type: `{'continuation_candidate': 10, 'failure_candidate': 10, 'reaction_candidate': 10, 'rejection_candidate': 10}`
- Sampled by fib level: `{'0.236': 8, '0.382': 8, '0.5': 8, '0.618': 8, '0.786': 8}`
- Output dir: `C:\Users\fa06662\Projects\Fibonacci-Research-Experiment-main\experiments\review\fib_level_events\review_20260608T114726Z`

## Events

### `BTC-USD_1d_L0p236_s152_e154_b290_cont`

![BTC-USD_1d_L0p236_s152_e154_b290_cont](charts/BTC-USD_1d_L0p236_s152_e154_b290_cont.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 27591.544 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2023-08-17T00:00:00+00:00 (bar 290)
- evidence: forward_bars=5, closes_beyond=6, closes_back=0, max_penetration_atr=1.9551
- anchors: H/L shown on chart | direction down | anchor_a 2023-04-01T00:00:00+00:00 -> anchor_b 2023-04-03T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p236_s193_e216_b332_cont`

![BTC-USD_1d_L0p236_s193_e216_b332_cont](charts/BTC-USD_1d_L0p236_s193_e216_b332_cont.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 27090.86 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: below
- event_time: 2023-09-28T00:00:00+00:00 (bar 332)
- evidence: forward_bars=5, closes_beyond=3, closes_back=2, max_penetration_atr=1.4792
- anchors: H/L shown on chart | direction up | anchor_a 2023-05-12T00:00:00+00:00 -> anchor_b 2023-06-04T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p236_s227_e229_b230_rej`

![BTC-USD_1d_L0p236_s227_e229_b230_rej](charts/BTC-USD_1d_L0p236_s227_e229_b230_rej.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 26377.448 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **rejection_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2023-06-18T00:00:00+00:00 (bar 230)
- evidence: forward_bars=5, closes_beyond=0, closes_back=5, max_penetration_atr=0.0224
- anchors: H/L shown on chart | direction up | anchor_a 2023-06-15T00:00:00+00:00 -> anchor_b 2023-06-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p236_s249_e500_b707_react`

![BTC-USD_1d_L0p236_s249_e500_b707_react](charts/BTC-USD_1d_L0p236_s249_e500_b707_react.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 63301.824 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **reaction_candidate** | touch_type: wick_above | approach_side: below
- event_time: 2024-10-07T00:00:00+00:00 (bar 707)
- evidence: forward_bars=5, closes_beyond=0, closes_back=5, max_penetration_atr=0.0169
- anchors: H/L shown on chart | direction up | anchor_a 2023-07-07T00:00:00+00:00 -> anchor_b 2024-03-14T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p236_s249_e637_b642_fail`

![BTC-USD_1d_L0p236_s249_e637_b642_fail](charts/BTC-USD_1d_L0p236_s249_e637_b642_fail.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 60624.768 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **failure_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2024-08-03T00:00:00+00:00 (bar 642)
- evidence: forward_bars=5, closes_beyond=4, closes_back=1, max_penetration_atr=2.5397
- anchors: H/L shown on chart | direction up | anchor_a 2023-07-07T00:00:00+00:00 -> anchor_b 2024-07-29T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p236_s249_e637_b701_rej`

![BTC-USD_1d_L0p236_s249_e637_b701_rej](charts/BTC-USD_1d_L0p236_s249_e637_b701_rej.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 60624.768 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **rejection_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2024-10-01T00:00:00+00:00 (bar 701)
- evidence: forward_bars=5, closes_beyond=0, closes_back=5, max_penetration_atr=0.0
- anchors: H/L shown on chart | direction up | anchor_a 2023-07-07T00:00:00+00:00 -> anchor_b 2024-07-29T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p236_s255_e260_b275_react`

![BTC-USD_1d_L0p236_s255_e260_b275_react](charts/BTC-USD_1d_L0p236_s255_e260_b275_react.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 30086.272 | fib_id: `machine_swing`
- relation: **below** | auto_candidate: **reaction_candidate** | touch_type: close_below | approach_side: below
- event_time: 2023-08-02T00:00:00+00:00 (bar 275)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- anchors: H/L shown on chart | direction down | anchor_a 2023-07-13T00:00:00+00:00 -> anchor_b 2023-07-18T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p236_s255_e419_b448_fail`

![BTC-USD_1d_L0p236_s255_e419_b448_fail](charts/BTC-USD_1d_L0p236_s255_e419_b448_fail.png)

- BTC/USD 1d (bitfinex) | fib **0.236** @ 40138.22 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **failure_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2024-01-22T00:00:00+00:00 (bar 448)
- evidence: forward_bars=5, closes_beyond=2, closes_back=2, max_penetration_atr=0.2962
- anchors: H/L shown on chart | direction up | anchor_a 2023-07-13T00:00:00+00:00 -> anchor_b 2023-12-24T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p382_s175_e177_b178_fail`

![BTC-USD_1d_L0p382_s175_e177_b178_fail](charts/BTC-USD_1d_L0p382_s175_e177_b178_fail.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 28866.608 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **failure_candidate** | touch_type: wick_below | approach_side: below
- event_time: 2023-04-27T00:00:00+00:00 (bar 178)
- evidence: forward_bars=5, closes_beyond=4, closes_back=2, max_penetration_atr=0.5351
- anchors: H/L shown on chart | direction up | anchor_a 2023-04-24T00:00:00+00:00 -> anchor_b 2023-04-26T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p382_s227_e229_b329_rej`

![BTC-USD_1d_L0p382_s227_e229_b329_rej](charts/BTC-USD_1d_L0p382_s227_e229_b329_rej.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 26080.776 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **rejection_candidate** | touch_type: close_above | approach_side: above
- event_time: 2023-09-25T00:00:00+00:00 (bar 329)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- anchors: H/L shown on chart | direction up | anchor_a 2023-06-15T00:00:00+00:00 -> anchor_b 2023-06-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p382_s249_e568_b613_rej`

![BTC-USD_1d_L0p382_s249_e568_b613_rej](charts/BTC-USD_1d_L0p382_s249_e568_b613_rej.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 55812.296 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **rejection_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2024-07-05T00:00:00+00:00 (bar 613)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- anchors: H/L shown on chart | direction up | anchor_a 2023-07-07T00:00:00+00:00 -> anchor_b 2024-05-21T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p382_s249_e853_b1193_cont`

![BTC-USD_1d_L0p382_s249_e853_b1193_cont](charts/BTC-USD_1d_L0p382_s249_e853_b1193_cont.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 70272.878 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-02-05T00:00:00+00:00 (bar 1193)
- evidence: forward_bars=5, closes_beyond=3, closes_back=0, max_penetration_atr=1.7707
- anchors: H/L shown on chart | direction up | anchor_a 2023-07-07T00:00:00+00:00 -> anchor_b 2025-03-02T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p382_s249_e963_b1188_cont`

![BTC-USD_1d_L0p382_s249_e963_b1188_cont](charts/BTC-USD_1d_L0p382_s249_e963_b1188_cont.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 77230.94 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **continuation_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2026-01-31T00:00:00+00:00 (bar 1188)
- evidence: forward_bars=5, closes_beyond=3, closes_back=2, max_penetration_atr=4.5581
- anchors: H/L shown on chart | direction up | anchor_a 2023-07-07T00:00:00+00:00 -> anchor_b 2025-06-20T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p382_s255_e274_b350_react`

![BTC-USD_1d_L0p382_s255_e274_b350_react](charts/BTC-USD_1d_L0p382_s255_e274_b350_react.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 29862.456 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **reaction_candidate** | touch_type: wick_above | approach_side: below
- event_time: 2023-10-16T00:00:00+00:00 (bar 350)
- evidence: forward_bars=5, closes_beyond=0, closes_back=5, max_penetration_atr=0.0788
- anchors: H/L shown on chart | direction down | anchor_a 2023-07-13T00:00:00+00:00 -> anchor_b 2023-08-01T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p382_s255_e770_b1218_fail`

![BTC-USD_1d_L0p382_s255_e770_b1218_fail](charts/BTC-USD_1d_L0p382_s255_e770_b1218_fail.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 70393.986 | fib_id: `machine_swing`
- relation: **below** | auto_candidate: **failure_candidate** | touch_type: close_below | approach_side: below
- event_time: 2026-03-02T00:00:00+00:00 (bar 1218)
- evidence: forward_bars=5, closes_beyond=2, closes_back=4, max_penetration_atr=0.6586
- anchors: H/L shown on chart | direction up | anchor_a 2023-07-13T00:00:00+00:00 -> anchor_b 2024-12-09T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p382_s255_e931_b1299_react`

![BTC-USD_1d_L0p382_s255_e931_b1299_react](charts/BTC-USD_1d_L0p382_s255_e931_b1299_react.png)

- BTC/USD 1d (bitfinex) | fib **0.382** @ 75206.97 | fib_id: `machine_swing`
- relation: **above** | auto_candidate: **reaction_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-05-22T00:00:00+00:00 (bar 1299)
- evidence: forward_bars=5, closes_beyond=1, closes_back=5, max_penetration_atr=0.3548
- anchors: H/L shown on chart | direction up | anchor_a 2023-07-13T00:00:00+00:00 -> anchor_b 2025-05-19T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p5_s150_e151_b336_react`

![BTC-USD_1d_L0p5_s150_e151_b336_react](charts/BTC-USD_1d_L0p5_s150_e151_b336_react.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 28337.5 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **reaction_candidate** | touch_type: wick_above | approach_side: below
- event_time: 2023-10-02T00:00:00+00:00 (bar 336)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- anchors: H/L shown on chart | direction down | anchor_a 2023-03-30T00:00:00+00:00 -> anchor_b 2023-03-31T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p5_s193_e216_b296_rej`

![BTC-USD_1d_L0p5_s193_e216_b296_rej](charts/BTC-USD_1d_L0p5_s193_e216_b296_rej.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 26664.5 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **rejection_candidate** | touch_type: wick_above | approach_side: below
- event_time: 2023-08-23T00:00:00+00:00 (bar 296)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- anchors: H/L shown on chart | direction up | anchor_a 2023-05-12T00:00:00+00:00 -> anchor_b 2023-06-04T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p5_s218_e219_b220_fail`

![BTC-USD_1d_L0p5_s218_e219_b220_fail](charts/BTC-USD_1d_L0p5_s218_e219_b220_fail.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 26362.0 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **failure_candidate** | touch_type: wick_below | approach_side: below
- event_time: 2023-06-08T00:00:00+00:00 (bar 220)
- evidence: forward_bars=5, closes_beyond=2, closes_back=4, max_penetration_atr=0.1774
- anchors: H/L shown on chart | direction up | anchor_a 2023-06-06T00:00:00+00:00 -> anchor_b 2023-06-07T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p5_s227_e275_b290_cont`

![BTC-USD_1d_L0p5_s227_e275_b290_cont](charts/BTC-USD_1d_L0p5_s227_e275_b290_cont.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 27450.5 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2023-08-17T00:00:00+00:00 (bar 290)
- evidence: forward_bars=5, closes_beyond=6, closes_back=0, max_penetration_atr=1.7749
- anchors: H/L shown on chart | direction up | anchor_a 2023-06-15T00:00:00+00:00 -> anchor_b 2023-08-02T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p5_s249_e1021_b1304_cont`

![BTC-USD_1d_L0p5_s249_e1021_b1304_cont](charts/BTC-USD_1d_L0p5_s249_e1021_b1304_cont.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 74215.0 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **continuation_candidate** | touch_type: close_above | approach_side: above
- event_time: 2026-05-27T00:00:00+00:00 (bar 1304)
- evidence: forward_bars=5, closes_beyond=5, closes_back=1, max_penetration_atr=1.3923
- anchors: H/L shown on chart | direction up | anchor_a 2023-07-07T00:00:00+00:00 -> anchor_b 2025-08-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p5_s255_e274_b281_rej`

![BTC-USD_1d_L0p5_s255_e274_b281_rej](charts/BTC-USD_1d_L0p5_s255_e274_b281_rej.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 30241.0 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **rejection_candidate** | touch_type: close_below | approach_side: below
- event_time: 2023-08-08T00:00:00+00:00 (bar 281)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- anchors: H/L shown on chart | direction down | anchor_a 2023-07-13T00:00:00+00:00 -> anchor_b 2023-08-01T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p5_s255_e295_b336_react`

![BTC-USD_1d_L0p5_s255_e295_b336_react](charts/BTC-USD_1d_L0p5_s255_e295_b336_react.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 28616.0 | fib_id: `machine_swing`
- relation: **below** | auto_candidate: **reaction_candidate** | touch_type: close_below | approach_side: below
- event_time: 2023-10-02T00:00:00+00:00 (bar 336)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- anchors: H/L shown on chart | direction down | anchor_a 2023-07-13T00:00:00+00:00 -> anchor_b 2023-08-22T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p5_s255_e948_b1193_fail`

![BTC-USD_1d_L0p5_s255_e948_b1193_fail](charts/BTC-USD_1d_L0p5_s255_e948_b1193_fail.png)

- BTC/USD 1d (bitfinex) | fib **0.5** @ 66182.5 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **failure_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-02-05T00:00:00+00:00 (bar 1193)
- evidence: forward_bars=5, closes_beyond=1, closes_back=5, max_penetration_atr=0.7762
- anchors: H/L shown on chart | direction up | anchor_a 2023-07-13T00:00:00+00:00 -> anchor_b 2025-06-05T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p618_s165_e172_b185_rej`

![BTC-USD_1d_L0p618_s165_e172_b185_rej](charts/BTC-USD_1d_L0p618_s165_e172_b185_rej.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 29511.434 | fib_id: `machine_swing`
- relation: **below** | auto_candidate: **rejection_candidate** | touch_type: close_below | approach_side: below
- event_time: 2023-05-04T00:00:00+00:00 (bar 185)
- evidence: forward_bars=5, closes_beyond=0, closes_back=5, max_penetration_atr=0.0137
- anchors: H/L shown on chart | direction down | anchor_a 2023-04-14T00:00:00+00:00 -> anchor_b 2023-04-21T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p618_s165_e172_b354_cont`

![BTC-USD_1d_L0p618_s165_e172_b354_cont](charts/BTC-USD_1d_L0p618_s165_e172_b354_cont.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 29511.434 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **continuation_candidate** | touch_type: wick_below | approach_side: below
- event_time: 2023-10-20T00:00:00+00:00 (bar 354)
- evidence: forward_bars=5, closes_beyond=6, closes_back=0, max_penetration_atr=6.1371
- anchors: H/L shown on chart | direction down | anchor_a 2023-04-14T00:00:00+00:00 -> anchor_b 2023-04-21T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p618_s206_e207_b328_react`

![BTC-USD_1d_L0p618_s206_e207_b328_react](charts/BTC-USD_1d_L0p618_s206_e207_b328_react.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 26291.302 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **reaction_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2023-09-24T00:00:00+00:00 (bar 328)
- evidence: forward_bars=5, closes_beyond=0, closes_back=3, max_penetration_atr=0.0761
- anchors: H/L shown on chart | direction up | anchor_a 2023-05-25T00:00:00+00:00 -> anchor_b 2023-05-26T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p618_s218_e225_b290_react`

![BTC-USD_1d_L0p618_s218_e225_b290_react](charts/BTC-USD_1d_L0p618_s218_e225_b290_react.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 25760.368 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **reaction_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2023-08-17T00:00:00+00:00 (bar 290)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- anchors: H/L shown on chart | direction up | anchor_a 2023-06-06T00:00:00+00:00 -> anchor_b 2023-06-13T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p618_s227_e235_b332_cont`

![BTC-USD_1d_L0p618_s227_e235_b332_cont](charts/BTC-USD_1d_L0p618_s227_e235_b332_cont.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 27348.11 | fib_id: `machine_swing`
- relation: **below** | auto_candidate: **continuation_candidate** | touch_type: close_below | approach_side: below
- event_time: 2023-09-28T00:00:00+00:00 (bar 332)
- evidence: forward_bars=5, closes_beyond=3, closes_back=3, max_penetration_atr=1.0652
- anchors: H/L shown on chart | direction up | anchor_a 2023-06-15T00:00:00+00:00 -> anchor_b 2023-06-23T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p618_s227_e245_b322_rej`

![BTC-USD_1d_L0p618_s227_e245_b322_rej](charts/BTC-USD_1d_L0p618_s227_e245_b322_rej.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 27342.762 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **rejection_candidate** | touch_type: wick_above | approach_side: below
- event_time: 2023-09-18T00:00:00+00:00 (bar 322)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- anchors: H/L shown on chart | direction up | anchor_a 2023-06-15T00:00:00+00:00 -> anchor_b 2023-07-03T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p618_s227_e258_b345_fail`

![BTC-USD_1d_L0p618_s227_e258_b345_fail](charts/BTC-USD_1d_L0p618_s227_e258_b345_fail.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 26986.738 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **failure_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2023-10-11T00:00:00+00:00 (bar 345)
- evidence: forward_bars=5, closes_beyond=4, closes_back=2, max_penetration_atr=0.2953
- anchors: H/L shown on chart | direction up | anchor_a 2023-06-15T00:00:00+00:00 -> anchor_b 2023-07-16T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p618_s249_e1021_b1193_fail`

![BTC-USD_1d_L0p618_s249_e1021_b1193_fail](charts/BTC-USD_1d_L0p618_s249_e1021_b1193_fail.png)

- BTC/USD 1d (bitfinex) | fib **0.618** @ 63721.26 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **failure_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2026-02-05T00:00:00+00:00 (bar 1193)
- evidence: forward_bars=5, closes_beyond=1, closes_back=5, max_penetration_atr=0.1778
- anchors: H/L shown on chart | direction up | anchor_a 2023-07-07T00:00:00+00:00 -> anchor_b 2025-08-17T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p786_s165_e175_b248_fail`

![BTC-USD_1d_L0p786_s165_e175_b248_fail](charts/BTC-USD_1d_L0p786_s165_e175_b248_fail.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 30114.14 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **failure_candidate** | touch_type: wick_above | approach_side: above
- event_time: 2023-07-06T00:00:00+00:00 (bar 248)
- evidence: forward_bars=5, closes_beyond=1, closes_back=4, max_penetration_atr=0.1916
- anchors: H/L shown on chart | direction down | anchor_a 2023-04-14T00:00:00+00:00 -> anchor_b 2023-04-24T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p786_s165_e193_b354_cont`

![BTC-USD_1d_L0p786_s165_e193_b354_cont](charts/BTC-USD_1d_L0p786_s165_e193_b354_cont.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 29874.246 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **continuation_candidate** | touch_type: wick_above | approach_side: below
- event_time: 2023-10-20T00:00:00+00:00 (bar 354)
- evidence: forward_bars=5, closes_beyond=4, closes_back=1, max_penetration_atr=5.6911
- anchors: H/L shown on chart | direction down | anchor_a 2023-04-14T00:00:00+00:00 -> anchor_b 2023-05-12T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p786_s165_e199_b275_react`

![BTC-USD_1d_L0p786_s165_e199_b275_react](charts/BTC-USD_1d_L0p786_s165_e199_b275_react.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 29993.23 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **reaction_candidate** | touch_type: wick_above | approach_side: below
- event_time: 2023-08-02T00:00:00+00:00 (bar 275)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- anchors: H/L shown on chart | direction down | anchor_a 2023-04-14T00:00:00+00:00 -> anchor_b 2023-05-18T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p786_s182_e196_b209_fail`

![BTC-USD_1d_L0p786_s182_e196_b209_fail](charts/BTC-USD_1d_L0p786_s182_e196_b209_fail.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 27688.148 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **failure_candidate** | touch_type: wick_below | approach_side: below
- event_time: 2023-05-28T00:00:00+00:00 (bar 209)
- evidence: forward_bars=5, closes_beyond=1, closes_back=3, max_penetration_atr=0.4843
- anchors: H/L shown on chart | direction down | anchor_a 2023-05-01T00:00:00+00:00 -> anchor_b 2023-05-15T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p786_s210_e227_b335_cont`

![BTC-USD_1d_L0p786_s210_e227_b335_cont](charts/BTC-USD_1d_L0p786_s210_e227_b335_cont.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 27693.9 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **continuation_candidate** | touch_type: wick_below | approach_side: below
- event_time: 2023-10-01T00:00:00+00:00 (bar 335)
- evidence: forward_bars=5, closes_beyond=3, closes_back=3, max_penetration_atr=0.505
- anchors: H/L shown on chart | direction down | anchor_a 2023-05-29T00:00:00+00:00 -> anchor_b 2023-06-15T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p786_s210_e256_b274_react`

![BTC-USD_1d_L0p786_s210_e256_b274_react](charts/BTC-USD_1d_L0p786_s210_e256_b274_react.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 28786.156 | fib_id: `machine_swing`
- relation: **touch** | auto_candidate: **reaction_candidate** | touch_type: wick_below | approach_side: above
- event_time: 2023-08-01T00:00:00+00:00 (bar 274)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- anchors: H/L shown on chart | direction up | anchor_a 2023-05-29T00:00:00+00:00 -> anchor_b 2023-07-14T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p786_s227_e258_b329_rej`

![BTC-USD_1d_L0p786_s227_e258_b329_rej](charts/BTC-USD_1d_L0p786_s227_e258_b329_rej.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 26036.026 | fib_id: `machine_swing`
- relation: **above** | auto_candidate: **rejection_candidate** | touch_type: close_above | approach_side: above
- event_time: 2023-09-25T00:00:00+00:00 (bar 329)
- evidence: forward_bars=5, closes_beyond=0, closes_back=6, max_penetration_atr=0.0
- anchors: H/L shown on chart | direction up | anchor_a 2023-06-15T00:00:00+00:00 -> anchor_b 2023-07-16T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____

### `BTC-USD_1d_L0p786_s249_e268_b281_rej`

![BTC-USD_1d_L0p786_s249_e268_b281_rej](charts/BTC-USD_1d_L0p786_s249_e268_b281_rej.png)

- BTC/USD 1d (bitfinex) | fib **0.786** @ 29743.794 | fib_id: `machine_swing`
- relation: **cross** | auto_candidate: **rejection_candidate** | touch_type: wick_below | approach_side: below
- event_time: 2023-08-08T00:00:00+00:00 (bar 281)
- evidence: forward_bars=5, closes_beyond=0, closes_back=5, max_penetration_atr=0.0834
- anchors: H/L shown on chart | direction down | anchor_a 2023-07-07T00:00:00+00:00 -> anchor_b 2023-07-26T00:00:00+00:00
- **human_label:** ____  **human_confidence:** ____  **human_note:** ____
