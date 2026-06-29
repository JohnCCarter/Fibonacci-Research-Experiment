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

## Agent epistemic principles

Binding operating principles (not hints) — read with §1.

- **Research easy, authority hard.** Keep experiments cheap and fast (small, falsifiable, minimal
  ceremony — *not* mini-Genesis). Make *promotion to truth* expensive: a result becomes facit, a
  claim, or an edge only via pre-registration, OOS + matched controls, and explicit human sign-off.
  Low friction to explore; high bar to assert. Null results are first-class outcomes.
  **Locking mechanics:** when a prereg is signed off, add the `<!-- prereg:locked -->` sentinel to
  it and move all post-lock material (run results, addenda, status) into a `*-postlock.md` sibling
  so the registration itself stays immutable. A `PreToolUse` hook
  ([`.claude/hooks/guard-locked-prereg.sh`](.claude/hooks/guard-locked-prereg.sh)) asks before any
  Edit/Write to a sentinel-bearing file.
- **Validity over convenience.** When a decision admits ≥2 plausible baselines / controls / null
  models / feature definitions / tolerances / confirmation buffers / split or power rules, do **not**
  silently pick the easiest-to-code or result-convenient one. Name the alternatives, state the
  tradeoff, and either lock one with a methodological reason **before running** or pre-declare a
  small family the result must **survive**. **Never choose a baseline/control after seeing the
  result.** Smallest implementation is allowed only **after** validity is preserved.
- **Intent alignment over plan inertia.** A technically correct step — code runs, test well-formed,
  stats sound, matches the local spec — can still be the *wrong* work if it does not answer the
  human's actual claim. Before starting or continuing any research / implementation / audit path,
  be able to state: what is the user's real goal, what question does this step answer, are they the
  same, and if not what is the mismatch. **Re-check intent** when a line repeatedly returns
  null/inconclusive, when the user says "not what I meant," when the test answers a narrower or
  different question, when the work is correct but no longer useful, or when you are optimizing the
  current plan instead of the objective. Do not continue a correct path that answers the wrong
  question — pause and ask, or explicitly reframe. **Guardrail (interlocks with *Validity over
  convenience*):** this must never be used to chase positive results — changing the question after a
  null is valid *only* when the prior question is shown misaligned with the original claim, and the
  new question is stated explicitly (scope, baselines, non-claims) **before** any new run.

---

## 2. Source authority (how to treat evidence)

The wiki (`docs/research_wiki/`) is **agent-native warm context** — navigation
**and** accumulated knowledge for fast cross-session orientation — but **never
truth**. When the wiki and a source layer disagree, the **source wins** — fix the
wiki or flag the conflict (this guard matters *more* when the agent both writes and
reads its own memory). Full model:
[source-authority.md](docs/research_wiki/reference/source-authority.md);
purpose: [decisions/2026-06-17-wiki-is-agent-native.md](docs/research_wiki/decisions/2026-06-17-wiki-is-agent-native.md).

| Rule | Meaning |
|------|---------|
| Human fib = **facit** | Manual anchors/levels/events are ground truth |
| `*_candidate` ≠ facit | Machine suggestions stay candidates until human promotion |
| Wiki = agent memory | `docs/research_wiki/` is agent-native warm context (navigation + accumulated knowledge); **source code and docs** are behavior truth |
| Source authority | When wiki and source evidence disagree, **source wins** — fix or flag the wiki |
| Local config ≠ truth | `.claude/settings.local.json`, `.env`, caches, `data/raw/`, temp charts/logs are local-only — never wiki memory or source truth. `.claude/{commands,hooks,settings.json}` ARE versioned (portable across machines) |
| No auto-fib as truth | Do not promote automated fib selection to facit |
| No trading signals | Research engine only — no signal/edge claims in agent output |
| Tracks | Research → Validate → Promotion — see [TRACKS.md](docs/TRACKS.md) |
| Archive blobs | Local disk only; git tracks `archive/` stubs and `MANIFEST.md` — **never commit archive data unless the user explicitly asks** ([repository-layout-policy.md](repository-layout-policy.md) §7) |

---

## 3. Wiki maintenance (prevent stale memory)

The agent **curates** the wiki (the human asks questions); maintenance is
self-interest, not a chore — persist now so the next agent orients in milliseconds.
**Query the wiki before re-deriving methodology** (see
[concepts/](docs/research_wiki/concepts/) and
[reference/closed-questions.md](docs/research_wiki/reference/closed-questions.md)).

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
