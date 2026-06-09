# Toplist notes — fib fingerprint × outcome (research triage)

Run: `mtf_proj_20260605T124001Z`

> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a
> signal, and not a strategy. No parameter tuning. Buckets with
> `n_events` < 5 are flagged `LOW SAMPLE`. Use this to decide
> *what to collect more data on*, not *what to trade*.

## Inventory

- Joined events: 76
- Joined rows (event × horizon): 304
- Candidate buckets: 132 (120 flagged LOW SAMPLE)
- Horizons: 5, 10, 20, 50
- Direction-inferred events per horizon (used for hints): h5=67, h10=67, h20=67, h50=67

## View 1 — candidate summary (top 1 per candidate × horizon)

Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).
`mean_post_bars_on_break_side` is the expected-side proxy.

| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |
|---|---|---|---|---|---|---|---|---|
| continuation_candidate | 5 | touch | 0.786 | 4 | LOW SAMPLE | 0.09169 | 0.01313 | 28.5 |
| continuation_candidate | 10 | touch | 0.786 | 4 | LOW SAMPLE | 0.1093 | 0.03321 | 28.5 |
| continuation_candidate | 20 | touch | 0.786 | 4 | LOW SAMPLE | 0.1093 | 0.03378 | 28.5 |
| continuation_candidate | 50 | touch | 1 | 2 | LOW SAMPLE | 0.1367 | 0.04715 | 29 |
| failure_candidate | 5 | cross | 0.382 | 1 | LOW SAMPLE | 0.2226 | 0.01496 | 0 |
| failure_candidate | 10 | cross | 0.382 | 1 | LOW SAMPLE | 0.2226 | 0.01496 | 0 |
| failure_candidate | 20 | cross | 0.382 | 1 | LOW SAMPLE | 0.2226 | 0.01496 | 0 |
| failure_candidate | 50 | cross | 0.382 | 1 | LOW SAMPLE | 0.2226 | 0.01496 | 0 |
| reaction_candidate | 5 | above | 0.786 | 1 | LOW SAMPLE | 0.1354 | 0.1354 | 10 |
| reaction_candidate | 10 | above | 0.786 | 1 | LOW SAMPLE | 0.1838 | 0.1838 | 10 |
| reaction_candidate | 20 | above | 0.786 | 1 | LOW SAMPLE | 0.1838 | 0.1838 | 10 |
| reaction_candidate | 50 | above | 0.786 | 1 | LOW SAMPLE | 0.1838 | 0.1838 | 10 |
| rejection_candidate | 5 | above | 0.236 | 1 | LOW SAMPLE | 0.2226 | 0.01496 | 0 |
| rejection_candidate | 10 | above | 0.236 | 1 | LOW SAMPLE | 0.2226 | 0.01496 | 0 |
| rejection_candidate | 20 | above | 0.236 | 1 | LOW SAMPLE | 0.2226 | 0.01496 | 0 |
| rejection_candidate | 50 | above | 0.236 | 1 | LOW SAMPLE | 0.2226 | 0.01496 | 0 |

## View 2 — fingerprint ↔ outcome hints (Spearman rho)

Direction-inferred events only; candidates pooled (coarse). Positive
rho vs `mfe` = field tends to be higher when favorable excursion is
higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,
not prediction.

| fingerprint field | mfe h5 | mfe h10 | mfe h20 | mfe h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.3307 | 0.3094 | 0.4009 | 0.2294 |
| pre_distance_atr_norm | 0.3541 | 0.426 | 0.4912 | 0.4973 |
| pre_approach_choppiness | -0.4191 | -0.4921 | -0.5504 | -0.5068 |
| at_wick_through_level | 0.585 | 0.5654 | 0.5014 | 0.3229 |
| at_close_distance_atr_norm | 0.0229 | 0.0766 | 0.0536 | 0.0472 |
| post_bars_on_break_side | -0.4059 | -0.4426 | -0.3534 | -0.2106 |
| post_retest_count | -0.2471 | -0.3162 | -0.4078 | -0.4597 |
| post_remained_near_level_rate | -0.2297 | -0.2434 | -0.3395 | -0.4183 |

| fingerprint field | mae h5 | mae h10 | mae h20 | mae h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.0454 | -0.085 | -0.0286 | -0.0571 |
| pre_distance_atr_norm | 0.4879 | 0.3918 | 0.1603 | 0.0141 |
| pre_approach_choppiness | -0.5137 | -0.428 | -0.191 | -0.0409 |
| at_wick_through_level | 0.5204 | 0.332 | 0.2053 | 0.087 |
| at_close_distance_atr_norm | 0.2465 | 0.2418 | 0.0587 | 0.0386 |
| post_bars_on_break_side | 0.065 | 0.1207 | 0.0184 | 0.1082 |
| post_retest_count | 0.2729 | 0.3754 | 0.4453 | 0.5515 |
| post_remained_near_level_rate | 0.3116 | 0.3636 | 0.3609 | 0.4768 |

## Triage buckets (arbitrary cut-offs, not tuned)

Cut-offs on max |rho vs mfe| across horizons: watch ≥ 0.5 & sign-stable, weak ≥ 0.3, else noise-like.

- **Worth more data (watch):** pre_approach_choppiness, at_wick_through_level
- **Weak / unstable:** pre_bars_approaching_level, pre_distance_atr_norm, post_bars_on_break_side, post_retest_count, post_remained_near_level_rate
- **Low covariation (noise-like):** at_close_distance_atr_norm

## What to look at next (triage, not conclusions)

- Candidates whose buckets are all LOW SAMPLE need more events before
  any pattern is worth reading.
- `watch` fields are only candidates for *more data collection*, not
  evidence of edge.
- Recent (2026) fibs may have truncated long horizons (`bars_available`),
  so h20/h50 fill in as post-2022-10-31 history grows.
