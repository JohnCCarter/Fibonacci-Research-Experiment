# Toplist notes — fib fingerprint × outcome (research triage)

Run: `mtf_proj_20260605T123951Z`

> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a
> signal, and not a strategy. No parameter tuning. Buckets with
> `n_events` < 5 are flagged `LOW SAMPLE`. Use this to decide
> *what to collect more data on*, not *what to trade*.

## Inventory

- Joined events: 507
- Joined rows (event × horizon): 2028
- Candidate buckets: 300 (156 flagged LOW SAMPLE)
- Horizons: 5, 10, 20, 50
- Direction-inferred events per horizon (used for hints): h5=423, h10=423, h20=423, h50=423

## View 1 — candidate summary (top 1 per candidate × horizon)

Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).
`mean_post_bars_on_break_side` is the expected-side proxy.

| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |
|---|---|---|---|---|---|---|---|---|
| continuation_candidate | 5 | above | 0.786 | 2 | LOW SAMPLE | 0.1004 | 0.007182 | 16.5 |
| continuation_candidate | 10 | above | 0.786 | 2 | LOW SAMPLE | 0.1199 | 0.007182 | 16.5 |
| continuation_candidate | 20 | above | 0.786 | 2 | LOW SAMPLE | 0.1199 | 0.007182 | 16.5 |
| continuation_candidate | 50 | touch | 0.618 | 4 | LOW SAMPLE | 0.1241 | 0.01595 | 36 |
| failure_candidate | 5 | cross | 0.786 | 8 | ok | 0.05128 | 0.01673 | 6.625 |
| failure_candidate | 10 | cross | 0.786 | 8 | ok | 0.07419 | 0.01789 | 6.625 |
| failure_candidate | 20 | above | 0.786 | 1 | LOW SAMPLE | 0.1217 | 0.01596 | 2 |
| failure_candidate | 50 | above | 0.786 | 1 | LOW SAMPLE | 0.1388 | 0.01596 | 2 |
| reaction_candidate | 5 | below | 1 | 3 | LOW SAMPLE | 0.04376 | 0.04376 | 23 |
| reaction_candidate | 10 | below | 0.382 | 1 | LOW SAMPLE | 0.121 | 0.121 | 27 |
| reaction_candidate | 20 | below | 0.618 | 2 | LOW SAMPLE | 0.1253 | 0.1253 | 43 |
| reaction_candidate | 50 | below | 0.618 | 2 | LOW SAMPLE | 0.1497 | 0.1497 | 43 |
| rejection_candidate | 5 | cross | 0.618 | 2 | LOW SAMPLE | 0.08636 | 0.000507 | 0 |
| rejection_candidate | 10 | cross | 0.618 | 2 | LOW SAMPLE | 0.08659 | 0.000507 | 0 |
| rejection_candidate | 20 | cross | 0.618 | 2 | LOW SAMPLE | 0.09092 | 0.000507 | 0 |
| rejection_candidate | 50 | below | 0.5 | 3 | LOW SAMPLE | 0.1242 | 0.04285 | 5.333 |

## View 2 — fingerprint ↔ outcome hints (Spearman rho)

Direction-inferred events only; candidates pooled (coarse). Positive
rho vs `mfe` = field tends to be higher when favorable excursion is
higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,
not prediction.

| fingerprint field | mfe h5 | mfe h10 | mfe h20 | mfe h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.06 | 0.0551 | 0.0728 | 0.0411 |
| pre_distance_atr_norm | 0.1371 | 0.1263 | 0.1039 | 0.068 |
| pre_approach_choppiness | -0.1376 | -0.1332 | -0.1038 | -0.073 |
| at_wick_through_level | 0.2715 | 0.2332 | 0.1859 | 0.1164 |
| at_close_distance_atr_norm | 0.1018 | 0.111 | 0.1038 | 0.0828 |
| post_bars_on_break_side | 0.09 | 0.0309 | -0.043 | -0.0724 |
| post_retest_count | -0.1746 | -0.3041 | -0.4018 | -0.4105 |
| post_remained_near_level_rate | -0.1794 | -0.2978 | -0.3763 | -0.3828 |

| fingerprint field | mae h5 | mae h10 | mae h20 | mae h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | -0.0259 | -0.0199 | -0.0326 | -0.0264 |
| pre_distance_atr_norm | 0.0654 | 0.0233 | 0.018 | -0.0366 |
| pre_approach_choppiness | -0.0658 | -0.0331 | -0.0224 | 0.0384 |
| at_wick_through_level | 0.1878 | 0.1438 | 0.1437 | 0.1118 |
| at_close_distance_atr_norm | -0.0351 | -0.0298 | -0.0616 | 0.0048 |
| post_bars_on_break_side | -0.0503 | 0.0027 | 0.0827 | 0.0946 |
| post_retest_count | 0.2119 | 0.3457 | 0.469 | 0.4884 |
| post_remained_near_level_rate | 0.2006 | 0.2872 | 0.3883 | 0.4101 |

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
