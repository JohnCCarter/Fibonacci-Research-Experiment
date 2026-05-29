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

Kör `uv run python -m fibengine.labeling.worklist` för att se täckning mot
20–30-setup-målet (PREMORTEM.md) och få färdiga `labeling.tool`-kommandon för de
symbol/timeframe-kombinationer som ännu saknar facit.

Varje label har ett `source`-fält:

- `source: "human"` (default) — manuellt facit, golden set.
- `source: "machine"` — provisorisk kandidat från `labeling.autolabel`. Exkluderas
  från recall/agreement och räknas inte mot 20–30-målet. Granska i `labeling.tool`
  och spara → blir `human`.

Legacy platt filnamn (`binance_BTC-USDT_1h.json` på rot) stöds fortfarande vid läsning men nya sparas i kategoriserad struktur.
