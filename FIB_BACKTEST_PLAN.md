# Fibonacci Backtest Plan

This plan turns the current synthetic and single-market stability checks into a staged research workflow for real market data.

Premortem source of truth: `premortem/PREMORTEM.md`. Each phase below is designed to reduce one or more premortem risks, especially overfitting to one market, look-ahead bias, weak auditability, and mixing Layer A swing selection with Layer B trade execution.

## Phase 1 - Real-Data Stability Matrix

Goal: verify that Layer A swing selection remains stable across multiple liquid markets and timeframes.

Scope:
- Run the existing causal walk-forward stability backtest over a matrix of symbols and timeframes.
- Start with liquid Binance spot markets: `BTC/USDT`, `ETH/USDT`, `SOL/USDT`.
- Start with `15m`, `1h`, and `4h`.
- Use the same scoring settings across the whole matrix.
- Write one JSONL row per market/timeframe into `experiments/backtest_matrix.jsonl`.

Success criteria:
- Every matrix row records symbol, timeframe, limit, config hash, run id, and stability metrics.
- No row silently disappears on failure; errors are recorded as JSONL rows.
- Results can be compared without inspecting per-run folders.

## Phase 2 - Stability Triage

Goal: classify where the current Fibonacci swing engine behaves well enough to justify deeper analysis.

Review metrics:
- Prefer low `flip_rate`.
- Prefer high `confirmed_rate`.
- Prefer high `direction_consistency`.
- Investigate high `mean_endpoint_drift_bars`.
- Flag any market/timeframe with `n_none > 0`.

Output:
- A concise ranked summary of stable, borderline, and weak market/timeframe combinations.
- Notes in `premortem/reflections/` when a result changes a working assumption.

## Phase 3 - Manual Label Recall

Goal: ensure the pivot candidate set can actually contain the swing points a human would draw.

Scope:
- Add or collect manually labeled examples in `data/labels/`.
- Measure whether detected pivots land near labeled high/low bars before tuning scoring weights.
- Keep `agreement` as a sanity signal only, not an optimization target.

Success criteria:
- Separate pivot recall metrics exist before any scoring changes.
- Failures identify whether the issue is detection, scoring, or confirmation.

## Phase 4 - Layer B Trade Simulation

Goal: test whether confirmed Fib swings can support a simple trade model without contaminating Layer A.

Scope:
- Only consume selected confirmed swings from Layer A.
- Simulate entries at configured retracement levels.
- Use explicit stop and target rules.
- Report fill rate, win rate, average R, max drawdown, and exposure.

Guardrail:
- Layer B must not feed back into swing selection, feature engineering, or scoring.

## Phase 5 - Iteration Discipline

Goal: avoid overfitting and keep experiments auditable.

Rules:
- Change one meaningful setting at a time.
- Keep config hashes in all output rows.
- Compare per symbol/timeframe, not just aggregate means.
- Record surprising outcomes in `premortem/reflections/`.
