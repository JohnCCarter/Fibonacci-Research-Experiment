# Toplist notes — fib fingerprint × outcome (research triage)

Run: `fp_outcomes_20260605T115819Z`

> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a
> signal, and not a strategy. No parameter tuning. Buckets with
> `n_events` < 5 are flagged `LOW SAMPLE`. Use this to decide
> *what to collect more data on*, not *what to trade*.

## Inventory

- Joined events: 1148
- Joined rows (event × horizon): 4592
- Candidate buckets: 360 (120 flagged LOW SAMPLE)
- Horizons: 5, 10, 20, 50
- Direction-inferred events per horizon (used for hints): h5=954, h10=954, h20=954, h50=954

## View 1 — candidate summary (top 1 per candidate × horizon)

Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).
`mean_post_bars_on_break_side` is the expected-side proxy.

| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |
|---|---|---|---|---|---|---|---|---|
| continuation_candidate | 5 | above | 0.786 | 1 | LOW SAMPLE | 0.4536 | 0.003961 | 50 |
| continuation_candidate | 10 | above | 0.786 | 1 | LOW SAMPLE | 0.4536 | 0.003961 | 50 |
| continuation_candidate | 20 | below | 1 | 2 | LOW SAMPLE | 0.468 | 0.03054 | 38 |
| continuation_candidate | 50 | below | 1 | 2 | LOW SAMPLE | 1.121 | 0.1122 | 38 |
| failure_candidate | 5 | cross | 1 | 15 | ok | 0.1968 | 0.06492 | 14 |
| failure_candidate | 10 | below | 1 | 1 | LOW SAMPLE | 0.2805 | 0.06191 | 3 |
| failure_candidate | 20 | touch | 0.786 | 2 | LOW SAMPLE | 0.4685 | 0.1336 | 3 |
| failure_candidate | 50 | touch | 0.786 | 2 | LOW SAMPLE | 0.5348 | 0.1336 | 3 |
| reaction_candidate | 5 | above | 1 | 6 | ok | 0.1741 | 0.1741 | 19.33 |
| reaction_candidate | 10 | cross | 0.786 | 2 | LOW SAMPLE | 0.2505 | 0.2505 | 28 |
| reaction_candidate | 20 | below | 0.786 | 3 | LOW SAMPLE | 0.4418 | 0.4418 | 23.33 |
| reaction_candidate | 50 | below | 1 | 2 | LOW SAMPLE | 1.075 | 1.075 | 29.5 |
| rejection_candidate | 5 | above | 0.618 | 9 | ok | 0.2334 | 0.06048 | 6.444 |
| rejection_candidate | 10 | above | 0.618 | 9 | ok | 0.3359 | 0.06048 | 6.444 |
| rejection_candidate | 20 | above | 0.618 | 9 | ok | 0.4798 | 0.09532 | 6.444 |
| rejection_candidate | 50 | cross | 0.618 | 7 | ok | 0.7922 | 0.1555 | 7.429 |

## View 2 — fingerprint ↔ outcome hints (Spearman rho)

Direction-inferred events only; candidates pooled (coarse). Positive
rho vs `mfe` = field tends to be higher when favorable excursion is
higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,
not prediction.

| fingerprint field | mfe h5 | mfe h10 | mfe h20 | mfe h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.162 | 0.1487 | 0.0638 | 0.0774 |
| pre_distance_atr_norm | 0.0719 | -0.0331 | -0.0094 | -0.0508 |
| pre_approach_choppiness | -0.0724 | 0.0084 | -0.0315 | 0.0139 |
| at_wick_through_level | 0.0665 | 0.0087 | -0.0045 | -0.0877 |
| at_close_distance_atr_norm | 0.0356 | 0.027 | 0.0104 | -0.013 |
| post_bars_on_break_side | 0.1361 | 0.1442 | 0.0498 | -0.0259 |
| post_retest_count | -0.1886 | -0.3279 | -0.3511 | -0.4202 |
| post_remained_near_level_rate | -0.2078 | -0.3383 | -0.3728 | -0.4516 |

| fingerprint field | mae h5 | mae h10 | mae h20 | mae h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.0783 | -0.008 | -0.0116 | -0.0157 |
| pre_distance_atr_norm | 0.1107 | 0.1908 | 0.0994 | 0.0752 |
| pre_approach_choppiness | -0.1163 | -0.1883 | -0.0802 | -0.0886 |
| at_wick_through_level | 0.1435 | 0.0775 | 0.0452 | -0.0281 |
| at_close_distance_atr_norm | 0.0899 | 0.0268 | 0.0084 | 0.0654 |
| post_bars_on_break_side | -0.0205 | -0.0444 | 0.0286 | 0.0549 |
| post_retest_count | 0.2588 | 0.3927 | 0.449 | 0.5713 |
| post_remained_near_level_rate | 0.1931 | 0.3302 | 0.3894 | 0.5176 |

## Triage buckets (arbitrary cut-offs, not tuned)

Cut-offs on max |rho vs mfe| across horizons: watch ≥ 0.5 & sign-stable, weak ≥ 0.3, else noise-like.

- **Worth more data (watch):** none
- **Weak / unstable:** post_retest_count, post_remained_near_level_rate
- **Low covariation (noise-like):** pre_bars_approaching_level, pre_distance_atr_norm, pre_approach_choppiness, at_wick_through_level, at_close_distance_atr_norm, post_bars_on_break_side

## What to look at next (triage, not conclusions)

- Candidates whose buckets are all LOW SAMPLE need more events before
  any pattern is worth reading.
- `watch` fields are only candidates for *more data collection*, not
  evidence of edge.
- Recent (2026) fibs may have truncated long horizons (`bars_available`),
  so h20/h50 fill in as post-2022-10-31 history grows.
