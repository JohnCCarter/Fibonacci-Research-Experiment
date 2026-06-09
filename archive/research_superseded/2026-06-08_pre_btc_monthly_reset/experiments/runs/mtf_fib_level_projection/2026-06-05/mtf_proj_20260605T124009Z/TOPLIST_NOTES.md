# Toplist notes — fib fingerprint × outcome (research triage)

Run: `mtf_proj_20260605T124009Z`

> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a
> signal, and not a strategy. No parameter tuning. Buckets with
> `n_events` < 5 are flagged `LOW SAMPLE`. Use this to decide
> *what to collect more data on*, not *what to trade*.

## Inventory

- Joined events: 5415
- Joined rows (event × horizon): 21660
- Candidate buckets: 384 (28 flagged LOW SAMPLE)
- Horizons: 5, 10, 20, 50
- Direction-inferred events per horizon (used for hints): h5=4583, h10=4583, h20=4583, h50=4583

## View 1 — candidate summary (top 1 per candidate × horizon)

Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).
`mean_post_bars_on_break_side` is the expected-side proxy.

| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |
|---|---|---|---|---|---|---|---|---|
| continuation_candidate | 5 | above | 1 | 15 | ok | 0.09126 | 0.01246 | 40.33 |
| continuation_candidate | 10 | above | 1 | 15 | ok | 0.1224 | 0.01271 | 40.33 |
| continuation_candidate | 20 | above | 1 | 15 | ok | 0.1525 | 0.01653 | 40.33 |
| continuation_candidate | 50 | above | 1 | 15 | ok | 0.2222 | 0.03759 | 40.33 |
| failure_candidate | 5 | cross | 0.618 | 92 | ok | 0.05989 | 0.01793 | 14.74 |
| failure_candidate | 10 | cross | 0.236 | 92 | ok | 0.09048 | 0.02424 | 13.71 |
| failure_candidate | 20 | cross | 0.236 | 92 | ok | 0.1147 | 0.03619 | 13.71 |
| failure_candidate | 50 | above | 0.236 | 3 | LOW SAMPLE | 0.2359 | 0.1827 | 26 |
| reaction_candidate | 5 | above | 0.786 | 13 | ok | 0.05387 | 0.05387 | 16.92 |
| reaction_candidate | 10 | above | 0.236 | 20 | ok | 0.07837 | 0.07837 | 23.15 |
| reaction_candidate | 20 | cross | 1 | 20 | ok | 0.1179 | 0.1179 | 29.8 |
| reaction_candidate | 50 | below | 1 | 21 | ok | 0.2022 | 0.2022 | 24.71 |
| rejection_candidate | 5 | cross | 0.236 | 22 | ok | 0.07001 | 0.008557 | 11.09 |
| rejection_candidate | 10 | cross | 0.236 | 22 | ok | 0.09455 | 0.01178 | 11.09 |
| rejection_candidate | 20 | cross | 0.236 | 22 | ok | 0.1293 | 0.02585 | 11.09 |
| rejection_candidate | 50 | above | 0.786 | 39 | ok | 0.1617 | 0.08566 | 10.36 |

## View 2 — fingerprint ↔ outcome hints (Spearman rho)

Direction-inferred events only; candidates pooled (coarse). Positive
rho vs `mfe` = field tends to be higher when favorable excursion is
higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,
not prediction.

| fingerprint field | mfe h5 | mfe h10 | mfe h20 | mfe h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.0279 | 0.0261 | 0.0306 | 0.0407 |
| pre_distance_atr_norm | 0.0719 | 0.029 | 0.0024 | 0.0323 |
| pre_approach_choppiness | -0.0777 | -0.0359 | -0.0028 | -0.0397 |
| at_wick_through_level | 0.2779 | 0.2651 | 0.21 | 0.1375 |
| at_close_distance_atr_norm | 0.0167 | 0.0433 | 0.0377 | 0.0457 |
| post_bars_on_break_side | -0.0177 | -0.0154 | -0.0649 | -0.0158 |
| post_retest_count | -0.1967 | -0.2967 | -0.4185 | -0.4298 |
| post_remained_near_level_rate | -0.1942 | -0.2862 | -0.4041 | -0.4086 |

| fingerprint field | mae h5 | mae h10 | mae h20 | mae h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.1288 | 0.1049 | 0.0567 | 0.0089 |
| pre_distance_atr_norm | 0.0794 | 0.052 | 0.0327 | 0.0349 |
| pre_approach_choppiness | -0.1022 | -0.068 | -0.0471 | -0.0383 |
| at_wick_through_level | 0.2578 | 0.2234 | 0.182 | 0.0873 |
| at_close_distance_atr_norm | 0.1303 | 0.0751 | 0.0395 | -0.0146 |
| post_bars_on_break_side | -0.0646 | -0.067 | -0.0234 | 0.0124 |
| post_retest_count | 0.1826 | 0.2725 | 0.3884 | 0.4701 |
| post_remained_near_level_rate | 0.1634 | 0.2361 | 0.3351 | 0.4013 |

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
