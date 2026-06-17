# data/raw index

| exchange | symbol | timeframe | cache file (local) |
|----------|--------|-----------|-------------------|
| bitfinex | BTC/USD | 1M | `bitfinex/BTC-USD/1M/limit_500.csv` |
| bitfinex | BTC/USD | 1w | `bitfinex/BTC-USD/1w/limit_1000.csv` |
| bitfinex | BTC/USD | 1d | `bitfinex/BTC-USD/1d/limit_3500.csv` |

CSV caches are gitignored. Refresh: `uv run python -m fibengine.data.fetch --symbols BTC/USD --timeframes 1M,1w,1d --refresh --config config/settings.expansion.yaml`

Preflight: `uv run python -m fibengine.labeling.preflight --symbol BTC/USD --timeframes "1M,1w,1d,4h,1h" --config config/settings.expansion.yaml`
