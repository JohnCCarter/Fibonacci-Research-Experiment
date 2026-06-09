# CLAUDE.md

Kort orientering för Claude (och andra agenter). **Konstitution och guardrails:**
[`AGENTS.md`](AGENTS.md). Layout: [`repository-layout-policy.md`](repository-layout-policy.md).

## Läs först (i ordning)

1. [`AGENTS.md`](AGENTS.md) — roller, workflow, guardrails
2. [`docs/research_wiki/handoff.md`](docs/research_wiki/handoff.md) — aktuellt fokus
3. [`docs/BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md`](docs/BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md) — aktiv
   research: **BTC/USD**, **1M → 1w → 1d → 4h → 1h**
4. [`docs/README.md`](docs/README.md) — doc-karta (undermappar)
5. [`docs/research_wiki/reference/module-map.md`](docs/research_wiki/reference/module-map.md) —
   paketkarta

Wiki = navigation; **kod och käll-docs** = beteendes sanning.

## Projektöversikt

**fibengine** — Python research engine för mänskligt swing-urval (Lager A) och Fib.
CLI-moduler + valfri Matplotlib-labeling-GUI. Ingen webbserver/databas. Mer i
[`README.md`](README.md).

## Aktivt protokoll (2026-06-08+)

- Endast **BTC/USD** tills monthly→weekly→daily är godkänt
- **Human fib = facit**; `*_candidate` ≠ facit; ingen auto-fib som sanning
- Äldre mixed-symbol/MTF-resultat ligger i `archive/` — **inte** aktuell evidens
- **Arkiv:** lokalt på disk; committa **inte** arkivblobs om inte användaren ber om det
  ([`repository-layout-policy.md`](repository-layout-policy.md) §7)

## Paket (`src/fibengine/`)

`core/` · `data/` · `pivots/` · `evaluation/` · `backtest/` · `viz/` · `labeling/` ·
`research/` · `validation/` · `sizing/` (Lager B — håll frikopplat) · `experiment.py`

## Vanliga kommandon

```bash
uv sync --extra dev
uv run ruff check src tests
uv run pytest -q
uv run python scripts/check_repo_bounds.py
```

**Data & labeling (BTC):**

```bash
uv run python -m fibengine.labeling.preflight --symbol BTC/USD --timeframes "1M,1w,1d,4h,1h" --config config/settings.expansion.yaml
uv run python -m fibengine.labeling.tool --symbol BTC/USD --timeframe 1M --timeframes "1M,1w,1d,4h,1h" --symbols BTC/USD --config config/settings.expansion.yaml
uv run python -m fibengine.data.fetch --symbols BTC/USD --timeframes 1M,1w,1d --refresh
```

Kör **preflight** före GUI. TF-byte i tool hämtar **inte** cache automatiskt — saknad
cache → felmeddelande (kör fetch).

## Konventioner

- `uv run …` (inte bart `python`/`pip`)
- Variant-config: `--config config/variants/…` eller `settings.expansion.yaml` — ändra
  inte baseline `config/settings.yaml` i onödan
- Minimala diffs; fråga vid oklar facit/promotion
- Kompakta svar: [`docs/agent/AGENT_RESPONSE_STYLE.md`](docs/agent/AGENT_RESPONSE_STYLE.md)
- GLM planerar/reviewar, Qwen implementerar inom handoff —
  [`docs/agent/MODEL_COLLABORATION.md`](docs/agent/MODEL_COLLABORATION.md)

## Token-budget — sök/läs inte brett här

Avgränsat i [`.rgignore`](.rgignore) (filer kan finnas i git men ska inte grep:as):

- `archive/` — superseded blobs + gamla experiment
- `experiments/results/` — append-only jsonl
- `data/labels/**/*_events.json`, `*_interactions.csv` — regenererbart
- Gitignorade: `data/raw/`, `experiments/runs/`, `experiments/review/`, `.venv/`

**Facit att läsa vid behov:** `data/labels/human_fib/bitfinex/BTC-USD/**/fib_*.json`
(bara bas-JSON, inte hela `data/labels/` via blind grep).

## Gotchas

- `load_candles(..., fetch_if_missing=True)` refreshar aldrig — kör `data.fetch --refresh`
- Bitfinex/CCXT kräver egress; annars fyll `data/raw/` manuellt
- `labeling/tool.py` kräver GUI-backend
- Byt inte namn på kritiska moduler utan policy-uppdatering (§8 i layout-policy)
