# Multi-run notes — fib fingerprint × outcome (data expansion triage)

Baseline run: `fp_outcomes_20260605T114206Z` (narrow window)
Expanded run: `fp_outcomes_20260605T115819Z` (combined / wider candle window)

> DESCRIPTIVE DATA-EXPANSION TRIAGE ONLY. Same method and thresholds;
> only the candle data scope widened to grow sample size. Not an edge,
> not a signal, not a strategy. No tuning. No candidate-logic change.

## Combined summary

- Events: 51 → **1148** (rows 204 → 4592)
- Candidate buckets: 148 → **360**
- Buckets newly reaching n≥5 (were LOW SAMPLE in baseline): **240**
- Buckets still LOW SAMPLE (n<5) in expanded: 120

## Sample-size inventory

| metric | baseline | expanded |
|---|---|---|
| total buckets | 148 | 360 |
| buckets n≥5 | 0 | 240 |
| buckets n≥10 | 0 | 152 |
| buckets n≥20 | 0 | 80 |
| LOW SAMPLE buckets | 148 | 120 |

Per-bucket detail: `sample_inventory.csv`.

## Fingerprint stability over more events

Compares Spearman(field, mfe) per horizon between runs (direction-
inferred events, candidates pooled). `WEAKENED` = a baseline signal
shrank with more data (small-sample artifact). `sign flip` = direction
reversed. Descriptive only.

| fingerprint field | base max\|rho\| | exp max\|rho\| | max shift | verdict |
|---|---|---|---|---|
| pre_bars_approaching_level | 0.3911 | 0.162 | 0.2783 | WEAKENED (small-sample artifact) |
| pre_distance_atr_norm | 0.4972 | 0.0719 | 0.4878 | UNSTABLE (sign flip) |
| pre_approach_choppiness | 0.4707 | 0.0724 | 0.5022 | UNSTABLE (sign flip) |
| at_wick_through_level | 0.4506 | 0.0877 | 0.4052 | UNSTABLE (sign flip) |
| at_close_distance_atr_norm | 0.2739 | 0.0356 | 0.2843 | UNSTABLE (sign flip) |
| post_bars_on_break_side | 0.6699 | 0.1442 | 0.806 | UNSTABLE (sign flip) |
| post_retest_count | 0.6263 | 0.4202 | 0.3604 | WEAKENED (small-sample artifact) |
| post_remained_near_level_rate | 0.375 | 0.4516 | 0.4855 | UNSTABLE (sign flip) |

## What to look at next (triage, not conclusions)

- `WEAKENED` / `sign flip` fields were noise at low N — deprioritize.
- `stable-ish` fields kept their (weak) co-occurrence as N grew — the
  only ones worth a closer, per-candidate look once buckets are larger.
- Buckets still LOW SAMPLE need more events (older BTC pre-2016 and SOL
  pre-2022 1d need a network refetch before they can join).
