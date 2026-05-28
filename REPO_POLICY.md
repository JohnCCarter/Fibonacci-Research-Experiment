# Repo Policy

Hur det här repot ska hållas organiserat över tid. Pragmatisk, inte byråkratisk.
Allt nytt arbete ska följa indexet nedan. Fungerar något annorlunda i praktiken
— uppdatera policyn först, inte tvärtom.

## 1. Mappindex

| Mapp | Syfte | Versionshanteras? |
|---|---|---|
| `src/fibengine/` | Produktionskod (motorn) | Ja |
| `tests/` | Tester (speglar `src/fibengine/`-strukturen, se §4) | Ja |
| `config/` | Körningskonfiguration (`settings.yaml`) | Ja |
| `config/variants/` | Alternativa settings-profiler + `INDEX.md` | Ja |
| `data/labels/` | Manuell facit (golden set) | Ja |
| `data/raw/` | Cachad rådata från CCXT + `INDEX.md` | Nej (gitignore) |
| `data/screenshots/` | Referensbilder + `INDEX.md` | Nej (gitignore) |
| `experiments/results/` | Append-only jsonl-ledgers (se §5) | Ja |
| `experiments/runs/` | Per-körning audit-mappar + `INDEX.md` | Selektivt (se §5) |
| `experiments/label_review/` | Versionerade label-checkpoints | Ja (se §5) |
| `premortem/` | Premortem + reflektioner | Ja |
| `premortem/reflections/` | Datums-stämplade reflektioner | Ja |
| `docs/` | Frivilliga djupare dokument | Ja (om det skapas) |
| `archive/` | Arkiverat material (dubletter, legacy paths, ersatta docs) | Ja |
| `tmp/` | Tillfälliga skript/artefakter | Valfritt (se §9) |

Toppnivån ska bara innehålla: `README.md`, `REPO_POLICY.md`, `pyproject.toml`,
`uv.lock`, `.gitignore`, och dessa mappar. **Inga stub-filer** som bara pekar
bort flyttat innehåll — uppdatera länkar till canonical path (t.ex. `docs/FIB_BACKTEST_PLAN.md`).
Tillfälliga filer läggs i `tmp/`.

## 1A. Tre spår (MÅSTE)

Allt arbete i repot ska kunna klassas i exakt ett av dessa spår:

1. **Research / Experiment**
2. **Validate**
3. **Promotion**

Definitioner och gate finns i `docs/TRACKS.md`. Vid tvekan: behandla ändringen
som Research tills Validate-kriterier uppfyllts.

### Spårkoppling till repo-ytor

- **Research / Experiment**
  - `config/variants/`
  - `src/fibengine/tuning/`
  - `experiments/runs/optuna/`
  - `experiments/label_review/`
  - `premortem/reflections/`

- **Validate**
  - `tests/`
  - `experiments/runs/stability/`
  - `experiments/results/pivot_recall.jsonl`
  - `experiments/results/backtests.jsonl`
  - `experiments/results/backtest_matrix.jsonl`

- **Promotion**
  - `config/settings.yaml` (canonical baseline)
  - `src/fibengine/core/` och etablerad runtime-surface
  - `README.md` + policydokument

## 2. `src/fibengine/` modulindex

Varje modul ska ha ett tydligt ansvar. Inga “utils.py” utan kategori.

| Modul | Ansvar |
|---|---|
| `core/config.py` | Settings-loading + validering |
| `core/models.py` | Dataklasser (Pivot, Swing) |
| `data/` | Hämta + ladda candles |
| `pivots/` | Pivot-detektering (Lager A) |
| `core/scale.py` | Multi-skala confluence |
| `core/structure.py` | HH/HL marknadsstruktur |
| `core/features.py` | Per-swing features |
| `core/scoring.py` | Viktad leg-poängsättning + select_swing |
| `core/confirm.py` | Bekräftad vs provisorisk swing |
| `core/fib.py` | Fib-nivå-beräkning |
| `evaluation/` | Mätning mot labels (Lager A diagnostics) |
| `labeling/` | Label-verktyg + lagring + batch |
| `backtest/` | Walk-forward stabilitet + trade-backtest |
| `sizing/` | Solros sizing (Lager B) |
| `tuning/` | Experimentell parameteroptimering (Optuna m.m.) |
| `viz/` | Plot-funktioner |
| `experiment.py` | Standardrunner som loggar till `experiments/runs/` |
| `core/logging_conf.py` | Loguru-setup |

## 3. Namnkonventioner

- **Filer i kod:** `snake_case.py`.
- **Tester:** `test_<modulnamn>.py`.
- **Label-filer:** `{exchange}/{symbol-with-dash}/{timeframe}.json` under `data/labels/`.
  Legacy platt format på rot (`{exchange}_{symbol}_{timeframe}.json`) läses fortfarande vid migration.
- **Run-id:** `{kind}_{YYYYMMDDTHHMMSSZ}` (`run_`, `bt_`, `pivot_recall_` etc.).
- **Batch-id:** `YYYY-MM-DD_kort-beskrivning` (t.ex. `2026-05-28_round6_locked`).
  Auto-genererade default-id (typ `2026-05-28_label_batch_115215`) räknas som
  temporära och bör inte sparas i Git över tid.

