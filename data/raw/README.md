# data/raw

Cached OHLCV CSV (gitignored). Empty after 2026-06-08 reset.

Fetch BTC candles:

```bash
uv run python -m fibengine.data.fetch --symbols BTC/USD --timeframes 1M,1w,1d --refresh
```

Prior caches: `archive/research_superseded/2026-06-08_pre_btc_monthly_reset/data/raw/`
