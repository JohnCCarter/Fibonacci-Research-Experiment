# Toplist notes — fib fingerprint × outcome (research triage)

Run: `fp_outcomes_20260605T114206Z`

> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a
> signal, and not a strategy. No parameter tuning. Buckets with
> `n_events` < 5 are flagged `LOW SAMPLE`. Use this to decide
> *what to collect more data on*, not *what to trade*.

## Inventory

- Joined events: 51
- Joined rows (event × horizon): 204
- Candidate buckets: 148 (148 flagged LOW SAMPLE)
- Horizons: 5, 10, 20, 50
- Direction-inferred events per horizon (used for hints): h5=40, h10=40, h20=40, h50=40

## View 1 — candidate summary (top 1 per candidate × horizon)

Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).
`mean_post_bars_on_break_side` is the expected-side proxy.

| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |
|---|---|---|---|---|---|---|---|---|
| continuation_candidate | 5 | cross | 0.786 | 3 | LOW SAMPLE | 0.1133 | 0.000473 | 5.667 |
| continuation_candidate | 10 | cross | 1 | 2 | LOW SAMPLE | 0.1749 | 0.005883 | 7.5 |
| continuation_candidate | 20 | touch | 0.786 | 1 | LOW SAMPLE | 0.2044 | 0.01734 | 10 |
| continuation_candidate | 50 | cross | 0.236 | 2 | LOW SAMPLE | 0.2269 | 0.01869 | 23 |
| failure_candidate | 5 | cross | 0.5 | 1 | LOW SAMPLE | 0.07699 | 0.001125 | 9 |
| failure_candidate | 10 | cross | 0.786 | 1 | LOW SAMPLE | 0.1023 | 0.008809 | 1 |
| failure_candidate | 20 | cross | 0.5 | 1 | LOW SAMPLE | 0.1222 | 0.001125 | 9 |
| failure_candidate | 50 | cross | 0.786 | 1 | LOW SAMPLE | 0.1655 | 0.008809 | 1 |
| reaction_candidate | 5 | above | 1 | 1 | LOW SAMPLE | 0.1443 | 0.1443 | 4 |
| reaction_candidate | 10 | above | 1 | 1 | LOW SAMPLE | 0.1443 | 0.1443 | 4 |
| reaction_candidate | 20 | above | 0.5 | 1 | LOW SAMPLE | 0.2109 | 0.2109 | 12 |
| reaction_candidate | 50 | touch | 0.382 | 1 | LOW SAMPLE | 0.2198 | 0.2198 | 19 |
| rejection_candidate | 5 | cross | 0.236 | 1 | LOW SAMPLE | 0.1706 | 0.005316 | 0 |
| rejection_candidate | 10 | below | 0.236 | 1 | LOW SAMPLE | 0.2077 | 0.009666 | 0 |
| rejection_candidate | 20 | touch | 0.236 | 1 | LOW SAMPLE | 0.2119 | 0.007856 | 0 |
| rejection_candidate | 50 | touch | 0.236 | 1 | LOW SAMPLE | 0.2119 | 0.007856 | 0 |

## View 2 — fingerprint ↔ outcome hints (Spearman rho)

Direction-inferred events only; candidates pooled (coarse). Positive
rho vs `mfe` = field tends to be higher when favorable excursion is
higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,
not prediction.

| fingerprint field | mfe h5 | mfe h10 | mfe h20 | mfe h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.3029 | 0.3911 | 0.3421 | 0.0064 |
| pre_distance_atr_norm | 0.4162 | 0.0676 | -0.4972 | -0.4971 |
| pre_approach_choppiness | -0.4025 | -0.0678 | 0.4707 | 0.4653 |
| at_wick_through_level | 0.1082 | -0.1837 | -0.4097 | -0.4506 |
| at_close_distance_atr_norm | 0.185 | 0.0246 | -0.2739 | -0.1939 |
| post_bars_on_break_side | -0.6699 | -0.6063 | -0.2538 | 0.1614 |
| post_retest_count | -0.4402 | -0.6263 | -0.3642 | -0.0598 |
| post_remained_near_level_rate | -0.2527 | -0.375 | -0.0891 | 0.0339 |

| fingerprint field | mae h5 | mae h10 | mae h20 | mae h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | -0.2406 | -0.2768 | -0.3051 | -0.4103 |
| pre_distance_atr_norm | -0.0986 | -0.1042 | -0.0625 | 0.1559 |
| pre_approach_choppiness | 0.0675 | 0.0816 | 0.0458 | -0.1431 |
| at_wick_through_level | 0.1101 | 0.1093 | 0.0708 | 0.3355 |
| at_close_distance_atr_norm | 0.2284 | 0.186 | 0.1522 | 0.1347 |
| post_bars_on_break_side | 0.3333 | 0.3803 | 0.4037 | 0.4023 |
| post_retest_count | 0.4161 | 0.443 | 0.469 | 0.6018 |
| post_remained_near_level_rate | 0.3397 | 0.3321 | 0.3574 | 0.3872 |

## Triage buckets (arbitrary cut-offs, not tuned)

Cut-offs on max |rho vs mfe| across horizons: watch ≥ 0.5 & sign-stable, weak ≥ 0.3, else noise-like.

- **Worth more data (watch):** post_retest_count
- **Weak / unstable:** pre_bars_approaching_level, pre_distance_atr_norm, pre_approach_choppiness, at_wick_through_level, post_bars_on_break_side, post_remained_near_level_rate
- **Low covariation (noise-like):** at_close_distance_atr_norm

## What to look at next (triage, not conclusions)

- Candidates whose buckets are all LOW SAMPLE need more events before
  any pattern is worth reading.
- `watch` fields are only candidates for *more data collection*, not
  evidence of edge.
- Recent (2026) fibs may have truncated long horizons (`bars_available`),
  so h20/h50 fill in as post-2022-10-31 history grows.