## 3A. Hårda strukturkrav (MÅSTE)

Detta är **obligatoriskt** för att repot ska räknas som organiserat:

1. **`data/raw/` MÅSTE** använda:
   `data/raw/{exchange}/{symbol}/{timeframe}/limit_{n}.csv`
2. **`data/screenshots/` MÅSTE** använda:
   `data/screenshots/{source}/{symbol}/{timeframe}/{filename}.png`
3. **`experiments/runs/` MÅSTE** använda:
   `experiments/runs/{kind}/{YYYY-MM-DD}/{run_id}/`
   där `kind ∈ {experiment, stability, optuna, archive}`.
4. **Indexfiler MÅSTE finnas och hållas uppdaterade**:
   - `data/raw/INDEX.md`
   - `data/screenshots/INDEX.md`
   - `experiments/runs/INDEX.md`
   - `data/labels/INDEX.md`
   - `experiments/label_review/INDEX.md`
5. **README MÅSTE finnas** i dessa mappar:
   - `data/raw/`, `data/screenshots/`, `experiments/runs/`,
     `experiments/label_review/`, `data/labels/`
6. **`config/settings.yaml` är baseline (MÅSTE)**:
   - ska inte överlagras av tuning-runs.
   - nya kandidater sparas i `config/variants/*.yaml`.
   - `config/variants/INDEX.md` ska uppdateras när en ny variant läggs till.

## 4. Tester

- Varje ny modul i `src/fibengine/` ska ha minst ett test i `tests/`.
- **Strukturen speglar `src/fibengine/`:** tests för en sub-package läggs i samma
  sub-mapp (`src/fibengine/backtest/runner.py` → `tests/backtest/test_backtest.py`).
  Kärnmoduler under `src/fibengine/core/` testas i `tests/core/`
  (`src/fibengine/core/config.py` → `tests/core/test_config.py`).
- Filnamn: `test_<modulnamn>.py`.
- Inga `__init__.py` i tests-mapparna (pytest plockar upp dem rekursivt via
  `testpaths = ["tests"]` i `pyproject.toml`).
- Tester ska köra utan nätverk. Mocka CCXT/data där det behövs.
- Köras med `uv run pytest`. Måste vara grönt innan commit.
- **Validate-gate:** En Research-kandidat får inte promoted status utan
  reproducerbar validate-körning + gröna tester.

## 5. `experiments/` — vad sparas, vad är tillfälligt

Detta är den mapp som lättast bloatar. Tydliga regler. Strukturen är:

```
experiments/
  results/         ← jsonl-ledgers (append-only)
  runs/            ← audit-mappar per körtyp/datum + INDEX
    experiment/YYYY-MM-DD/run_...
    stability/YYYY-MM-DD/bt_...
    optuna/YYYY-MM-DD/optuna_...
  label_review/    ← versionerade label-checkpoints
```

### Sparas (versionshanteras)

**`experiments/results/`** — append-only jsonl-ledgers, en rad per körning:
- `pivot_recall.jsonl` — pivot-kvalitet vs labels
- `backtests.jsonl` — walk-forward stabilitet (Lager A)
- `trade_backtests.jsonl` — trade-ekonomi (Lager B)
- `backtest_matrix.jsonl` — sweep över symbol/timeframe för stabilitet
- `trade_matrix.jsonl` — sweep över symbol/timeframe för trade-ekonomi
- `leaderboard.jsonl` — sammanfattning av `python -m fibengine.experiment`-körningar
- `optuna_trials.jsonl` — trial-utfall från `python -m fibengine.tuning.optuna_runner`
- `optuna_best.json` — senaste bästa Optuna-resultat (överskrivs med senaste körning)

**`experiments/label_review/batches/<batch_id>/`** — där `batch_id` följer §3:
- `metadata.json`
- `labels_manifest.json`
- `notes.md`
- `INDEX.md` i `experiments/label_review/` listar aktiva batchar.

### Sparas inte / städas
- `experiments/runs/<kind>/<YYYY-MM-DD>/<run_id>/` — per-körning audit.
  Behåll bara senaste 5–10 mest relevanta. Resten kan tas bort när jsonl-raderna
  räcker som spår.
- Auto-genererade `label_review_*Z`-mappar med många `Figure_*.png` — räknas som
  artefakter, inte källa. Får tas bort när de inte längre används.
- `smoke-*`, `tmp-*`, `test-*` batch-id — alltid temporära, ska bort efter användning.
- `*.png` på toppnivå i en label_review-mapp utan kontext — räknas som rester
  från manuella `plt.savefig`. Får tas bort.

### `experiments/label_review/<batch_id>/labels_snapshot/`
Skapas bara om man kör `uv run python -m fibengine.labeling.batch --copy-labels`.
Default är manifest-only. Använd `--copy-labels` sparsamt och bara för milstolpar.

## 6. `data/labels/` — arbetssätt

