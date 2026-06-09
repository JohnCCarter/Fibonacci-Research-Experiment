# Toplist notes — fib fingerprint × outcome (research triage)

Run: `mtf_proj_20260605T124448Z`

> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a
> signal, and not a strategy. No parameter tuning. Buckets with
> `n_events` < 5 are flagged `LOW SAMPLE`. Use this to decide
> *what to collect more data on*, not *what to trade*.

## Inventory

- Joined events: 6836
- Joined rows (event × horizon): 27344
- Candidate buckets: 384 (24 flagged LOW SAMPLE)
- Horizons: 5, 10, 20, 50
- Direction-inferred events per horizon (used for hints): h5=5791, h10=5791, h20=5791, h50=5791

## View 1 — candidate summary (top 1 per candidate × horizon)

Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).
`mean_post_bars_on_break_side` is the expected-side proxy.

| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |
|---|---|---|---|---|---|---|---|---|
| continuation_candidate | 5 | above | 0.5 | 22 | ok | 0.07271 | 0.009691 | 43.41 |
| continuation_candidate | 10 | above | 0.5 | 22 | ok | 0.1119 | 0.01268 | 43.41 |
| continuation_candidate | 20 | above | 0.5 | 22 | ok | 0.1369 | 0.0179 | 43.41 |
| continuation_candidate | 50 | above | 0.5 | 22 | ok | 0.2225 | 0.02434 | 43.41 |
| failure_candidate | 5 | cross | 0.618 | 122 | ok | 0.0591 | 0.01646 | 14.2 |
| failure_candidate | 10 | cross | 0.236 | 117 | ok | 0.08388 | 0.02363 | 13.8 |
| failure_candidate | 20 | above | 0.236 | 4 | LOW SAMPLE | 0.1298 | 0.0715 | 25 |
| failure_candidate | 50 | above | 0.236 | 4 | LOW SAMPLE | 0.2369 | 0.2947 | 25 |
| reaction_candidate | 5 | above | 0.786 | 19 | ok | 0.0519 | 0.0519 | 15.16 |
| reaction_candidate | 10 | above | 0.236 | 22 | ok | 0.07422 | 0.07422 | 24.73 |
| reaction_candidate | 20 | cross | 1 | 25 | ok | 0.1059 | 0.1059 | 27.12 |
| reaction_candidate | 50 | below | 1 | 24 | ok | 0.2032 | 0.2032 | 22.88 |
| rejection_candidate | 5 | cross | 0.236 | 30 | ok | 0.06217 | 0.008489 | 10.87 |
| rejection_candidate | 10 | cross | 0.236 | 30 | ok | 0.08585 | 0.01137 | 10.87 |
| rejection_candidate | 20 | cross | 0.236 | 30 | ok | 0.1147 | 0.02296 | 10.87 |
| rejection_candidate | 50 | cross | 0.236 | 30 | ok | 0.1477 | 0.03808 | 10.87 |

## View 2 — fingerprint ↔ outcome hints (Spearman rho)

Direction-inferred events only; candidates pooled (coarse). Positive
rho vs `mfe` = field tends to be higher when favorable excursion is
higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,
not prediction.

| fingerprint field | mfe h5 | mfe h10 | mfe h20 | mfe h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.0362 | 0.035 | 0.0335 | 0.0333 |
| pre_distance_atr_norm | 0.0828 | 0.052 | 0.0328 | 0.0488 |
| pre_approach_choppiness | -0.0855 | -0.0551 | -0.0281 | -0.0513 |
| at_wick_through_level | 0.0898 | 0.0647 | 0.0176 | -0.0204 |
| at_close_distance_atr_norm | 0.0188 | 0.0399 | 0.0298 | 0.0348 |
| post_bars_on_break_side | -0.0069 | -0.0074 | -0.0556 | -0.0164 |
| post_retest_count | -0.2003 | -0.2975 | -0.4137 | -0.4265 |
| post_remained_near_level_rate | -0.2015 | -0.2888 | -0.3997 | -0.4062 |

| fingerprint field | mae h5 | mae h10 | mae h20 | mae h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.1123 | 0.0939 | 0.0521 | 0.0006 |
| pre_distance_atr_norm | 0.0912 | 0.0584 | 0.0349 | 0.0287 |
| pre_approach_choppiness | -0.109 | -0.0711 | -0.0462 | -0.0294 |
| at_wick_through_level | 0.1022 | 0.0871 | 0.0688 | 0.0004 |
| at_close_distance_atr_norm | 0.1141 | 0.0719 | 0.0427 | -0.0075 |
| post_bars_on_break_side | -0.0545 | -0.051 | -0.0075 | 0.0217 |
| post_retest_count | 0.1771 | 0.2739 | 0.3892 | 0.4739 |
| post_remained_near_level_rate | 0.1577 | 0.2341 | 0.3342 | 0.4056 |

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
