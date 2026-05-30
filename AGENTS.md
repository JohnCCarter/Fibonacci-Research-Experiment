# AGENTS.md

## Cursor Cloud specific instructions

### Product

**fibengine** is a Python research engine for human-like Fibonacci swing selection (Layer A). There is no web server or database—workflows are CLI modules (`experiment`, `backtest`, `labeling`) plus an optional Matplotlib labeling GUI.

### Dependencies (automatic on VM startup)

The update script runs `uv sync --extra dev`, which creates/updates `.venv` from `pyproject.toml` / `uv.lock`. Python **3.11+** is required (CI and local use 3.12).

### Lint / test / build (match CI)

From repo root:

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest -q
uv build
```

Optional local gate (same hooks as documented in README): `uv run pre-commit run --all-files`.

### Running the main pipeline (hello-world)

1. **Candles** — `uv run python -m fibengine.data.fetch` caches OHLCV under `data/raw/` (gitignored). This needs outbound HTTPS to Binance via CCXT. If the API is blocked in the VM, either request egress for `api.binance.com` or populate `data/raw/` manually before running pipelines that call `load_candles()`.
2. **Experiment** — `uv run python -m fibengine.experiment` runs swing selection for all human labels in `data/labels/`, writes plots and `metrics.json` under `experiments/runs/experiment/<date>/<run_id>/`, and appends to `experiments/results/leaderboard.jsonl`.
3. **Labeling worklist** — `uv run python -m fibengine.labeling.worklist` (no network).
4. **Interactive labeler** — `uv run python -m fibengine.labeling.tool` needs a display/GUI backend (not typical in headless cloud VMs).

### Services

| Component | Required for | Notes |
|-----------|----------------|-------|
| `.venv` via `uv sync` | Everything | No Docker Compose in repo |
| `pytest` | CI / dev | Uses synthetic fixtures; no network |
| Binance (CCXT) | Live fetch / fresh caches | Optional if `data/raw/` already populated |
| Matplotlib GUI | `labeling.tool` | Optional |

### Gotchas

- `load_candles(..., fetch_if_missing=True)` will call the exchange when cache is missing—failures look like CCXT `NetworkError` / SSL errors if egress is blocked.
- Long timeframes use higher `timeframe_limits` in `config/settings.yaml`; labels can be `out_of_window` if history is too short (see experiment logs).
- Coverage gate is **60%** via pytest `addopts` in `pyproject.toml`; `labeling/tool.py` is omitted from coverage.
