# Fibonacci Research Experiment

En research-/prototyp-engine som försöker välja swing high/low på ett chart
**som en teknisk analytiker** — inte en vanlig Fib-indikator och inte standard
ZigZag-Fib. Den väljer swingar, ritar Fib automatiskt och förbättras iterativt.

> Status: MVP / prototyp / premortem. Lättviktig disciplin (logging, audits,
> reflektion) — ingen tung governance. Kan ev. portas in i Genesis-Core senare.

## Filosofi

- **Principer styr, exempel = referens.** Motorn poängsätter på analytiker-
  principer (fraktal-vändpunkter, HH/HL-struktur, ren impuls, prominens). Dina
  manuella Fib-ritningar är *exempel*, inte en domare — de visas som en mjuk
  `agreement`-signal för sanity, men vi optimerar **aldrig** vikter mot dem.
- **Mjuka, tunbara features — ingen hård determinism.** Marknadsstruktur m.m.
  matar den viktade poängsättningen istället för hårda `if`-grindar.
- **Lager A vs Lager B.** Lager A = swing-urvalet (repots syfte). Lager B =
  trade/exekvering (t.ex. solros-sizing) — frikopplat, påverkar inte urvalet.

## Snabbstart

```bash
uv sync --extra dev                          # bygg miljö + lockfile
uv run python -m fibengine.data.fetch        # hämta + cacha candles (CCXT)
uv run python -m fibengine.labeling.tool     # klicka swing high/low -> facit
uv run python -m fibengine.experiment        # kör pipeline + logga resultat
uv run python -m fibengine.backtest.runner   # kausalt walk-forward: urvals-stabilitet
uv run pytest                                 # kör tester
```

## Pipeline (Lager A)

```
candles → pivot-kandidater (window/fractal) → features (HH/HL-struktur +
        multi-skala-confluence) → viktad score → välj swing-leg → rita Fib
        → agreement vs exempel
```

Pivot-läge styrs av `pivots.mode` (`window` = lokala extrema, `fractal` = strikt
Williams). Vikter tunas på principgrund i `config/settings.yaml` — inte mot facit.

**Multi-skala-confluence** (`scale_confluence`): en sväng vars vändpunkter också
är fraktal-vändpunkter på större grader (`scoring.confluence_degrees`) får högre
poäng — signifikans över skalor, inte 1.618-mystik. Äkta multi-timeframe
(resampling till 4h/1D) är ett planerat senare steg.

## Backtest: urvals-stabilitet (Lager A)

`fibengine.backtest.runner` kör ett **kausalt walk-forward**: vid varje
cursor-position väljs swing på enbart data ≤ t (ingen framtid läcker in), och
stabiliteten mäts — `flip_rate`, `persistence_steps`, `direction_consistency`,
`mean_endpoint_drift_bars`. Mäter om motorn väljer koherent över tid (inte PnL;
det är Lager B). Notera: end-baren förlängs ofta en bar i taget under en trend,
vilket räknas som "ändring" — så hög `flip_rate` med hög `direction_consistency`
betyder oftast en *växande* sväng, inte regim-flipp.

## Struktur

- `config/settings.yaml` — symbol, pivot-läge, heuristik-vikter, eval-skalor, sizing, backtest
- `src/fibengine/` — kärnkod (data, pivots, structure, scale, features, scoring,
  fib, labeling, eval, viz) + `sizing/` (Lager B) + `backtest/` (urvals-stabilitet)
- `data/labels/` — manuellt facit (versioneras)
- `data/raw/`, `data/screenshots/` — cache resp. referensbilder (gitignorade)
- `experiments/` — per-körning audit-mappar + `leaderboard.jsonl`
- `premortem/` — premortem + reflektioner

## Arbetsflöde för facit

1. Labela dina setups med `labeling/tool.py` → exakta tid+pris sparas som JSON.
2. Arkivera TradingView-screenshots i `data/screenshots/` som visuell referens.
