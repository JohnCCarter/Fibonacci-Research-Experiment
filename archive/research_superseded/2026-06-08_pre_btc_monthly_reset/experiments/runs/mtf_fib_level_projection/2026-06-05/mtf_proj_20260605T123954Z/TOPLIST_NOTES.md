# Toplist notes — fib fingerprint × outcome (research triage)

Run: `mtf_proj_20260605T123954Z`

> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a
> signal, and not a strategy. No parameter tuning. Buckets with
> `n_events` < 5 are flagged `LOW SAMPLE`. Use this to decide
> *what to collect more data on*, not *what to trade*.

## Inventory

- Joined events: 107
- Joined rows (event × horizon): 428
- Candidate buckets: 184 (160 flagged LOW SAMPLE)
- Horizons: 5, 10, 20, 50
- Direction-inferred events per horizon (used for hints): h5=85, h10=85, h20=85, h50=85

## View 1 — candidate summary (top 1 per candidate × horizon)

Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).
`mean_post_bars_on_break_side` is the expected-side proxy.

| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |
|---|---|---|---|---|---|---|---|---|
| continuation_candidate | 5 | above | 0.382 | 1 | LOW SAMPLE | 0.06747 | 0.000799 | 20 |
| continuation_candidate | 10 | above | 0.382 | 1 | LOW SAMPLE | 0.08724 | 0.000799 | 20 |
| continuation_candidate | 20 | above | 0.382 | 1 | LOW SAMPLE | 0.1287 | 0.000799 | 20 |
| continuation_candidate | 50 | above | 1 | 1 | LOW SAMPLE | 0.1742 | 0.00346 | 29 |
| failure_candidate | 5 | cross | 1 | 1 | LOW SAMPLE | 0.03782 | 0.003739 | 24 |
| failure_candidate | 10 | cross | 1 | 1 | LOW SAMPLE | 0.03991 | 0.003739 | 24 |
| failure_candidate | 20 | cross | 0.236 | 2 | LOW SAMPLE | 0.05485 | 0.008081 | 15.5 |
| failure_candidate | 50 | touch | 0.618 | 1 | LOW SAMPLE | 0.09077 | 0.01275 | 2 |
| reaction_candidate | 5 | above | 0.236 | 2 | LOW SAMPLE | 0.0199 | 0.0199 | 4.5 |
| reaction_candidate | 10 | touch | 0.618 | 2 | LOW SAMPLE | 0.0417 | 0.0417 | 2 |
| reaction_candidate | 20 | touch | 0.618 | 2 | LOW SAMPLE | 0.05427 | 0.05427 | 2 |
| reaction_candidate | 50 | below | 0.5 | 1 | LOW SAMPLE | 0.1689 | 0.1689 | 0 |
| rejection_candidate | 5 | touch | 0.5 | 2 | LOW SAMPLE | 0.02695 | 0.0033 | 11 |
| rejection_candidate | 10 | touch | 0.5 | 2 | LOW SAMPLE | 0.04494 | 0.0033 | 11 |
| rejection_candidate | 20 | below | 0.5 | 1 | LOW SAMPLE | 0.06639 | 0.005702 | 0 |
| rejection_candidate | 50 | below | 0.5 | 1 | LOW SAMPLE | 0.1486 | 0.005702 | 0 |

## View 2 — fingerprint ↔ outcome hints (Spearman rho)

Direction-inferred events only; candidates pooled (coarse). Positive
rho vs `mfe` = field tends to be higher when favorable excursion is
higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,
not prediction.

| fingerprint field | mfe h5 | mfe h10 | mfe h20 | mfe h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.0831 | 0.1362 | 0.0969 | 0.1738 |
| pre_distance_atr_norm | -0.1428 | -0.0173 | -0.0205 | 0.1271 |
| pre_approach_choppiness | 0.0095 | -0.0526 | -0.0113 | -0.1477 |
| at_wick_through_level | -0.0792 | -0.0338 | -0.0907 | -0.0695 |
| at_close_distance_atr_norm | 0.1437 | 0.2184 | 0.224 | 0.2485 |
| post_bars_on_break_side | 0.1627 | -0.0288 | -0.135 | 0.1462 |
| post_retest_count | -0.3561 | -0.5608 | -0.6584 | -0.5485 |
| post_remained_near_level_rate | -0.3181 | -0.4836 | -0.5583 | -0.454 |

| fingerprint field | mae h5 | mae h10 | mae h20 | mae h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | -0.185 | -0.0407 | -0.1879 | -0.196 |
| pre_distance_atr_norm | -0.0089 | -0.0856 | -0.1438 | -0.0704 |
| pre_approach_choppiness | -0.0412 | 0.0412 | 0.1265 | 0.0569 |
| at_wick_through_level | 0.1595 | 0.128 | 0.073 | -0.0013 |
| at_close_distance_atr_norm | 0.1048 | 0.031 | -0.1918 | -0.2046 |
| post_bars_on_break_side | 0.1144 | 0.0619 | 0.08 | -0.0257 |
| post_retest_count | 0.1738 | 0.3328 | 0.504 | 0.5616 |
| post_remained_near_level_rate | 0.1332 | 0.2609 | 0.3948 | 0.4554 |

## Triage buckets (arbitrary cut-offs, not tuned)

Cut-offs on max |rho vs mfe| across horizons: watch ≥ 0.5 & sign-stable, weak ≥ 0.3, else noise-like.

- **Worth more data (watch):** post_retest_count, post_remained_near_level_rate
- **Weak / unstable:** none
- **Low covariation (noise-like):** pre_bars_approaching_level, pre_distance_atr_norm, pre_approach_choppiness, at_wick_through_level, at_close_distance_atr_norm, post_bars_on_break_side

## What to look at next (triage, not conclusions)

- Candidates whose buckets are all LOW SAMPLE need more events before
  any pattern is worth reading.
- `watch` fields are only candidates for *more data collection*, not
  evidence of edge.
- Recent (2026) fibs may have truncated long horizons (`bars_available`),
  so h20/h50 fill in as post-2022-10-31 history grows.
