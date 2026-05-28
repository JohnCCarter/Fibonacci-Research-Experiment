# data/labels

Golden set för manuellt labelade swing high/low.

## Struktur

```
labels/
  INDEX.md
  {exchange}/
    {symbol-with-dash}/
      {timeframe}.json
```

Exempel: `binance/BTC-USDT/1h.json`

## Index

- `INDEX.md` — tabell över alla labels (path, exchange, symbol, timeframe).
- `binance/README.md` — översikt per börs.

Labels skrivs via `uv run python -m fibengine.labeling.tool`.

Legacy platt filnamn (`binance_BTC-USDT_1h.json` på rot) stöds fortfarande vid läsning men nya sparas i kategoriserad struktur.
