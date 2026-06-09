# Toplist notes — fib fingerprint × outcome (research triage)

Run: `mtf_proj_20260605T124444Z`

> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a
> signal, and not a strategy. No parameter tuning. Buckets with
> `n_events` < 5 are flagged `LOW SAMPLE`. Use this to decide
> *what to collect more data on*, not *what to trade*.

## Inventory

- Joined events: 617
- Joined rows (event × horizon): 2468
- Candidate buckets: 336 (192 flagged LOW SAMPLE)
- Horizons: 5, 10, 20, 50
- Direction-inferred events per horizon (used for hints): h5=512, h10=512, h20=512, h50=512

## View 1 — candidate summary (top 1 per candidate × horizon)

Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).
`mean_post_bars_on_break_side` is the expected-side proxy.

| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |
|---|---|---|---|---|---|---|---|---|
| continuation_candidate | 5 | below | 0.618 | 2 | LOW SAMPLE | 0.1034 | 0.005876 | 41 |
| continuation_candidate | 10 | below | 0.382 | 3 | LOW SAMPLE | 0.1326 | 0.008799 | 41.67 |
| continuation_candidate | 20 | below | 0.382 | 3 | LOW SAMPLE | 0.1401 | 0.008799 | 41.67 |
| continuation_candidate | 50 | above | 1 | 1 | LOW SAMPLE | 0.1742 | 0.00346 | 29 |
| failure_candidate | 5 | cross | 0.786 | 10 | ok | 0.04904 | 0.01694 | 10 |
| failure_candidate | 10 | cross | 1 | 9 | ok | 0.07128 | 0.03226 | 14 |
| failure_candidate | 20 | touch | 0.786 | 4 | LOW SAMPLE | 0.09161 | 0.05633 | 10.5 |
| failure_candidate | 50 | touch | 0.5 | 4 | LOW SAMPLE | 0.2327 | 0.06241 | 17.25 |
| reaction_candidate | 5 | below | 0.236 | 1 | LOW SAMPLE | 0.0413 | 0.0413 | 6 |
| reaction_candidate | 10 | below | 0.382 | 3 | LOW SAMPLE | 0.06062 | 0.06062 | 14 |
| reaction_candidate | 20 | below | 0.382 | 3 | LOW SAMPLE | 0.09218 | 0.09218 | 14 |
| reaction_candidate | 50 | below | 0.618 | 1 | LOW SAMPLE | 0.223 | 0.223 | 1 |
| rejection_candidate | 5 | cross | 0.618 | 2 | LOW SAMPLE | 0.08636 | 0.000507 | 0 |
| rejection_candidate | 10 | cross | 0.5 | 1 | LOW SAMPLE | 0.1521 | 0.01138 | 4 |
| rejection_candidate | 20 | cross | 0.5 | 1 | LOW SAMPLE | 0.1521 | 0.01138 | 4 |
| rejection_candidate | 50 | below | 0.786 | 3 | LOW SAMPLE | 0.2718 | 0.03473 | 5 |

## View 2 — fingerprint ↔ outcome hints (Spearman rho)

Direction-inferred events only; candidates pooled (coarse). Positive
rho vs `mfe` = field tends to be higher when favorable excursion is
higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,
not prediction.

| fingerprint field | mfe h5 | mfe h10 | mfe h20 | mfe h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.0536 | 0.0227 | 0.0472 | 0.0525 |
| pre_distance_atr_norm | 0.0776 | 0.0573 | -0.0064 | 0.0116 |
| pre_approach_choppiness | -0.0624 | -0.0451 | 0.0172 | 0.0003 |
| at_wick_through_level | -0.2573 | -0.2974 | -0.3023 | -0.2621 |
| at_close_distance_atr_norm | 0.0052 | 0.0005 | -0.001 | 0.0154 |
| post_bars_on_break_side | 0.0016 | -0.0533 | -0.1089 | -0.0674 |
| post_retest_count | -0.0737 | -0.1768 | -0.2668 | -0.3216 |
| post_remained_near_level_rate | -0.0581 | -0.1497 | -0.2347 | -0.2664 |

| fingerprint field | mae h5 | mae h10 | mae h20 | mae h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.0006 | 0.0008 | -0.0518 | -0.024 |
| pre_distance_atr_norm | 0.0057 | 0.0348 | 0.0023 | 0.0457 |
| pre_approach_choppiness | -0.0096 | -0.0288 | 0.0049 | -0.0436 |
| at_wick_through_level | -0.0902 | -0.1402 | -0.1649 | -0.1905 |
| at_close_distance_atr_norm | -0.0147 | -0.005 | -0.0618 | -0.009 |
| post_bars_on_break_side | -0.0572 | -0.1017 | 0.0017 | 0.0439 |
| post_retest_count | 0.1972 | 0.3092 | 0.434 | 0.4959 |
| post_remained_near_level_rate | 0.1899 | 0.2692 | 0.3774 | 0.4311 |

## Triage buckets (arbitrary cut-offs, not tuned)

Cut-offs on max |rho vs mfe| across horizons: watch ≥ 0.5 & sign-stable, weak ≥ 0.3, else noise-like.

- **Worth more data (watch):** none
- **Weak / unstable:** at_wick_through_level, post_retest_count
- **Low covariation (noise-like):** pre_bars_approaching_level, pre_distance_atr_norm, pre_approach_choppiness, at_close_distance_atr_norm, post_bars_on_break_side, post_remained_near_level_rate

## What to look at next (triage, not conclusions)

- Candidates whose buckets are all LOW SAMPLE need more events before
  any pattern is worth reading.
- `watch` fields are only candidates for *more data collection*, not
  evidence of edge.
- Recent (2026) fibs may have truncated long horizons (`bars_available`),
  so h20/h50 fill in as post-2022-10-31 history grows.
