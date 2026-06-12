# BTC/USD 1D Reaction-Review Cycle (2026-06-12)

## Overview

| | |
|---|---|
| Timeframe | 1D source fibs → 4H reaction |
| Protocol | BTC-first top-down |
| Fib count | 67 |
| Coverage | 2017-01-05 → 2024-12-20 |
| Direction split | 34 down / 33 up |
| Review window | anchor_b + 90 days (fixed horizon) |
| Cache used | expansion config: 4H back to 2017-01-01 (`limit_8000.csv`) |
| Review TFs | 4H only (1H deferred — cache not fetched) |
| Total 4H interactions | **1 816** |
| Mean per fib | 27.1 |
| Artifacts | `experiments/review/source_fib_projection/<fib_id>/` × 67 |
| Batch manifest | `experiments/review/source_fib_projection/btc_1d_batch_manifest.json` |
| Review windows | `data/labels/human_fib/bitfinex/BTC-USD/1d/review_windows.yaml` |
| Batch script | `scripts/run_btc_1d_reaction_review.py` |

Pipeline: `source_fib_projection_review` (per fib) via batch runner. No charts generated — run `source_fib_projection_chart` per fib if needed.

---

## Summary Table

| Fib ID | Dir | Anchor A | Anchor B | Review End | 4H Events |
|--------|-----|----------|----------|------------|-----------|
| fib_BTC-USD_1d_20170105T000000 | down | 2017-01-05 | 2017-01-12 | 2017-04-12 | 33 |
| fib_BTC-USD_1d_20170112T000000 | up | 2017-01-12 | 2017-03-04 | 2017-06-02 | 13 |
| fib_BTC-USD_1d_20170316T000000 | down | 2017-03-16 | 2017-03-25 | 2017-06-23 | 11 |
| fib_BTC-USD_1d_20170525T000000 | **down** | 2017-05-25 | 2017-05-27 | 2017-08-25 | **54** |
| fib_BTC-USD_1d_20170527T000000 | up | 2017-05-27 | 2017-06-11 | 2017-09-09 | 30 |
| fib_BTC-USD_1d_20170612T000000 | down | 2017-06-12 | 2017-06-15 | 2017-09-13 | 37 |
| fib_BTC-USD_1d_20170716T000000 | up | 2017-07-16 | 2017-09-02 | 2017-12-01 | **3** |
| fib_BTC-USD_1d_20170902T000000 | down | 2017-09-02 | 2017-09-15 | 2017-12-14 | 17 |
| fib_BTC-USD_1d_20170915T000000 | up | 2017-09-15 | 2017-09-19 | 2017-12-18 | **5** |
| fib_BTC-USD_1d_20171108T000000 | down | 2017-11-08 | 2017-11-12 | 2018-02-10 | 17 |
| fib_BTC-USD_1d_20171112T000000 | up | 2017-11-12 | 2017-12-17 | 2018-03-17 | 29 |
| fib_BTC-USD_1d_20171205T000000 | **up** | 2017-12-05 | 2017-12-08 | 2018-03-08 | **51** |
| fib_BTC-USD_1d_20171217T000000 | down | 2017-12-17 | 2017-12-22 | 2018-03-22 | 30 |
| fib_BTC-USD_1d_20171222T000000 | up | 2017-12-22 | 2017-12-27 | 2018-03-27 | 38 |
| fib_BTC-USD_1d_20171230T000000 | up | 2017-12-30 | 2018-01-06 | 2018-04-06 | 21 |
| fib_BTC-USD_1d_20180107T000000 | down | 2018-01-07 | 2018-01-11 | 2018-04-11 | 6 |
| fib_BTC-USD_1d_20180115T000000 | down | 2018-01-15 | 2018-01-17 | 2018-04-17 | 34 |
| fib_BTC-USD_1d_20180121T000000 | down | 2018-01-21 | 2018-01-23 | 2018-04-23 | 31 |
| fib_BTC-USD_1d_20180128T000000 | down | 2018-01-28 | 2018-02-06 | 2018-05-07 | 42 |
| fib_BTC-USD_1d_20180206T000000 | up | 2018-02-06 | 2018-02-20 | 2018-05-21 | 42 |
| fib_BTC-USD_1d_20180305T000000 | down | 2018-03-05 | 2018-03-09 | 2018-06-07 | 26 |
| fib_BTC-USD_1d_20180312T000000 | down | 2018-03-12 | 2018-03-18 | 2018-06-16 | 44 |
| fib_BTC-USD_1d_20190610T000000 | up | 2019-06-10 | 2019-06-26 | 2019-09-24 | 39 |
| fib_BTC-USD_1d_20190710T000000 | down | 2019-07-10 | 2019-07-17 | 2019-10-15 | 31 |
| fib_BTC-USD_1d_20190806T000000 | down | 2019-08-06 | 2019-08-15 | 2019-11-13 | 19 |
| fib_BTC-USD_1d_20191026T000000 | down | 2019-10-26 | 2019-11-25 | 2020-02-23 | 24 |
| fib_BTC-USD_1d_20191218T000000 | up | 2019-12-18 | 2019-12-23 | 2020-03-22 | 19 |
| fib_BTC-USD_1d_20200102T000000 | up | 2020-01-02 | 2020-01-08 | 2020-04-07 | 22 |
| fib_BTC-USD_1d_20200307T000000 | down | 2020-03-07 | 2020-03-13 | 2020-06-11 | 31 |
| fib_BTC-USD_1d_20200316T000000 | up | 2020-03-16 | 2020-03-20 | 2020-06-18 | 13 |
| fib_BTC-USD_1d_20200330T000000 | up | 2020-03-30 | 2020-04-08 | 2020-07-07 | 10 |
| fib_BTC-USD_1d_20200416T000000 | up | 2020-04-16 | 2020-04-19 | 2020-07-18 | **5** |
| fib_BTC-USD_1d_20200421T000000 | up | 2020-04-21 | 2020-05-07 | 2020-08-05 | 9 |
| fib_BTC-USD_1d_20200510T000000 | up | 2020-05-10 | 2020-05-14 | 2020-08-12 | 39 |
| fib_BTC-USD_1d_20200721T000000 | up | 2020-07-21 | 2020-08-02 | 2020-10-31 | 25 |
| fib_BTC-USD_1d_20201211T000000 | up | 2020-12-11 | 2020-12-20 | 2021-03-20 | **2** |
| fib_BTC-USD_1d_20201221T000000 | up | 2020-12-21 | 2021-01-08 | 2021-04-08 | 13 |
| fib_BTC-USD_1d_20210114T000000 | down | 2021-01-14 | 2021-01-22 | 2021-04-22 | 17 |
| fib_BTC-USD_1d_20210127T000000 | up | 2021-01-27 | 2021-02-21 | 2021-05-22 | 28 |
| fib_BTC-USD_1d_20210228T000000 | up | 2021-02-28 | 2021-03-13 | 2021-06-11 | 33 |
| fib_BTC-USD_1d_20210325T000000 | up | 2021-03-25 | 2021-04-02 | 2021-07-01 | 37 |
| fib_BTC-USD_1d_20210414T000000 | down | 2021-04-14 | 2021-04-25 | 2021-07-24 | 20 |
| fib_BTC-USD_1d_20210510T000000 | down | 2021-05-10 | 2021-05-19 | 2021-08-17 | 23 |
| fib_BTC-USD_1d_20210720T000000 | up | 2021-07-20 | 2021-08-01 | 2021-10-30 | 6 |
| fib_BTC-USD_1d_20210805T000000 | up | 2021-08-05 | 2021-09-07 | 2021-12-06 | 24 |
| fib_BTC-USD_1d_20210907T000000 | down | 2021-09-07 | 2021-09-07 | 2021-12-06 | 30 |
| fib_BTC-USD_1d_20210918T000000 | down | 2021-09-18 | 2021-09-21 | 2021-12-20 | 27 |
| fib_BTC-USD_1d_20210929T000000 | up | 2021-09-29 | 2021-11-09 | 2022-02-07 | 29 |
| fib_BTC-USD_1d_20211109T000000 | down | 2021-11-09 | 2021-11-12 | 2022-02-10 | 7 |
| fib_BTC-USD_1d_20211227T000000 | down | 2021-12-27 | 2021-12-31 | 2022-03-31 | 10 |
| fib_BTC-USD_1d_20220105T000000 | **down** | 2022-01-05 | 2022-01-10 | 2022-04-10 | **65** |
| fib_BTC-USD_1d_20220120T000000 | **down** | 2022-01-20 | 2022-01-24 | 2022-04-24 | **57** |
| fib_BTC-USD_1d_20220124T000000 | **up** | 2022-01-24 | 2022-02-10 | 2022-05-11 | **52** |
| fib_BTC-USD_1d_20220215T000000 | **down** | 2022-02-15 | 2022-02-24 | 2022-05-25 | **60** |
| fib_BTC-USD_1d_20220505T000000 | down | 2022-05-05 | 2022-05-12 | 2022-08-10 | 10 |
| fib_BTC-USD_1d_20220607T000000 | down | 2022-06-07 | 2022-06-18 | 2022-09-16 | 23 |
| fib_BTC-USD_1d_20220618T000000 | **up** | 2022-06-18 | 2022-06-26 | 2022-09-24 | **45** |
| fib_BTC-USD_1d_20220713T000000 | **up** | 2022-07-13 | 2022-07-20 | 2022-10-18 | **50** |
| fib_BTC-USD_1d_20220913T000000 | down | 2022-09-13 | 2022-09-21 | 2022-12-20 | 31 |
| fib_BTC-USD_1d_20221105T000000 | down | 2022-11-05 | 2022-11-09 | 2023-02-07 | 17 |
| fib_BTC-USD_1d_20230107T000000 | up | 2023-01-07 | 2023-02-02 | 2023-05-03 | 10 |
| fib_BTC-USD_1d_20230310T000000 | up | 2023-03-10 | 2023-03-14 | 2023-06-12 | 14 |
| fib_BTC-USD_1d_20230815T000000 | down | 2023-08-15 | 2023-08-17 | 2023-11-15 | 37 |
| fib_BTC-USD_1d_20240223T000000 | up | 2024-02-23 | 2024-03-14 | 2024-06-12 | 23 |
| fib_BTC-USD_1d_20240408T000000 | **down** | 2024-04-08 | 2024-04-17 | 2024-07-16 | **48** |
| fib_BTC-USD_1d_20240805T000000 | up | 2024-08-05 | 2024-08-23 | 2024-11-21 | 19 |
| fib_BTC-USD_1d_20241217T000000 | **down** | 2024-12-17 | 2024-12-20 | 2025-03-20 | **49** |

