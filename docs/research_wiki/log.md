# Research Wiki Log

Append-only trail of wiki ingests, decisions, and review sessions.

Use headings like:

```text
## [YYYY-MM-DD] type | Short title
```

Types: `ingest`, `decision`, `review`, `question`, `maintenance`.


> Older entries: [log-archive-pre-btc-reset-part1.md](log-archive-pre-btc-reset-part1.md)

## [2026-06-08] decision | Research reset â€” BTC monthly-first protocol

Archived 480 generated files to
`archive/research_superseded/2026-06-08_pre_btc_monthly_reset/` (runs, results,
review packs, label_review batch, wiki reviews). Code/tests/facit kept. New protocol:
[docs/BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md](../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md).
Manifest: [MANIFEST.md](../../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/MANIFEST.md).

## [2026-06-08] maintenance | Cursor agent shell â€” full alignment pass (branch)

Single review session on `feature/research-fib`: constitution (`AGENTS.md`), doc map
(`docs/agent/INDEX.md`), then `.cursor/rules` â†’ `hooks` â†’ `commands` â†’ `agents`.
Principle: constitution canonical; rules/hooks/commands/subagents = enforcement layers;
GLM/Qwen workflow for non-trivial code only (Auto uses rules + `/repo-agent`).
Handoff + index updated; see [handoff.md](handoff.md).

## [2026-06-08] chore | Align `.cursor/agents` with handoff template and constitution

Reviewed `glm-lead` and `qwen-implementer`: full handoff sections (incl. Risks/facit),
slash/fallback cross-refs, commit guardrail on Qwen, slimmed duplicate prose vs AGENTS.md.

## [2026-06-08] chore | Align `.cursor/commands` with handoff template and constitution

Reviewed `/glm-plan`, `/qwen-implement`, `/repo-agent`: added when-to-use lines, full handoff
sections, subagent cross-refs, model-handoff `@`; clarified repo-agent vs implementation flow.

## [2026-06-08] chore | Align `.cursor/hooks` with constitution; fix setup docs

Reviewed hooks.json + three session/prompt scripts. Qwen session now injects
`handoff.md` (not MODEL_COLLABORATION blob); GLM/Qwen context points to AGENTS.md.
Fixed stale `CURSOR_WORKSPACE_AGENT.md` (env var, GLM hook missing, Auto clarification).

## [2026-06-08] chore | Slim and align `.cursor/rules` with constitution

Reviewed four `alwaysApply` rules: deduped overlap with AGENTS.md, added Auto-model
guidance, fixed model-collaboration frontmatter `description`, tightened wiki/repo-aware
rules. Constitution remains canonical; rules are enforcement layer only.

## [2026-06-08] docs | Agent/subagent doc map (INDEX.md)

Added `docs/agent/INDEX.md` â€” layered inventory of all agent MD (constitution,
subagents, rules, hooks, setup, templates, wiki). Aligned cross-links to
*CONSTITUTION FOR AGENTS AND SUBAGENTS* in AGENTS.md.

## [2026-06-08] docs | AGENTS.md as agent constitution

Rewrote root `AGENTS.md` as canonical constitution for GLM lead, Qwen implementer
subagent, and universal duties/guardrails; product/Cloud moved to appendices.
Linked from `.cursor/agents/*`, `docs/agent/`, `.cursor/README.md`.

## [2026-06-08] chore | Categorize loose docs/ markdown files

Moved 22 top-level `docs/*.md` into `agent/`, `labeling/`, `research/`,
`validate/`, `tooling/` with per-folder README indexes; kept `CONTRIBUTING.md` and
`TRACKS.md` at `docs/` root. Updated cross-links repo-wide.

## [2026-06-09] chore | gitignore + label index for BTC facit hygiene

`.gitignore`: human_fib `*_events.json` / `*_interactions.csv` (regenerable),
`archive/research_superseded/**/charts/`, `_scratch_*.py`, data/raw|screenshots
stubs un-ignored. Removed 111 sidecars from git index. Updated `data/labels/INDEX.md`,
`archive/INDEX.md`, data-conventions.

## [2026-06-08] feat | labeling.preflight + cache-only TF switch in tool

`fibengine.labeling.preflight` checks candle caches, human fib counts, and HTF
overlay readiness before GUI. Tool no longer auto-fetches on timeframe switch
(avoid Bitfinex rate limits). Tests: `test_labeling_preflight.py`.

## [2026-06-08] feat | HTF read-only fib overlays in labeling.tool

`labeling.htf_fib_overlay`: on lower ladder TFs (1w/1d/4h/1h), draw saved
higher-TF human fib levels as read-only dotted lines; respects existing `f`
toggle and timeframe key navigation. Tests: `test_htf_fib_overlay.py`.

## [2026-06-08] reset | Archive data/ labels, human_fib, raw, screenshots

Per fresh-start for BTC monthly-first protocol: moved 279 files from
`data/labels/bitfinex/{BTC,ETH,SOL}-USD`, `human_fib/...`, `data/raw/`,
`data/screenshots/` into
`archive/research_superseded/2026-06-08_pre_btc_monthly_reset/data/`. Active
paths empty; updated INDEX, MANIFEST, DATA_CLASSIFICATION, handoff, protocol.

## [2026-06-09] policy | Archive blobs — no git commit unless user asks

`repository-layout-policy.md` §7, `archive/README.md`, `AGENTS.md`, repo-aware rule,
Copilot instructions: archive data stays local; agents commit stubs/manifests only.

## [2026-06-09] chore | Untrack legacy archive/experiments blobs

Gitignored `archive/experiments/**` (May 2026 spot-check runs/reviews); ~314 files
removed from index. README/INDEX stubs remain tracked. On-disk paths unchanged.

## [2026-06-09] chore | Untrack superseded research archive blobs

Commit 3 had ~557 files under `archive/research_superseded/` in git. `.gitignore`
now ignores that tree except each reset's `MANIFEST.md` (same pattern as `data/raw/`).
Archive stays on disk locally; active facit remains 76 BTC `fib_*.json`.

## [2026-06-08] release | Merge PR #27 to main

Merged `feature/research-spot-check` â†’ `main` (`bd22e87`): tooling Aâ€“F, fib/MTF
research stack, docs/wiki, cursor collaboration, security fixes. Closed superseded
PRs #20/#24/#26. Local `main` verified: pytest 198 passed.

## [2026-06-08] chore | Close #25; remove scratch scripts

Closed **#25** on GitHub after tooling Aâ€“F landed on `feature/research-spot-check`
(3 commits: feat/docs/chore). Deleted one-off `_scratch_*.py` scripts â€” findings
already in wiki reviews (`fib-n20-bucket`, `mtf-clean-forward-n20`, MTF checkpoint).
Repo bounds tiers raised for `research/*.py` (750 lines).
