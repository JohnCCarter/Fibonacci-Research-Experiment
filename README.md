# Fibonacci Research Experiment

En research-/prototyp-engine som försöker välja swing high/low på ett chart
**som en teknisk analytiker** — inte en vanlig Fib-indikator och inte standard
ZigZag-Fib. Den väljer swingar, ritar Fib automatiskt, jämförs mot manuella
ritningar (facit) och förbättras iterativt.

> Status: MVP / prototyp / premortem. Lättviktig disciplin (logging, audits,
> reflektion) — ingen tung governance. Kan ev. portas in i Genesis-Core senare.

## Snabbstart

```bash
uv sync --extra dev                          # bygg miljö + lockfile
uv run python -m fibengine.data.fetch        # hämta + cacha candles (CCXT)
uv run python -m fibengine.labeling.tool     # klicka swing high/low -> facit
uv run python -m fibengine.experiment        # kör pipeline + logga resultat
uv run pytest                                 # kör tester
```

## Pipeline

```
candles → pivot-kandidater → features → viktad score → välj swing-par
        → rita Fib → jämför mot facit → iterera vikter
```

## Struktur

- `config/settings.yaml` — exchange, symbol, timeframe, heuristik-vikter, toleranser
- `src/fibengine/` — kärnkod (data, pivots, features, scoring, fib, labeling, eval, viz)
- `data/labels/` — manuellt facit (versioneras)
- `data/raw/`, `data/screenshots/` — cache resp. referensbilder (gitignorade)
- `experiments/` — per-körning audit-mappar + `leaderboard.jsonl`
- `premortem/` — premortem + reflektioner

## Arbetsflöde för facit

1. Labela dina setups med `labeling/tool.py` → exakta tid+pris sparas som JSON.
2. Arkivera TradingView-screenshots i `data/screenshots/` som visuell referens.
