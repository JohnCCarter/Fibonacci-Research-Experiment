# Toplist notes — fib fingerprint × outcome (research triage)

Run: `mtf_proj_20260605T123413Z`

> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a
> signal, and not a strategy. No parameter tuning. Buckets with
> `n_events` < 5 are flagged `LOW SAMPLE`. Use this to decide
> *what to collect more data on*, not *what to trade*.

## Inventory

- Joined events: 23
- Joined rows (event × horizon): 92
- Candidate buckets: 60 (60 flagged LOW SAMPLE)
- Horizons: 5, 10, 20, 50
- Direction-inferred events per horizon (used for hints): h5=18, h10=18, h20=18, h50=18

## View 1 — candidate summary (top 1 per candidate × horizon)

Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).
`mean_post_bars_on_break_side` is the expected-side proxy.

| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |
|---|---|---|---|---|---|---|---|---|
| continuation_candidate | 5 | touch | 0.5 | 1 | LOW SAMPLE | 0.0677 | 0.001579 | 21 |
| continuation_candidate | 10 | cross | 0.236 | 1 | LOW SAMPLE | 0.08923 | 0.01251 | 18 |
| continuation_candidate | 20 | touch | 0.618 | 1 | LOW SAMPLE | 0.1434 | 0.001746 | 21 |
| continuation_candidate | 50 | touch | 0.618 | 1 | LOW SAMPLE | 0.1464 | 0.001746 | 21 |
| failure_candidate | 5 | cross | 0.786 | 1 | LOW SAMPLE | 0.01679 | 0.01344 | 81 |
| failure_candidate | 10 | cross | 0.786 | 1 | LOW SAMPLE | 0.02008 | 0.01344 | 81 |
| failure_candidate | 20 | cross | 0.786 | 1 | LOW SAMPLE | 0.02008 | 0.02272 | 81 |
| failure_candidate | 50 | cross | 0.786 | 1 | LOW SAMPLE | 0.02008 | 0.05807 | 81 |
| reaction_candidate | 5 | touch | 1 | 3 | LOW SAMPLE | 0.01397 | 0.01397 | 45.67 |
| reaction_candidate | 10 | touch | 0.618 | 2 | LOW SAMPLE | 0.0417 | 0.0417 | 2 |
| reaction_candidate | 20 | touch | 0.618 | 2 | LOW SAMPLE | 0.05427 | 0.05427 | 2 |
| reaction_candidate | 50 | touch | 1 | 3 | LOW SAMPLE | 0.1439 | 0.1439 | 45.67 |
| rejection_candidate | 5 | touch | 1 | 2 | LOW SAMPLE | 0.0143 | 0.01132 | 75 |
| rejection_candidate | 10 | touch | 1 | 2 | LOW SAMPLE | 0.01594 | 0.01966 | 75 |
| rejection_candidate | 20 | touch | 1 | 2 | LOW SAMPLE | 0.01594 | 0.02907 | 75 |
| rejection_candidate | 50 | touch | 1 | 2 | LOW SAMPLE | 0.01594 | 0.06254 | 75 |

## View 2 — fingerprint ↔ outcome hints (Spearman rho)

Direction-inferred events only; candidates pooled (coarse). Positive
rho vs `mfe` = field tends to be higher when favorable excursion is
higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,
not prediction.

| fingerprint field | mfe h5 | mfe h10 | mfe h20 | mfe h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.0123 | 0.1888 | 0.1407 | 0.1024 |
| pre_distance_atr_norm | 0.6116 | 0.6325 | 0.5803 | 0.5301 |
| pre_approach_choppiness | -0.5614 | -0.5886 | -0.5468 | -0.4966 |
| at_wick_through_level | -0.5535 | -0.4956 | -0.6777 | -0.7046 |
| at_close_distance_atr_norm | -0.3176 | -0.2556 | -0.0983 | -0.1335 |
| post_bars_on_break_side | -0.3779 | -0.506 | -0.2821 | -0.2738 |
| post_retest_count | -0.3067 | -0.3391 | -0.4553 | -0.3841 |
| post_remained_near_level_rate | -0.2538 | -0.3089 | -0.365 | -0.3152 |

| fingerprint field | mae h5 | mae h10 | mae h20 | mae h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | -0.1234 | -0.0703 | -0.0494 | -0.0494 |
| pre_distance_atr_norm | -0.7643 | -0.5259 | -0.4841 | -0.5175 |
| pre_approach_choppiness | 0.7873 | 0.4799 | 0.4255 | 0.4673 |
| at_wick_through_level | 0.5763 | 0.5142 | 0.4377 | 0.4956 |
| at_close_distance_atr_norm | 0.4087 | 0.1852 | -0.0693 | -0.061 |
| post_bars_on_break_side | 0.4498 | 0.2103 | 0.0968 | 0.0885 |
| post_retest_count | 0.1068 | 0.3307 | 0.5683 | 0.5851 |
| post_remained_near_level_rate | 0.0048 | 0.1881 | 0.4 | 0.4053 |

## Triage buckets (arbitrary cut-offs, not tuned)

Cut-offs on max |rho vs mfe| across horizons: watch ≥ 0.5 & sign-stable, weak ≥ 0.3, else noise-like.

- **Worth more data (watch):** pre_distance_atr_norm, pre_approach_choppiness, at_wick_through_level, post_bars_on_break_side
- **Weak / unstable:** at_close_distance_atr_norm, post_retest_count, post_remained_near_level_rate
- **Low covariation (noise-like):** pre_bars_approaching_level

## What to look at next (triage, not conclusions)

- Candidates whose buckets are all LOW SAMPLE need more events before
  any pattern is worth reading.
- `watch` fields are only candidates for *more data collection*, not
  evidence of edge.
- Recent (2026) fibs may have truncated long horizons (`bars_available`),
  so h20/h50 fill in as post-2022-10-31 history grows.
