# Results — Chain-clustering probe (is chaining a mode or a per-leg coin flip?)

**Date run:** 2026-07-21 (cloud session, autonomous, owner blanket GO) · **Prereg (locked incl.
§9 pre-run amendments):** [prereg](btc-fib-chain-clustering-probe-prereg-20260721.md) ·
**Status:** **SIGNED OFF by owner 2026-07-21** (mobile session). Executed verbatim: seed 20260721,
n_perm/n_boot = 2000, LOCKED acceptance band, fail-closed manifest check passed (484), fresh
2026-07-21 cache (4h 21 273 bars; signed cascade numbers reproduce exactly on it). Runtime ~2 s
(memoized bar lookup).

## Verdict (primary cell, 4h)

**`no_chain_clustering`** — chained selections do **not** cluster serially beyond the marginal
rate, once the hub-coupling confound is guarded:

| Cell | Pairs | Chain rate | A (full) | null | p | **A_sf (single-file)** | null | **p_sf** | Verdict |
|------|-------|-----------|----------|------|---|------------------------|------|----------|---------|
| **4h** | **363** | 0.256 | 31 | 23.6 | 0.022 | **25** | 19.1 | **0.061** | **`no_chain_clustering`** |
| 1d | 74 | 0.189 | 4 | 2.5 | 0.220 | 3 | 2.2 | 0.377 | `context_only` |
| 1w | 23 | 0.391 | 3 | 3.2 | 0.718 | 2 | 1.7 | 0.566 | `context_only` |

Exclusions (4h): 2 no-predecessor, 6 degenerate, 0 outside-window. Hub diagnostics: 362
adjacent slots, 294 single-file, 42 hub-shared. Markov gap = +0.107, bootstrap CI
**[−0.002, +0.220] includes 0**; permutation-null mean ≈ 0.

**The §9 A1 guard was decisive (honesty note):** the unguarded full-array statistic alone would
have *passed* (p = 0.022) — the verdict would then have rested partly on 42 hub-shared slots
where two consecutive pairs test the *same* predecessor anchor. The single-file statistic
(true leg→leg transitions only) does not reach the locked gate (p = 0.061). Point estimates sit
above null in both statistics, so a **weak clustering tendency is compatible with the data** —
but per the locked family the verdict is a null. Do not cite this as "clustering disproven";
cite it as "not demonstrated at current power under the confound-guarded gate".

## Descriptives (reported, never verdict-bearing)

- **Every chained pair reverses direction** (93/93 reversal, 0 continuation). This is
  **mechanically expected**, not a discovery: a down-leg's endpoint is a low, and a new leg
  *originating* at a low is by fib convention an up-leg. It still pins the geometry: the
  cascade is a **zigzag** (impulse → retracement-anchored next impulse), exactly the
  TradingView drawing rhythm in the owner's self-report.
- **Chained pairs are immediate**: median inter-leg gap 0 bars (endpoint bar = origin bar)
  vs 15.5 bars for unchained pairs.
- Run lengths: 62 runs of 1s; max run 6, three runs ≥ 4 — long runs exist but are not
  statistically surprising given rate 0.256 and N=363.
- Labeling-day sensitivity (§7): nearly degenerate — 352/363 pairs have both legs drawn the
  same day (the big 2026-06-12 session), so the labeling-session confound cannot be
  distinguished from structure on this corpus (disclosed; unchanged adjacency on the subset).

## Modeling consequence (per prereg §2, binding for the next step)

Independence (at current power) → the sequential-conditioning selection feature can be a
**per-leg feature** (chained-origin proximity to the latest completed leg endpoint); a
state-aware "in-cascade regime" model is **not** justified by this probe. If the owner later
wants the borderline (p_sf = 0.061) chased, that is a NEW prereg on fresh/augmented facit —
not a re-run.

## Non-claims (§7 hold)

No edge/behaviour/backtest/PnL/Genesis claim; no model; no facit touched; no auto-fib;
1H/ETH untouched.

## Reproduce

`uv run --no-sync python -m fibengine.research.chain_clustering --probe --config
config/settings.expansion.yaml` → `experiments/review/chain_clustering/summary.json`
(gitignored/regenerable), deterministic, ~2 s.

## Owner sign-off

- [x] **Signed 2026-07-21** — verdict accepted advisory→signed, no objections; the
      "not demonstrated at current power" framing above stays binding.
- [x] Next: sequential-conditioning selection feature — ran same day →
      [`no_sequential_feature_signal`](btc-fib-sequential-feature-results-20260721.md)