---

## Outlier Notes

### High-event fibs (>= 45 interactions)

**Jan–Feb 2022 cluster (4 fibs, 52–65 events each):**
`20220105` (65), `20220215` (60), `20220120` (57), `20220124` (52).
All four are 4–5-day swings in the Jan–Feb 2022 chopfest before the LUNA/UST collapse. Price oscillated tightly between broken 2021-ATH levels, generating extreme interaction density across all six fib levels within the 90-day window. These fibs are an artifact of compressed-range volatility, not structurally distinct behavior.

**May 2017 down swing — `20170525` (54 events):**
2-day swing (2017-05-25 → 05-27) during the first major 2017 correction. Price re-tested the drop levels repeatedly through the summer rally to $3k. High density because the anchor range was narrow and the 4H revisited those prices many times.

**Dec 2017 up swing — `20171205` (51 events):**
3-day parabolic leg (2017-12-05 → 12-08, 0.382/0.5/0.618 in the $15k–$17k zone). The Q1 2018 bear market opened with repeated tests of these levels — accounting for the high interaction count during the 90-day window.

**Jun–Jul 2022 recovery bounces — `20220618` (45), `20220713` (50):**
BTC bottom range (Jun–Jul 2022, ~$19k–$24k). Both up swings in the dead-cat / accumulation range; price oscillated for months around these fib levels, concentrated within the 90-day window due to the range-bound environment.

