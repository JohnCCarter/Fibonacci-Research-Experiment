# CLAUDE.md

Kort orienteringsfil för agenter. Detaljer ligger i länkade dokument — läs dem
vid behov istället för att utforska brett. Agent-svarsstil och pipeline-gotchas:
se [`AGENTS.md`](AGENTS.md). Layout/namnkonventioner: se
[`repository-layout-policy.md`](repository-layout-policy.md).

## Projektöversikt
**fibengine** är en Python-research-engine som väljer swing high/low "som en
analytiker" (Lager A = swing-urval) och ritar Fib automatiskt. Lager B (sizing)
är frikopplat. Ingen webbserver/databas — arbetsflöden är `python -m`-CLI-moduler
plus en valfri Matplotlib-labeling-GUI. Status: MVP/prototyp. Mer i
[`README.md`](README.md).

## Paket-karta (`src/fibengine/`)
- `core/` — domäntyper, fib-matte, config, scoring, structure, scale
- `data/` — OHLCV fetch/cache/load
- `pivots/` — pivot-detektion
- `evaluation/` — jämför prediktion vs labels
- `backtest/` — kausalt walk-forward, matriser, trade-experiment
- `viz/` — plottning
- `labeling/` — label-store, GUI, worklist, human-fib, behavior-facit, kandidater
- `research/` — level-event-detektor + human-review-verktyg
- `sizing/` — Lager B (håll frikopplat från Lager A)
- `validation/` — scheman
- `experiment.py` — huvud-runner

Fullständig karta: [`docs/research_wiki/reference/module-map.md`](docs/research_wiki/reference/module-map.md).

## Entrypoints (kör via uv)
- `uv run python -m fibengine.experiment` — huvudpipeline
- `uv run python -m fibengine.data.fetch [--refresh] [--labeling-set]` — candles (CCXT/Bitfinex)
- `uv run python -m fibengine.backtest.runner` / `.matrix`
- `uv run python -m fibengine.labeling.{worklist,autolabel,tool,batch}`

Inga console_scripts definieras i `pyproject.toml` — använd `python -m`.

## Viktiga kommandon
- Setup: `uv sync --extra dev`
- Lint: `uv run ruff check src tests`
- Format: `uv run ruff format src tests`  (CI kör `--check`)
- Test: `uv run pytest -q`  (coverage-gate 60 %, `pythonpath=src`)
- Repo-bounds: `uv run python scripts/check_repo_bounds.py`
- Build: `uv build`
- Före push: `uv run pre-commit run --all-files`
- Ingen typecheck konfigurerad (ingen mypy/pyright).

## Konventioner (föredra X framför Y)
- Föredra `uv run …` framför bart `python`/`pip`.
- Föredra en variant under `config/variants/*.yaml` med `--config` framför att
  ändra baseline `config/settings.yaml`.
- Föredra att hålla moduler inom storleksgränserna (`check_repo_bounds.py`) och
  att dela upp stora filer framför att låta dem växa.
- Föredra `git mv` vid flytt (bevara historik) och uppdatera berörda
  `README.md`/`INDEX.md`.
- Föredra tester som speglar `src/`: `tests/<pkg>/test_<modul>.py`.
- Föredra att hålla `sizing/` (Lager B) frikopplat från swing-urval (Lager A).
- Föredra mänskliga labels som facit; maskin-labels (`source="machine"`) hålls
  utanför metrics och 20–30-målet.
- Föredra kompakta svar (se `AGENTS.md` response-style); expandera på begäran.
- Föredra att starta i ett index
  ([`docs/research_wiki/index.md`](docs/research_wiki/index.md), `module-map.md`)
  framför att grep:a brett.

## Läs/rör INTE detta (token-budget)
- Grep:a/läs **inte** `archive/` (~19 MB arkiverade artefakter). Avgränsat i
  `.rgignore`.
- Läs **inte** ledgers/labels rad-för-rad: `experiments/results/*.jsonl`,
  `data/labels/**` — använd `fibengine.research.ledger_query` eller läs bara
  struktur. Avgränsade i `.rgignore`.
- Ignorera (gitignorade) `data/raw/`, `data/screenshots/`, `experiments/runs/`,
  `experiments/review/`, `.venv/`, cache-kataloger, `tmp/`.
- Byt **inte** namn på kritiska moduler utan policy-/doc-uppdatering
  (`repository-layout-policy.md` §8): `core/fib.py`, `core/models.py`,
  `core/scoring.py`, `labeling/human_fib.py`, `labeling/human_fib_events.py`,
  `research/level_events.py`, `labeling/tool.py`.

## Gotchas
- `load_candles(..., fetch_if_missing=True)` hämtar bara om cache saknas — aldrig
  refresh. Kör `fibengine.data.fetch --refresh` för färska barer.
- Nät-fel mot Bitfinex/CCXT ser ut som `NetworkError`/SSL om egress är blockerad;
  populera `data/raw/` manuellt vid blockerad nät.
- `labeling/tool.py` kräver GUI-backend (ej i headless-VM) och är undantagen coverage.
