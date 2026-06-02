# 2026-05-28 Real-Data Stability Matrix

Hypothesis: if the Layer A swing selector is not overfit to one BTC sample, it should remain stable across liquid symbols and multiple timeframes without changing scoring weights.

Run: `matrix_20260528T072357Z`

Scope:
- Exchange: Bitfinex spot via CCXT
- Symbols: `BTC/USD`, `ETH/USD`, `SOL/USD`
- Timeframes: `15m`, `1h`, `4h`
- Limit: 500 candles per market/timeframe

Observations:
- All 9 cases completed with `n_none == 0`.
- Best first-pass stability came from `ETH/USD 1h`: `flip_rate=0.0683`, `confirmed_rate=0.9386`, `direction_consistency=0.9795`.
- `SOL/USD 1h` and `ETH/USD 15m` were also strong on flip/confirmation.
- `BTC/USD 15m` was the weakest row in this matrix by flip rate and confirmed rate, but still not broken.
- Endpoint drift remains the main metric to investigate. `SOL/USD 1h` had strong stability but high drift (`52.125` bars).

Decision:
- Keep the current Layer A scoring unchanged for now.
- Do not tune weights from this matrix alone.
- Next work should add pivot-recall measurement against manual labels before changing detection/scoring.

Layer B smoke matrix:
- Run: `trade_matrix_20260528T075650Z`
- The simple confirmed-swing retracement model was best on `ETH/USD 1h`: `avg_r=0.8479`, `win_rate=0.7059`, `fill_rate=0.68`.
- `SOL/USD 15m` and `BTC/USD 1h` were also positive, but weaker.
- `SOL/USD 1h`, `SOL/USD 4h`, and `ETH/USD 15m` were negative.
- This supports keeping Layer B separate: stable swing selection does not automatically imply a profitable entry/exit rule on every market/timeframe.

