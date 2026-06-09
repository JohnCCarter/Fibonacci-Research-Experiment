# Toplist notes — fib fingerprint × outcome (research triage)

Run: `mtf_proj_20260605T124041Z`

> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a
> signal, and not a strategy. No parameter tuning. Buckets with
> `n_events` < 5 are flagged `LOW SAMPLE`. Use this to decide
> *what to collect more data on*, not *what to trade*.

## Inventory

- Joined events: 7453
- Joined rows (event × horizon): 29812
- Candidate buckets: 384 (24 flagged LOW SAMPLE)
- Horizons: 5, 10, 20, 50
- Direction-inferred events per horizon (used for hints): h5=6303, h10=6303, h20=6303, h50=6303

## View 1 — candidate summary (top 1 per candidate × horizon)

Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).
`mean_post_bars_on_break_side` is the expected-side proxy.

| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |
|---|---|---|---|---|---|---|---|---|
| continuation_candidate | 5 | above | 1 | 27 | ok | 0.0704 | 0.01248 | 33.59 |
| continuation_candidate | 10 | above | 0.5 | 26 | ok | 0.1057 | 0.01143 | 42.65 |
| continuation_candidate | 20 | above | 0.5 | 26 | ok | 0.1295 | 0.01584 | 42.65 |
| continuation_candidate | 50 | above | 0.5 | 26 | ok | 0.2075 | 0.02166 | 42.65 |
| failure_candidate | 5 | cross | 0.618 | 135 | ok | 0.05811 | 0.0168 | 14.84 |
| failure_candidate | 10 | cross | 0.236 | 126 | ok | 0.08274 | 0.02245 | 13.6 |
| failure_candidate | 20 | above | 0.236 | 4 | LOW SAMPLE | 0.1298 | 0.0715 | 25 |
| failure_candidate | 50 | above | 0.236 | 4 | LOW SAMPLE | 0.2369 | 0.2947 | 25 |
| reaction_candidate | 5 | above | 0.786 | 21 | ok | 0.0502 | 0.0502 | 14.9 |
| reaction_candidate | 10 | cross | 1 | 25 | ok | 0.07023 | 0.07023 | 27.12 |
| reaction_candidate | 20 | cross | 1 | 25 | ok | 0.1059 | 0.1059 | 27.12 |
| reaction_candidate | 50 | below | 1 | 27 | ok | 0.1933 | 0.1933 | 22.22 |
| rejection_candidate | 5 | above | 1 | 51 | ok | 0.06089 | 0.01348 | 10.57 |
| rejection_candidate | 10 | above | 1 | 51 | ok | 0.08496 | 0.02041 | 10.57 |
| rejection_candidate | 20 | above | 1 | 51 | ok | 0.1139 | 0.03357 | 10.57 |
| rejection_candidate | 50 | above | 1 | 51 | ok | 0.1452 | 0.06484 | 10.57 |

## View 2 — fingerprint ↔ outcome hints (Spearman rho)

Direction-inferred events only; candidates pooled (coarse). Positive
rho vs `mfe` = field tends to be higher when favorable excursion is
higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,
not prediction.

| fingerprint field | mfe h5 | mfe h10 | mfe h20 | mfe h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.0376 | 0.0343 | 0.0347 | 0.0344 |
| pre_distance_atr_norm | 0.0854 | 0.0557 | 0.0332 | 0.0489 |
| pre_approach_choppiness | -0.0856 | -0.0567 | -0.0273 | -0.0493 |
| at_wick_through_level | 0.0258 | 0.0017 | -0.0398 | -0.0643 |
| at_close_distance_atr_norm | 0.0147 | 0.0344 | 0.0259 | 0.0313 |
| post_bars_on_break_side | -0.0055 | -0.0105 | -0.057 | -0.0186 |
| post_retest_count | -0.1859 | -0.2827 | -0.3953 | -0.4136 |
| post_remained_near_level_rate | -0.1879 | -0.2747 | -0.3821 | -0.3928 |

| fingerprint field | mae h5 | mae h10 | mae h20 | mae h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.1037 | 0.0874 | 0.0449 | -0.0005 |
| pre_distance_atr_norm | 0.0878 | 0.0591 | 0.0343 | 0.0319 |
| pre_approach_choppiness | -0.1032 | -0.0698 | -0.0437 | -0.032 |
| at_wick_through_level | 0.0587 | 0.0425 | 0.0254 | -0.0355 |
| at_close_distance_atr_norm | 0.1027 | 0.0651 | 0.0347 | -0.0076 |
| post_bars_on_break_side | -0.0536 | -0.0531 | -0.0056 | 0.0248 |
| post_retest_count | 0.178 | 0.2754 | 0.3914 | 0.475 |
| post_remained_near_level_rate | 0.1582 | 0.2341 | 0.3351 | 0.4059 |

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
