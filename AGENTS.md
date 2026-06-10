# CONSTITUTION FOR AGENTS

This file is the **canonical constitution** for every automated agent that works
in this repository (Cursor, Copilot, Cloud Agents). It defines **duties,
guardrails, and the source-authority model**.

Wiki maintenance discipline lives in
[`.cursor/rules/research-wiki-maintenance.mdc`](.cursor/rules/research-wiki-maintenance.mdc);
source authority lives in
[`docs/research_wiki/reference/source-authority.md`](docs/research_wiki/reference/source-authority.md).

---

## 1. Duties of every agent

| Duty | Requirement |
|------|-------------|
| **Inspect first** | Read relevant code, docs, wiki (`handoff.md`, `log.md`) before answers or edits |
| **Facts vs assumptions** | Label **Observed** (repo/output) vs **Assumption**; do not guess missing behavior |
| **Minimal diffs** | Smallest correct change; no drive-by refactors |
| **Ask before scope creep** | Unclear facit, promotion, or research impact → stop and ask |
| **Response style** | Compact by default — [AGENT_RESPONSE_STYLE.md](docs/agent/AGENT_RESPONSE_STYLE.md) |
| **Verify** | After code changes: `uv run ruff check src tests` and `uv run pytest -q` |

Enforcement: [`.cursor/rules/`](.cursor/rules/) (`alwaysApply`).

---

## 2. Source authority (how to treat evidence)

The wiki (`docs/research_wiki/`) is **navigation and synthesis**, never truth.
When the wiki and a source layer disagree, the **source wins** — fix the wiki or
flag the conflict. Full model:
[source-authority.md](docs/research_wiki/reference/source-authority.md).

| Rule | Meaning |
|------|---------|
| Human fib = **facit** | Manual anchors/levels/events are ground truth |
| `*_candidate` ≠ facit | Machine suggestions stay candidates until human promotion |
| Wiki = navigation | `docs/research_wiki/` synthesizes; **source code and docs** are behavior truth |
| Source authority | When wiki and source evidence disagree, **source wins** — fix or flag the wiki |
| Local config ≠ truth | `.claude/`, `.env`, caches, `data/raw/`, temp charts/logs are local-only — never wiki memory or source truth |
| No auto-fib as truth | Do not promote automated fib selection to facit |
| No trading signals | Research engine only — no signal/edge claims in agent output |
| Tracks | Research → Validate → Promotion — see [TRACKS.md](docs/TRACKS.md) |
| Archive blobs | Local disk only; git tracks `archive/` stubs and `MANIFEST.md` — **never commit archive data unless the user explicitly asks** ([repository-layout-policy.md](repository-layout-policy.md) §7) |

---

## 3. Wiki maintenance (prevent stale memory)

After meaningful research/labeling/review work: update the smallest relevant page
under `docs/research_wiki/`, link it from `index.md`, append one `log.md` entry,
and update `handoff.md` if focus/next-action/blockers changed. Skip for trivial
Q&A or mechanical changes. Rule:
[research-wiki-maintenance.mdc](.cursor/rules/research-wiki-maintenance.mdc).

The repo-bound contract is enforced by
[`scripts/check_repo_bounds.py`](scripts/check_repo_bounds.py) (file-size limits,
required wiki/schema files exist, no local/private artifact tracked) — run in CI.

---

## 4. Navigation map

| Need | Go to |
|------|--------|
| **Claude quick start** | [CLAUDE.md](CLAUDE.md) — orientation + `.rgignore` token budget |
| Current focus / next step | [research_wiki/handoff.md](docs/research_wiki/handoff.md) |
| Source authority | [research_wiki/reference/source-authority.md](docs/research_wiki/reference/source-authority.md) |
| Doc categories | [docs/README.md](docs/README.md) |
| Response style | [docs/agent/AGENT_RESPONSE_STYLE.md](docs/agent/AGENT_RESPONSE_STYLE.md) |

---

## Appendix A — Product and quality gate (all agents)

**fibengine** is a Python research engine for human-like Fibonacci swing selection
(Layer A). CLI workflows (`experiment`, `backtest`, `labeling`) plus optional Matplotlib
labeling GUI. No web server or database.

From repo root (match CI):

```bash
uv run python scripts/check_repo_bounds.py
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest -q
uv build
```

Optional: `uv run pre-commit run --all-files` · Python **3.11+** via `uv sync --extra dev`.

**Hello-world pipeline**

1. `uv run python -m fibengine.data.fetch` — cache OHLCV under `data/raw/` (`--refresh` for updates)
2. `uv run python -m fibengine.experiment` — swing selection vs `data/labels/`
3. `uv run python -m fibengine.labeling.worklist` — worklist (no network)
4. `uv run python -m fibengine.labeling.tool` — GUI (needs display)

**Gotchas:** `load_candles(..., fetch_if_missing=True)` fetches only when cache is missing;
coverage gate **60%** (`pyproject.toml`); long TF limits in `config/settings.yaml`.

---

## Appendix B — Cloud VM

Cloud startup runs `uv sync --extra dev`. Bitfinex egress may be blocked — populate
`data/raw/` manually or allow `api.bitfinex.com`. Headless VMs typically skip the
`labeling.tool` GUI.
