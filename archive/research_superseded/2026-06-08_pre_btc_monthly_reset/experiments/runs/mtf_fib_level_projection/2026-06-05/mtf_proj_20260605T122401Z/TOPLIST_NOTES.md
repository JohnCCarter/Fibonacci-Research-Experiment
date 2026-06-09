# Toplist notes — fib fingerprint × outcome (research triage)

Run: `mtf_proj_20260605T122401Z`

> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a
> signal, and not a strategy. No parameter tuning. Buckets with
> `n_events` < 5 are flagged `LOW SAMPLE`. Use this to decide
> *what to collect more data on*, not *what to trade*.

## Inventory

- Joined events: 42
- Joined rows (event × horizon): 168
- Candidate buckets: 116 (116 flagged LOW SAMPLE)
- Horizons: 5, 10, 20, 50
- Direction-inferred events per horizon (used for hints): h5=35, h10=35, h20=35, h50=35

## View 1 — candidate summary (top 1 per candidate × horizon)

Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).
`mean_post_bars_on_break_side` is the expected-side proxy.

| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |
|---|---|---|---|---|---|---|---|---|
| continuation_candidate | 5 | touch | 0.236 | 1 | LOW SAMPLE | 0.1437 | 0.000142 | 99 |
| continuation_candidate | 10 | touch | 0.236 | 1 | LOW SAMPLE | 0.2865 | 0.000142 | 99 |
| continuation_candidate | 20 | touch | 0.236 | 1 | LOW SAMPLE | 0.2865 | 0.000142 | 99 |
| continuation_candidate | 50 | cross | 0.382 | 2 | LOW SAMPLE | 0.2927 | 0.02526 | 98.5 |
| failure_candidate | 5 | cross | 0.5 | 1 | LOW SAMPLE | 0.07269 | 0.02794 | 27 |
| failure_candidate | 10 | cross | 1 | 1 | LOW SAMPLE | 0.1215 | 0.006137 | 0 |
| failure_candidate | 20 | cross | 0.618 | 1 | LOW SAMPLE | 0.212 | 0.0272 | 4 |
| failure_candidate | 50 | cross | 0.618 | 1 | LOW SAMPLE | 0.3691 | 0.0272 | 4 |
| reaction_candidate | 5 | above | 1 | 1 | LOW SAMPLE | 0.08714 | 0.08714 | 96 |
| reaction_candidate | 10 | below | 0.382 | 1 | LOW SAMPLE | 0.1452 | 0.1452 | 95 |
| reaction_candidate | 20 | above | 1 | 1 | LOW SAMPLE | 0.1808 | 0.1808 | 96 |
| reaction_candidate | 50 | below | 0.382 | 1 | LOW SAMPLE | 0.3372 | 0.3372 | 95 |
| rejection_candidate | 5 | touch | 0.5 | 2 | LOW SAMPLE | 0.09237 | 0.005412 | 8.5 |
| rejection_candidate | 10 | touch | 0.5 | 2 | LOW SAMPLE | 0.1762 | 0.01011 | 8.5 |
| rejection_candidate | 20 | touch | 0.5 | 2 | LOW SAMPLE | 0.1762 | 0.03416 | 8.5 |
| rejection_candidate | 50 | touch | 0.5 | 2 | LOW SAMPLE | 0.3245 | 0.05212 | 8.5 |

## View 2 — fingerprint ↔ outcome hints (Spearman rho)

Direction-inferred events only; candidates pooled (coarse). Positive
rho vs `mfe` = field tends to be higher when favorable excursion is
higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,
not prediction.

| fingerprint field | mfe h5 | mfe h10 | mfe h20 | mfe h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | -0.0562 | 0.056 | 0.0657 | -0.0602 |
| pre_distance_atr_norm | -0.0252 | -0.2594 | -0.5045 | -0.4209 |
| pre_approach_choppiness | 0.0207 | 0.2339 | 0.4944 | 0.4534 |
| at_wick_through_level | -0.1384 | -0.1588 | -0.2871 | -0.4518 |
| at_close_distance_atr_norm | -0.1989 | -0.1479 | 0.0762 | 0.1546 |
| post_bars_on_break_side | -0.0194 | -0.0337 | 0.0186 | -0.1779 |
| post_retest_count | -0.1544 | -0.3613 | -0.635 | -0.4967 |
| post_remained_near_level_rate | -0.1842 | -0.3931 | -0.6736 | -0.4993 |

| fingerprint field | mae h5 | mae h10 | mae h20 | mae h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.0481 | 0.1025 | 0.1493 | -0.1452 |
| pre_distance_atr_norm | 0.0469 | -0.0447 | 0.0287 | 0.2646 |
| pre_approach_choppiness | -0.059 | 0.045 | -0.0492 | -0.2792 |
| at_wick_through_level | 0.3521 | 0.3818 | 0.3336 | 0.195 |
| at_close_distance_atr_norm | -0.0053 | 0 | -0.0756 | -0.0476 |
| post_bars_on_break_side | 0.0951 | 0.0555 | 0.0974 | 0.0525 |
| post_retest_count | 0.1927 | 0.234 | 0.4895 | 0.6212 |
| post_remained_near_level_rate | 0.0711 | 0.114 | 0.3668 | 0.5518 |

## Triage buckets (arbitrary cut-offs, not tuned)

Cut-offs on max |rho vs mfe| across horizons: watch ≥ 0.5 & sign-stable, weak ≥ 0.3, else noise-like.

- **Worth more data (watch):** pre_distance_atr_norm, post_retest_count, post_remained_near_level_rate
- **Weak / unstable:** pre_approach_choppiness, at_wick_through_level
- **Low covariation (noise-like):** pre_bars_approaching_level, at_close_distance_atr_norm, post_bars_on_break_side

## What to look at next (triage, not conclusions)

- Candidates whose buckets are all LOW SAMPLE need more events before
  any pattern is worth reading.
- `watch` fields are only candidates for *more data collection*, not
  evidence of edge.
- Recent (2026) fibs may have truncated long horizons (`bars_available`),
  so h20/h50 fill in as post-2022-10-31 history grows.