**Apr/Dec 2024 down swings — `20240408` (48), `20241217` (49):**
Post-halving correction (Apr 2024) and end-of-year pullback (Dec 2024). Active market at higher prices with denser 4H participation.

---

### Low-event fibs (<= 5 interactions)

**`20201211` (2 events) — Dec 2020 bull breakout:**
9-day up swing (2020-12-11 → 12-20). The BTC breakout above the 2017 ATH was near-vertical. Within the 90-day window (through 2021-03-20), price barely retraced to this fib's levels — the 0.786 and 1.0 were already far below the market. Lowest event count in the dataset.

**`20170716` (3 events) — Jul–Sep 2017 parabolic up:**
47-day up swing during the alt-season rocket (Jul–Sep 2017 $2k → $4.5k). Price only returned to these levels much later; within 90 days it kept running.

**`20170915` (5 events), `20200416` (5 events):**
Both are very short-duration swings (2–3 days) in strongly trending markets (2017 bull, 2020 post-halving rally). Price did not retrace to these fib levels within 90 days of anchor_b.

---

## Notes

- **1H deferred:** 1H cache not fetched. Extend via `data.fetch --timeframes 1h` when ready.
- **Charts not generated:** Run `source_fib_projection_chart --source-fib <path> --chart-timeframes 4h` per fib for visual artifacts.
- **Review window is research-scoped:** The 90-day horizon is a methodological choice; it does not imply these fibs are inactive after 90 days. Use `--full-history` for unrestricted debugging.
- **Expansion config required:** Default `settings.yaml` cuts 4H at 2022-10-31 (`history_start`). The expansion config must be specified for any re-run.
