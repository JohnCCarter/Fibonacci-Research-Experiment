# Toplist notes — fib fingerprint × outcome (research triage)

Run: `mtf_proj_20260605T124004Z`

> DESCRIPTIVE / LOW-SAMPLE TRIAGE ONLY. This is not an edge, not a
> signal, and not a strategy. No parameter tuning. Buckets with
> `n_events` < 5 are flagged `LOW SAMPLE`. Use this to decide
> *what to collect more data on*, not *what to trade*.

## Inventory

- Joined events: 681
- Joined rows (event × horizon): 2724
- Candidate buckets: 340 (172 flagged LOW SAMPLE)
- Horizons: 5, 10, 20, 50
- Direction-inferred events per horizon (used for hints): h5=574, h10=574, h20=574, h50=574

## View 1 — candidate summary (top 1 per candidate × horizon)

Full sorted table: `toplist.csv` (mfe↓, mae↑, break-side dwell↓, n↓).
`mean_post_bars_on_break_side` is the expected-side proxy.

| candidate | h | relation | level | n | flag | mean_mfe | mean_mae | brk_side |
|---|---|---|---|---|---|---|---|---|
| continuation_candidate | 5 | below | 1 | 2 | LOW SAMPLE | 0.08493 | 0.03156 | 38 |
| continuation_candidate | 10 | above | 0.236 | 1 | LOW SAMPLE | 0.1704 | 0.004157 | 49 |
| continuation_candidate | 20 | above | 0.236 | 1 | LOW SAMPLE | 0.1704 | 0.004157 | 49 |
| continuation_candidate | 50 | cross | 0.786 | 15 | ok | 0.1922 | 0.07755 | 39.47 |
| failure_candidate | 5 | cross | 0.618 | 17 | ok | 0.06367 | 0.02156 | 15.53 |
| failure_candidate | 10 | cross | 1 | 6 | ok | 0.09137 | 0.0432 | 16.5 |
| failure_candidate | 20 | above | 0.236 | 1 | LOW SAMPLE | 0.2399 | 0.03363 | 22 |
| failure_candidate | 50 | touch | 0.5 | 3 | LOW SAMPLE | 0.3856 | 0.04721 | 5.333 |
| reaction_candidate | 5 | cross | 0.786 | 2 | LOW SAMPLE | 0.06521 | 0.06521 | 25 |
| reaction_candidate | 10 | above | 1 | 2 | LOW SAMPLE | 0.08279 | 0.08279 | 3 |
| reaction_candidate | 20 | cross | 0.786 | 2 | LOW SAMPLE | 0.12 | 0.12 | 25 |
| reaction_candidate | 50 | below | 1 | 3 | LOW SAMPLE | 0.2532 | 0.2532 | 4 |
| rejection_candidate | 5 | cross | 0.236 | 1 | LOW SAMPLE | 0.1003 | 0.02625 | 0 |
| rejection_candidate | 10 | cross | 0.236 | 1 | LOW SAMPLE | 0.1734 | 0.02625 | 0 |
| rejection_candidate | 20 | below | 0.236 | 2 | LOW SAMPLE | 0.2611 | 0.03126 | 4 |
| rejection_candidate | 50 | below | 0.236 | 2 | LOW SAMPLE | 0.4268 | 0.03126 | 4 |

## View 2 — fingerprint ↔ outcome hints (Spearman rho)

Direction-inferred events only; candidates pooled (coarse). Positive
rho vs `mfe` = field tends to be higher when favorable excursion is
higher. `n/a` = <3 pairs or no variance. Descriptive co-occurrence,
not prediction.

| fingerprint field | mfe h5 | mfe h10 | mfe h20 | mfe h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.0588 | 0.048 | 0.0466 | 0.0445 |
| pre_distance_atr_norm | 0.0351 | 0.0256 | 0.0115 | 0.0078 |
| pre_approach_choppiness | -0.042 | -0.0254 | -0.0074 | -0.0128 |
| at_wick_through_level | 0.2007 | 0.1703 | 0.1173 | 0.0747 |
| at_close_distance_atr_norm | 0.0575 | 0.044 | -0.0018 | -0.0104 |
| post_bars_on_break_side | 0.024 | -0.0074 | -0.0514 | -0.062 |
| post_retest_count | -0.1455 | -0.2317 | -0.3529 | -0.3751 |
| post_remained_near_level_rate | -0.135 | -0.2138 | -0.3585 | -0.3795 |

| fingerprint field | mae h5 | mae h10 | mae h20 | mae h50 |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.0579 | 0.061 | 0.0082 | -0.0333 |
| pre_distance_atr_norm | 0.0539 | 0.0785 | 0.0321 | 0.0738 |
| pre_approach_choppiness | -0.0773 | -0.1025 | -0.057 | -0.0898 |
| at_wick_through_level | 0.2384 | 0.1669 | 0.1446 | 0.0859 |
| at_close_distance_atr_norm | 0.0837 | 0.0628 | 0.0535 | 0.0074 |
| post_bars_on_break_side | -0.0538 | -0.0689 | 0.0166 | 0.0568 |
| post_retest_count | 0.1366 | 0.2552 | 0.3763 | 0.4677 |
| post_remained_near_level_rate | 0.108 | 0.2055 | 0.3392 | 0.4369 |

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