- Detta är **golden set / working copy**. Sparas via `labeling.tool`.
- Kategoriserad struktur: `data/labels/{exchange}/{symbol}/{timeframe}.json`.
- `data/labels/INDEX.md` ska hållas uppdaterad vid större tillägg (kan genereras från `iter_label_files()`).
- Inga manuella ändringar i JSON utan att labeln går igenom verktygets valideringar
  (se `_label_warnings` i `labeling/tool.py`):
  - `high` och `low` får inte ligga på samma candle.
  - Ingen punkt får ligga inom `lookback` barer från vänster eller höger edge.
- Vid större omlabling: skapa en `batch` först, så det går att gå tillbaka.

## 7. Toppnivå-dokument

| Fil | Roll |
|---|---|
| `README.md` | Översikt + snabbstart |
| `REPO_POLICY.md` | Denna policy |
| `docs/FIB_BACKTEST_PLAN.md` | Backtest-roadmap (faser, status, kommandon) |
| `archive/` | Allt arkiverat material; se `archive/README.md` + `archive/INDEX.md` |
| `pyproject.toml`, `uv.lock` | Beroenden |

Lägg inga nya markdown-dokument på toppnivå utan kategori. Skapa `docs/`
om det blir fler än 3 sådana.

## 8. Dependencies

- Inga dependencies utan motivering. Lägg till via `uv add ...` så `pyproject.toml`
  och `uv.lock` hålls samstämda.

## 8A. Quality gate (MÅSTE före push)

Lokal check och CI ska matcha. Se `docs/CONTRIBUTING.md`.

1. `uv sync --extra dev`
2. `uv run pre-commit run --all-files` (eller `ruff check`, `ruff format --check`, `pytest`)
3. GitHub Actions: `.github/workflows/ci.yml`

Installera hooks en gång: `uv run pre-commit install`.
- Nya tunga dependencies (UI, optimering, ML) ska kort dokumenteras i README:s
  beroendelista och i policy om de byter på arbetsflödet.

## 9. Tillfälliga skript / debug

- `tmp` är **tillåtet**.
- Lägg tillfälliga skript/artefakter i `tmp/` (inte på toppnivå).
- Namnkonvention: `tmp_<beskrivning>.py` eller datums-prefix, t.ex.
  `2026-05-28_tmp_sweep.py`.
- Om ett script blir långlivat eller återanvändbart: flytta in i `src/fibengine/...`
  med riktigt namn och test.

## 10. Städningsritual

Kör manuell `repo housekeeping` vid behov:

1. Lista innehåll i `experiments/label_review/` (endast `batches/`, `packs/` ska ligga kvar).
   Flytta `smoke-*`, rot-dubletter, `label_review_*Z` och liknande till
   `archive/experiments/label_review/`; uppdatera `archive/INDEX.md`.
2. Legacy `experiments/*.jsonl` på fel path → `archive/experiments/ledgers/<datum>-…/`;
   canonical ledger: `experiments/results/`.
3. Lista innehåll i `experiments/runs/`. Behåll de senaste ~10. Resten kan tas
   bort när jsonl-raderna är tillräckliga (eller flytta till `archive/experiments/runs/` om ni versionerar dem).
4. Sök efter lösa `tmp_*.py` i repo-roten och flytta dem till `tmp/`.
5. Inga stub-markdown på toppnivå efter flytt till `docs/` — radera stub, länka canonical.
6. Kör `uv run pytest` för att säkerställa att städningen inte tog något viktigt.

## 11. Premortem & reflektion (MÅSTE)

Premortem-tänk och reflektion är en **obligatorisk del** av arbetsflödet.

### Hårda krav

1. **Innan större ändring/tuning** ska risk/hypotes vara uttryckt i
   `premortem/PREMORTEM.md` eller en ny reflektion.
2. **Efter varje betydande körning/beslut** (t.ex. ny batch av labels, ny vikt-tuning,
   ny backtest-matris) ska minst en reflektion skrivas i
   `premortem/reflections/`.
3. Filnamn i `premortem/reflections/` **MÅSTE** följa:
   `YYYY-MM-DD-<kort-beskrivning>.md`
4. Reflektionen **MÅSTE** innehålla:
   - Hypotes
   - Scope (symbol/timeframe/data)
   - Observationer (nyckelmetrics)
   - Beslut
   - Nästa steg

### Miniminivå per vecka

- Minst **en** ny reflektion per aktiv vecka där experiment körs.

## 12. Skriva på policyn

Policyn ändras genom att uppdatera den här filen direkt. Vid större ändringar i
struktur eller arbetsflöde: uppdatera först, sen flytta filerna. Aldrig tvärtom.

## 13. Promotion-gate (MÅSTE)

Något får bara klassas som **trusted engine behavior** när alla punkter är uppfyllda:

1. Ursprunglig kandidat finns i Research-spåret (t.ex. `config/variants/` eller tuning-run).
2. Validate-evidens finns (relevanta körningar i `experiments/results/`/`experiments/runs/stability/`).
3. `uv run pytest` är grönt.
4. Kort reflektion i `premortem/reflections/` dokumenterar beslutet.
5. Först därefter får ändringen in i Promotion-ytan (t.ex. `config/settings.yaml`).
