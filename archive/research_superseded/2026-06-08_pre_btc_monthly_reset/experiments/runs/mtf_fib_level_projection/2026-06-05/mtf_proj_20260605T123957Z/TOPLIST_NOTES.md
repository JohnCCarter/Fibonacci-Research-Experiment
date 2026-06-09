# Toplist notes — fib fingerprint × outcome (research triage)

Run: `mtf_proj_20260605T123957Z`

> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a
> signal, and not a strategy. No parameter tuning. Buckets with
> `n_events` < 5 are flagged `LOW SAMPLE`. Use this to decide
> *what to collect more data on*, not *what to trade*.

## Inventory

- Joined events: 667
- Joined rows (event × horizon): 2668
- Candidate buckets: 316 (152 flagged LOW SAMPLE)
- Horizons: 5, 10, 20, 50
- Direction-inferred events per horizon (used for hints): h5=571, h10=571, h20=571, h50=571

## View 1 — candidate summary (top 1 per candidate × horizon)

Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).
`mean_post_bars_on_break_side` is the expected-side proxy.

| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |
|---|---|---|---|---|---|---|---|---|
| continuation_candidate | 5 | above | 0.5 | 3 | LOW SAMPLE | 0.08985 | 0.002946 | 44.33 |
| continuation_candidate | 10 | touch | 0.786 | 6 | ok | 0.1061 | 0.009381 | 37.67 |
| continuation_candidate | 20 | touch | 0.786 | 6 | ok | 0.1647 | 0.009881 | 37.67 |
| continuation_candidate | 50 | above | 0.5 | 3 | LOW SAMPLE | 0.3021 | 0.01721 | 44.33 |
| failure_candidate | 5 | cross | 0.618 | 15 | ok | 0.06003 | 0.009164 | 14.47 |
| failure_candidate | 10 | cross | 0.618 | 15 | ok | 0.074 | 0.009981 | 14.47 |
| failure_candidate | 20 | cross | 0.618 | 15 | ok | 0.1136 | 0.0186 | 14.47 |
| failure_candidate | 50 | cross | 0.618 | 15 | ok | 0.1348 | 0.04412 | 14.47 |
| reaction_candidate | 5 | cross | 0.786 | 2 | LOW SAMPLE | 0.04316 | 0.04316 | 7 |
| reaction_candidate | 10 | cross | 1 | 1 | LOW SAMPLE | 0.06786 | 0.06786 | 34 |
| reaction_candidate | 20 | touch | 0.786 | 10 | ok | 0.0843 | 0.0843 | 17.1 |
| reaction_candidate | 50 | above | 0.786 | 2 | LOW SAMPLE | 0.1783 | 0.1783 | 18.5 |
| rejection_candidate | 5 | above | 1 | 1 | LOW SAMPLE | 0.19 | 0.001551 | 0 |
| rejection_candidate | 10 | above | 1 | 1 | LOW SAMPLE | 0.19 | 0.001551 | 0 |
| rejection_candidate | 20 | above | 1 | 1 | LOW SAMPLE | 0.19 | 0.001551 | 0 |
| rejection_candidate | 50 | above | 1 | 1 | LOW SAMPLE | 0.1915 | 0.001551 | 0 |

## View 2 — fingerprint ↔ outcome hints (Spearman rho)

Direction-inferred events only; candidates pooled (coarse). Positive
rho vs `mfe` = field tends to be higher when favorable excursion is
higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,
not prediction.

| fingerprint field | mfe h5 | mfe h10 | mfe h20 | mfe h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.0568 | 0.0518 | 0.006 | -0.0362 |
| pre_distance_atr_norm | 0.1404 | 0.1573 | 0.13 | 0.1165 |
| pre_approach_choppiness | -0.1434 | -0.1656 | -0.1294 | -0.1187 |
| at_wick_through_level | 0.3276 | 0.3023 | 0.2482 | 0.1693 |
| at_close_distance_atr_norm | 0.0351 | 0.0225 | 0.0102 | 0.0083 |
| post_bars_on_break_side | 0.0292 | 0.0542 | -0.0158 | -0.0096 |
| post_retest_count | -0.2625 | -0.3639 | -0.4972 | -0.5445 |
| post_remained_near_level_rate | -0.3063 | -0.3928 | -0.5017 | -0.5189 |

| fingerprint field | mae h5 | mae h10 | mae h20 | mae h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.1202 | 0.1096 | 0.0946 | 0.0023 |
| pre_distance_atr_norm | 0.1248 | 0.0382 | 0.0137 | -0.0281 |
| pre_approach_choppiness | -0.1476 | -0.0508 | -0.0218 | 0.0238 |
| at_wick_through_level | 0.2167 | 0.1271 | 0.1143 | 0.0394 |
| at_close_distance_atr_norm | 0.0857 | 0.1097 | 0.1164 | 0.0853 |
| post_bars_on_break_side | 0.0218 | 0.0182 | 0.0678 | 0.0774 |
| post_retest_count | 0.1384 | 0.2596 | 0.3982 | 0.521 |
| post_remained_near_level_rate | 0.1094 | 0.1974 | 0.3175 | 0.4193 |

## Triage buckets (arbitrary cut-offs, not tuned)

Cut-offs on max |rho vs mfe| across horizons: watch ≥ 0.5 & sign-stable, weak ≥ 0.3, else noise-like.

- **Worth more data (watch):** post_retest_count, post_remained_near_level_rate
- **Weak / unstable:** at_wick_through_level
- **Low covariation (noise-like):** pre_bars_approaching_level, pre_distance_atr_norm, pre_approach_choppiness, at_close_distance_atr_norm, post_bars_on_break_side

## What to look at next (triage, not conclusions)

- Candidates whose buckets are all LOW SAMPLE need more events before
  any pattern is worth reading.
- `watch` fields are only candidates for *more data collection*, not
  evidence of edge.
- Recent (2026) fibs may have truncated long horizons (`bars_available`),
  so h20/h50 fill in as post-2022-10-31 history grows.
