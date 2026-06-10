# Fibonacci Research Experiment

En research-/prototyp-engine som försöker välja swing high/low på ett chart
**som en teknisk analytiker** — inte en vanlig Fib-indikator och inte standard
ZigZag-Fib. Den väljer swingar, ritar Fib automatiskt och förbättras iterativt.

> Status: MVP / prototyp / premortem. Lättviktig disciplin (logging, audits,
> reflektion) — ingen tung governance. Kan ev. portas in i Genesis-Core senare.

> Organisation: se [`repository-layout-policy.md`](repository-layout-policy.md) för mappindex, namnkonventioner
> och städningsregler.
> Premortem/reflektion är obligatoriskt: se `premortem/` och `repository-layout-policy.md` §11.
> Spårmodell: se `docs/TRACKS.md` (Research / Validate / Promotion).
> Backtest-roadmap: [`docs/validate/FIB_BACKTEST_PLAN.md`](docs/validate/FIB_BACKTEST_PLAN.md).
> Bitfinex / Genesis validate: [`docs/validate/GENESIS_BITFINEX_VALIDATE.md`](docs/validate/GENESIS_BITFINEX_VALIDATE.md).
> Arkiv (legacy/dubletter): [`archive/`](archive/README.md).

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
uv run python -m fibengine.data.fetch --labeling-set --refresh  # BTC/ETH/SOL 1w+1d till idag
uv run python -m fibengine.labeling.worklist # vad återstår att labela mot 20–30-målet
uv run python -m fibengine.labeling.autolabel # maskin-kandidater (source=machine) att granska
uv run python -m fibengine.labeling.tool     # klicka swing high/low -> facit
uv run python -m fibengine.labeling.batch    # lättviktig label-checkpoint (manifest/hashar)
uv run python -m fibengine.experiment        # kör pipeline + logga resultat
uv run python -m fibengine.backtest.runner   # kausalt walk-forward: urvals-stabilitet
uv run python -m fibengine.backtest.matrix   # stabilitet över symbol/timeframe-matris
uv run pytest                                 # kör tester
uv run pre-commit install                     # git hooks (en gång)
uv run pre-commit run --all-files             # lint + format + test före push
```

Kvalitetsgate: CI i `.github/workflows/ci.yml` (ruff + pytest på push/PR mot `main`).

Använd `--config` för en principmotiverad variant under `config/variants/` utan att ändra baseline:

```bash
uv run python -m fibengine.experiment --config config/variants/<profil>.yaml
uv run python -m fibengine.backtest.runner --config config/variants/<profil>.yaml
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
stabiliteten mäts. `flip_rate` räknar bara *riktiga hopp* — en sväng vars
endpunkt växer en bar i taget (samma start/riktning) klassas som `extension_rate`,
inte instabilitet. `raw_change_rate` behålls för transparens, och `confirmed_rate`
visar hur ofta den valda swingen var bekräftad. Mäter koherens över tid, inte PnL
(det är Lager B).

**Stabilitets-gate.** Backtest/matris kör en explicit pass/fail-gate
(`stability_gate`) där `mean_endpoint_drift_bars` är en **förstklassig** kriterie vid
sidan av `flip_rate`/`confirmed_rate`/`direction_consistency` — en "stabil" swing vars
endpunkt ändå vandrar långt vid hopp är ekonomiskt instabil. Trösklarna sätts i
`config/settings.yaml` (`backtest.gate_*`); resultatet skrivs som `gate_passed` +
`gate_checks` i ledgern.

**Bekräftad vs provisorisk swing:** varje vald swing får `status`. *Provisorisk* =
extremen kan fortfarande växa (för få barer efter, eller ingen pullback ännu).
*Bekräftad* = minst `pivots.fractal_n` barer efter extremen OCH priset har dragit
tillbaka ≥ `scoring.confirm_min_retrace` av legen. Agera bara på bekräftade Fib;
provisoriska ritas streckade i plotten.

## Struktur

- `config/settings.yaml` — symbol, pivot-läge, heuristik-vikter, eval-skalor, sizing,
  backtest + stabilitets-gate (`backtest.gate_*`). `data.timeframe_limits` laddar mer
  historik för långa TF (1d/1w/1M) så äldre labels inte hamnar out-of-window
- `src/fibengine/` — kategoriserad kärnkod: `core/` (domänlogik), `data/`,
  `pivots/`, `labeling/`, `evaluation/`, `viz/`, `backtest/`, `sizing/` + `experiment.py`
- `tests/` — speglar `src/fibengine/`-strukturen (inkl. `tests/core/`,
  `tests/backtest/`, `tests/data/`, `tests/evaluation/`, `tests/labeling/`,
  `tests/pivots/`, `tests/sizing/`, `tests/viz/`)
- `data/labels/` — manuellt facit (`{exchange}/{symbol}/{timeframe}.json` + `INDEX.md`)
- `data/raw/`, `data/screenshots/` — cache resp. referensbilder (gitignorade)
- `experiments/results/` — append-only jsonl-ledgers (pivot_recall, backtests,
  trade_backtests, backtest_matrix, trade_matrix, leaderboard)
- `experiments/runs/` — per-körning audit-mappar
- `experiments/label_review/` — versionerade label-checkpoints
- `premortem/` — premortem + reflektioner (`reflections/`)
- `docs/TRACKS.md` — beslutsgate mellan Research, Validate och Promotion

## Arbetsflöde för facit

Viktigt: dina TradingView-ritningar är inte "den heliga sanningen" och ska inte
kopieras blint. De är mänskliga referenspunkter för att se om motorn hittar
rimliga kandidater och beter sig begripligt. Om motorn ibland väljer en annan
leg än en ritning är det en signal att undersöka, inte automatiskt ett fel.

1. Labela dina setups med `labeling/tool.py` → exakta tid+pris sparas som JSON.
2. Arkivera TradingView-screenshots i `data/screenshots/` som visuell referens.

### Maskin-labeling (kandidater, inte facit)

Två giltiga frågor (motor-swing vs synligt chartfönster) — se
[`docs/labeling/MACHINE_LABELING.md`](docs/labeling/MACHINE_LABELING.md).

`labeling/autolabel.py` kan generera **provisoriska** swing-kandidater
(`source="machine"`) från motorns eget urval, så att du slipper börja från ett
tomt chart. Tre hårda regler skyddar facit-integriteten:

- Maskin-labels **exkluderas** från recall/agreement (`pivot_recall`, `experiment`)
  och räknas **inte** mot 20–30-målet — annars mäter vi motorn mot sin egen output.
- En befintlig **mänsklig** label skrivs aldrig över.
- Öppna kandidaten i `labeling.tool`, granska/justera och tryck `s` → den sparas som
  `source="human"` (befordran). Rubrikstämpla aldrig en ogranskad kandidat som facit.
