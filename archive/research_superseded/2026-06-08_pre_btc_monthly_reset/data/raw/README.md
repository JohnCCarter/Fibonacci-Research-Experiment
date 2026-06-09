# data/raw

Cachad OHLCV-data från fetch-steget.

## Struktur

```text
raw/
  INDEX.md
  {exchange}/
    {symbol-with-dash}/
      {timeframe}/
        limit_{n}.csv
```

Exempel: `bitfinex/BTC-USD/1h/limit_500.csv`

## Index

- `INDEX.md` listar alla cachefiler med exchange, symbol, timeframe och limit.
