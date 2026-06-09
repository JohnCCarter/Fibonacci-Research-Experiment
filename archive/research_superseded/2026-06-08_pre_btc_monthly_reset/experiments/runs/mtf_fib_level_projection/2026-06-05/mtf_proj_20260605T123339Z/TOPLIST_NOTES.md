# Toplist notes — fib fingerprint × outcome (research triage)

Run: `mtf_proj_20260605T123339Z`

> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a
> signal, and not a strategy. No parameter tuning. Buckets with
> `n_events` < 5 are flagged `LOW SAMPLE`. Use this to decide
> *what to collect more data on*, not *what to trade*.

## Inventory

- Joined events: 87
- Joined rows (event × horizon): 348
- Candidate buckets: 184 (168 flagged LOW SAMPLE)
- Horizons: 5, 10, 20, 50
- Direction-inferred events per horizon (used for hints): h5=72, h10=72, h20=72, h50=72

## View 1 — candidate summary (top 1 per candidate × horizon)

Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).
`mean_post_bars_on_break_side` is the expected-side proxy.

| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |
|---|---|---|---|---|---|---|---|---|
| continuation_candidate | 5 | above | 0.236 | 1 | LOW SAMPLE | 0.09718 | -1.2e-05 | 27 |
| continuation_candidate | 10 | above | 0.236 | 1 | LOW SAMPLE | 0.09718 | -1.2e-05 | 27 |
| continuation_candidate | 20 | cross | 0.236 | 1 | LOW SAMPLE | 0.1018 | 0.01062 | 100 |
| continuation_candidate | 50 | cross | 0.236 | 1 | LOW SAMPLE | 0.2611 | 0.01062 | 100 |
| failure_candidate | 5 | cross | 0.5 | 2 | LOW SAMPLE | 0.03266 | 0.008622 | 57.5 |
| failure_candidate | 10 | cross | 0.786 | 1 | LOW SAMPLE | 0.0701 | 0.006781 | 1 |
| failure_candidate | 20 | cross | 0.786 | 1 | LOW SAMPLE | 0.08945 | 0.006781 | 1 |
| failure_candidate | 50 | cross | 0.786 | 1 | LOW SAMPLE | 0.0961 | 0.006781 | 1 |
| reaction_candidate | 5 | touch | 0.382 | 2 | LOW SAMPLE | 0.02377 | 0.02377 | 2 |
| reaction_candidate | 10 | cross | 0.618 | 2 | LOW SAMPLE | 0.04273 | 0.04273 | 49 |
| reaction_candidate | 20 | touch | 0.5 | 2 | LOW SAMPLE | 0.06623 | 0.06623 | 70 |
| reaction_candidate | 50 | cross | 0.618 | 2 | LOW SAMPLE | 0.124 | 0.124 | 49 |
| rejection_candidate | 5 | cross | 1 | 1 | LOW SAMPLE | 0.04153 | 0.006013 | 55 |
| rejection_candidate | 10 | below | 0.5 | 1 | LOW SAMPLE | 0.09309 | 0.01251 | 0 |
| rejection_candidate | 20 | below | 0.5 | 1 | LOW SAMPLE | 0.1537 | 0.01251 | 0 |
| rejection_candidate | 50 | below | 0.5 | 1 | LOW SAMPLE | 0.3033 | 0.01251 | 0 |

## View 2 — fingerprint ↔ outcome hints (Spearman rho)

Direction-inferred events only; candidates pooled (coarse). Positive
rho vs `mfe` = field tends to be higher when favorable excursion is
higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,
not prediction.

| fingerprint field | mfe h5 | mfe h10 | mfe h20 | mfe h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | -0.011 | -0.0336 | -0.0504 | -0.1222 |
| pre_distance_atr_norm | 0.0256 | 0.0596 | 0.141 | 0.1015 |
| pre_approach_choppiness | -0.0473 | -0.0313 | -0.1044 | -0.0767 |
| at_wick_through_level | 0.2382 | 0.0162 | 0.012 | 0.02 |
| at_close_distance_atr_norm | -0.0233 | -0.1151 | -0.0541 | 0.1361 |
| post_bars_on_break_side | 0.3029 | 0.2744 | 0.0238 | -0.1936 |
| post_retest_count | 0.0463 | -0.0368 | -0.2419 | -0.4115 |
| post_remained_near_level_rate | 0.1003 | -0.0206 | -0.2493 | -0.362 |

| fingerprint field | mae h5 | mae h10 | mae h20 | mae h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.1926 | 0.1939 | -0.0227 | 0.0119 |
| pre_distance_atr_norm | 0.021 | 0.0802 | -0.0418 | 0.1338 |
| pre_approach_choppiness | -0.0148 | -0.0722 | 0.0268 | -0.1482 |
| at_wick_through_level | 0.3443 | 0.3863 | 0.3653 | 0.3043 |
| at_close_distance_atr_norm | 0.1531 | 0.1622 | -0.0332 | -0.0129 |
| post_bars_on_break_side | -0.0497 | -0.1121 | -0.0373 | 0.1228 |
| post_retest_count | 0.0978 | 0.1236 | 0.3912 | 0.5252 |
| post_remained_near_level_rate | 0.0637 | 0.0501 | 0.2854 | 0.4476 |

## Triage buckets (arbitrary cut-offs, not tuned)

Cut-offs on max |rho vs mfe| across horizons: watch ≥ 0.5 & sign-stable, weak ≥ 0.3, else noise-like.

- **Worth more data (watch):** none
- **Weak / unstable:** post_bars_on_break_side, post_retest_count, post_remained_near_level_rate
- **Low covariation (noise-like):** pre_bars_approaching_level, pre_distance_atr_norm, pre_approach_choppiness, at_wick_through_level, at_close_distance_atr_norm

## What to look at next (triage, not conclusions)

- Candidates whose buckets are all LOW SAMPLE need more events before
  any pattern is worth reading.
- `watch` fields are only candidates for *more data collection*, not
  evidence of edge.
- Recent (2026) fibs may have truncated long horizons (`bars_available`),
  so h20/h50 fill in as post-2022-10-31 history grows.
