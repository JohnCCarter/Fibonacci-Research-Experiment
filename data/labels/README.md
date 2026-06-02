# data/labels

Golden set fÃ¶r manuellt labelade swing high/low.

## Struktur

```
labels/
  INDEX.md
  {exchange}/
    {symbol-with-dash}/
      {timeframe}.json
```

Exempel (ny default): `bitfinex/BTC-USD/1d.json`  
Legacy Bitfinex-facit Ã¤r arkiverat under `archive/data_labels_Bitfinex/labels/`.

## Aktiva mappar (Bitfinex)

- Swing-facit: `data/labels/bitfinex/{symbol}/{timeframe}.json`
- Human-fib annoteringar: `data/labels/human_fib/bitfinex/{symbol}/{timeframe}/{fib_id}.json`

## Index

- `INDEX.md` â€” tabell Ã¶ver alla labels (path, exchange, symbol, timeframe).
- `archive/data_labels_Bitfinex/labels/Bitfinex/README.md` â€” legacy Bitfinex-Ã¶versikt (arkiv).

Labels skrivs via `uv run python -m fibengine.labeling.tool` (begrÃ¤nsningar: [`docs/LABELING_TOOL.md`](../docs/LABELING_TOOL.md)).

KÃ¶r `uv run python -m fibengine.labeling.worklist` fÃ¶r att se tÃ¤ckning mot
20â€“30-setup-mÃ¥let (PREMORTEM.md) och fÃ¥ fÃ¤rdiga `labeling.tool`-kommandon fÃ¶r de
symbol/timeframe-kombinationer som Ã¤nnu saknar facit.

Varje label har ett `source`-fÃ¤lt:

- `source: "human"` (default) â€” manuellt facit, golden set.
- `source: "machine"` â€” provisorisk kandidat frÃ¥n `labeling.autolabel`. Exkluderas
  frÃ¥n recall/agreement och rÃ¤knas inte mot 20â€“30-mÃ¥let. Granska i `labeling.tool`
  och spara â†’ blir `human`.

**TvÃ¥ giltiga typer av maskin-svar** (motor-swing vs chartfÃ¶nster): [`docs/MACHINE_LABELING.md`](../docs/MACHINE_LABELING.md).

Legacy platt filnamn (`{exchange}_{symbol}_{timeframe}.json` pÃ¥ rot) stÃ¶ds fortfarande vid lÃ¤sning men nya sparas i kategoriserad struktur.

## Multi-leg (research, 1d+)

Flera fib-legs i **samma** fil nÃ¤r du mÃ¤rker ned + upp (eller fler segment) pÃ¥ daily:

- Spara via labeling tool: `p` (push leg), sedan `s` â€” se [LABELING_TOOL.md](../docs/LABELING_TOOL.md) Â§5B.
- JSON fÃ¥r `"legs": [ { "id": "leg_1", "high": ..., "low": ... }, ... ]`.
- Top-level `high`/`low` = leg_1 (bakÃ¥tkompatibilitet fÃ¶r motor/recall idag).

**Legacy-not:** Bitfinex/BTC-USD-labels har rensats bort frÃ¥n arkivet i den aktiva cleanup-rundan.

**Motor anvÃ¤nder inte** `legs[]` Ã¤n â€” endast research/golden. Se [MTF_DAILY_RESEARCH.md](../docs/MTF_DAILY_RESEARCH.md).

