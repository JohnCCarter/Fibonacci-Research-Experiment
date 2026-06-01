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

Labels skrivs via `uv run python -m fibengine.labeling.tool` (begränsningar: [`docs/LABELING_TOOL.md`](../docs/LABELING_TOOL.md)).

Kör `uv run python -m fibengine.labeling.worklist` för att se täckning mot
20–30-setup-målet (PREMORTEM.md) och få färdiga `labeling.tool`-kommandon för de
symbol/timeframe-kombinationer som ännu saknar facit.

Varje label har ett `source`-fält:

- `source: "human"` (default) — manuellt facit, golden set.
- `source: "machine"` — provisorisk kandidat från `labeling.autolabel`. Exkluderas
  från recall/agreement och räknas inte mot 20–30-målet. Granska i `labeling.tool`
  och spara → blir `human`.

**Två giltiga typer av maskin-svar** (motor-swing vs chartfönster): [`docs/MACHINE_LABELING.md`](../docs/MACHINE_LABELING.md).

Legacy platt filnamn (`binance_BTC-USDT_1h.json` på rot) stöds fortfarande vid läsning men nya sparas i kategoriserad struktur.

## Multi-leg (research, 1d+)

Flera fib-legs i **samma** fil när du märker ned + upp (eller fler segment) på daily:

- Spara via labeling tool: `p` (push leg), sedan `s` — se [LABELING_TOOL.md](../docs/LABELING_TOOL.md) §5B.
- JSON får `"legs": [ { "id": "leg_1", "high": ..., "low": ... }, ... ]`.
- Top-level `high`/`low` = leg_1 (bakåtkompatibilitet för motor/recall idag).

**Exempel:** `binance/BTC-USDT/1d.json` — 30 legs (BTC HUR-facit, 2026-05-29).

**Motor använder inte** `legs[]` än — endast research/golden. Se [MTF_DAILY_RESEARCH.md](../docs/MTF_DAILY_RESEARCH.md).
