# AGENTS.md

## Response style (read first)

**Default: compact.** Short answers; no long reports; show what changed (not whole files); max **10** bullets; status updates = **blockers + next step** only.

**Expand** when the user opts in (e.g. “förklara mer”, “det är ok att förklara”, “full rapport”) or when safety/correctness requires detail.

Full spec: [docs/agent/AGENT_RESPONSE_STYLE.md](docs/agent/AGENT_RESPONSE_STYLE.md) · Cursor rule: `.cursor/rules/agent-response-style.mdc`

## Repo-aware agent (all models, including BYOK Qwen in Chat)

**Policy:** Inspect the repo before implementation answers; separate facts from assumptions; minimal diffs; ask before edit when scope is unclear. Not a memory-only chatbot.

- Rule: `.cursor/rules/repo-aware-coding-agent.mdc` (`alwaysApply: true`)
- **Model collaboration (GLM lead + Qwen implement):** [docs/agent/MODEL_COLLABORATION.md](docs/agent/MODEL_COLLABORATION.md) · `/glm-plan` · `/qwen-implement`
- **Cursor workspace setup:** [docs/agent/CURSOR_WORKSPACE_AGENT.md](docs/agent/CURSOR_WORKSPACE_AGENT.md) · [.cursor/README.md](.cursor/README.md)
- Research context: `docs/research_wiki/index.md`, `handoff.md`

---

## Cursor Cloud specific instructions

### Product

**fibengine** is a Python research engine for human-like Fibonacci swing selection (Layer A). There is no web server or databaseâ€”workflows are CLI modules (`experiment`, `backtest`, `labeling`) plus an optional Matplotlib labeling GUI.

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

1. **Candles** — `uv run python -m fibengine.data.fetch` caches OHLCV under `data/raw/` (gitignored). Cache is not auto-refreshed; use `--refresh`. Labeling set: `uv run python -m fibengine.data.fetch --labeling-set --refresh`. Needs outbound HTTPS to Bitfinex via CCXT. If the API is blocked in the VM, either request egress for `api.Bitfinex.com` or populate `data/raw/` manually before running pipelines that call `load_candles()`.
2. **Experiment** â€” `uv run python -m fibengine.experiment` runs swing selection for all human labels in `data/labels/`, writes plots and `metrics.json` under `experiments/runs/experiment/<date>/<run_id>/`, and appends to `experiments/results/leaderboard.jsonl`.
3. **Labeling worklist** â€” `uv run python -m fibengine.labeling.worklist` (no network).
4. **Interactive labeler** â€” `uv run python -m fibengine.labeling.tool` needs a display/GUI backend (not typical in headless cloud VMs).

### Services

| Component | Required for | Notes |
|-----------|----------------|-------|
| `.venv` via `uv sync` | Everything | No Docker Compose in repo |
| `pytest` | CI / dev | Uses synthetic fixtures; no network |
| Bitfinex (CCXT) | Live fetch / fresh caches | Optional if `data/raw/` already populated |
| Matplotlib GUI | `labeling.tool` | Optional |

### Gotchas

- `load_candles(..., fetch_if_missing=True)` only fetches when cache is missing (never refreshes). Re-run `fibengine.data.fetch --refresh` for up-to-date bars.
- `load_candles(..., fetch_if_missing=True)` failures look like CCXT `NetworkError` / SSL errors if egress is blocked.
- Long timeframes use higher `timeframe_limits` in `config/settings.yaml`; labels can be `out_of_window` if history is too short (see experiment logs).
- Coverage gate is **60%** via pytest `addopts` in `pyproject.toml`; `labeling/tool.py` is omitted from coverage.

