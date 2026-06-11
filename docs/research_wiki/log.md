# Research Wiki Log

Append-only trail of wiki ingests, decisions, and review sessions.

Use headings like:

```text
## [YYYY-MM-DD] type | Short title
```

Types: `ingest`, `decision`, `review`, `question`, `maintenance`.


> Older entries: [log-archive-pre-btc-reset-part1.md](log-archive-pre-btc-reset-part1.md)

## [2026-06-11] review | BTC/USD 1M reaction-review cycle complete — all 9 source fibs

All 9 human-drawn 1M source fibs reviewed through 1D + 4H using
`source_fib_projection_review` + `source_fib_projection_chart` (log scale,
`tradingview_log_chamoun`). Review windows confirmed in `review_windows.yaml`
(anchor_b → next macro boundary; 20260101 window extends to latest cache 2026-06-08).
Total: 62 1D events, 127 4H events across the full set.
Summary artifact: [reviews/btc-1m-reaction-review-cycle-20260611.md](reviews/btc-1m-reaction-review-cycle-20260611.md).

## [2026-06-10] maintenance | Remove GLM/Qwen/NVIDIA model-collaboration material

Correction to the entry below: the multi-model operating model is **not** active.
Deleted all GLM/Qwen/NVIDIA-NIM/BYOK material (26 files): `docs/agent/{MODEL_COLLABORATION,
CURSOR_WORKSPACE_AGENT,VSCODE_COPILOT_NVIDIA_MODELS,REPO_AWARE_AGENT,INDEX,README}.md`,
`docs/research_wiki/reference/nvidia-{glm,qwen}-api.md`, `templates/model-handoff.md`,
`docs/prompts/qwen-chat-starter.md`, `.cursor/{agents,commands,hooks}/*`, `.cursor/hooks.json`,
`.cursor/rules/model-collaboration-policy.mdc`, `scripts/nvidia_*`/`qwen_repo_agent_check.py`,
and `.env.example`. Rewrote `AGENTS.md` to a lean constitution (duties, source
authority, wiki maintenance, quality gate). Stripped model-collab references from
`CLAUDE.md`, `.github/copilot-instructions.md`, `.cursor/README.md`,
`.cursor/rules/repo-aware-coding-agent.mdc`, `.cursor/skills/README.md`, `glossary.md`,
`index.md`, `reference/cli-commands.md`, `docs/README.md`. Schema now describes only:
evidence handling, wiki maintenance, source authority, stale-memory prevention, and
verification via tests/checks. Historical entries below are kept as append-only record.

## [2026-06-10] maintenance | Align repo with Karpathy LLM Wiki pattern

Made source authority explicit and minimal. Added
[reference/source-authority.md](reference/source-authority.md) (layer model +
conflict rule: source evidence beats wiki synthesis). Clarified the wiki's role
in [README.md](README.md) and [index.md](index.md) (memory/synthesis, not
evidence or executable truth); moved multi-model/BYOK tooling links to an
"out of scope for the LLM Wiki pattern" section. Added a short source-authority +
local-config rule to `AGENTS.md` §6, `CLAUDE.md`, `.github/copilot-instructions.md`,
and the Cursor wiki rule. Expanded `scripts/check_repo_bounds.py` to fail when a
required wiki/schema file is missing or a local/private artifact (`.claude/`,
`.env`, caches, `dist/`, `._*.png`, logs) is tracked; wired it into CI. Reconciled
[data/labels/INDEX.md](../../data/labels/INDEX.md) with disk (1M=9; 1w/1d/4h dirs
absent — prior counts archived, not current). Gitignored `.claude/` and `._*.png`.

## [2026-06-10] decision | Addendum 2 — retire golden-zone review sampling

Issue #30 (Addendum 2): the machine must not bias any level. Removed
`primary_active_levels` and golden-zone review-sampling from configs (`settings.yaml`,
`settings.expansion.yaml`, `settings.deep-4h.yaml`), `core/config.py` (`FibConfig`), and the
review path (`human_review_pack._with_primary_levels`, `HumanReviewConfig.primary_levels`,
the `sample_candidates` golden-zone branch). All levels are now sampled equally (round-robin
via `_balanced_fill`). Added `human_highlights` (presentation/review-only) to
`HumanFibAnnotation` (round-trips; old JSON loads as `[]`). Docs updated. The prior
golden-zone pack `human_fib_review_20260609T135548Z` is superseded by an unbiased
regenerated pack. Two-phase work; Phase 2 (source-fib projection review view) pending.

## [2026-06-09] decision | Log-scale + golden-zone fib profile

Fib levels now log-interpolated (`scale_mode: log`, profile `tradingview_log_chamoun`,
`[0, 0.382, 0.5, 0.618, 0.786, 1]`, no 0.236). Golden zone
`primary_active_levels: [0.5, 0.618]` leads review sampling; full ladder stays context,
context capped so it never dominates. Charts render a log price axis (labeling tool +
both review tools) — saved level prices were already log; the fix was the linear y-axis.
Prior linear/0.236 labels+events+packs archived to
`archive/research_superseded/2026-06-09_pre_log_fib_profile_reset/`. 1M re-drawn (9 fibs).
Follow-up: `detect_level_events` was still pricing levels linearly — threaded `scale_mode`
through `human_fib_events` so emitted level prices match the log facit (e.g. 0.5 =
25 954.54, not 37 610). Events + pack regenerated; active pack
`human_fib_review_20260609T135548Z`. 225 tests pass.

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

## [2026-06-09] docs | Agent skills — pandera.pandas import convention

validation + data-analysis skills and module-map: agents must use
`import pandera.pandas as pa`, not top-level `import pandera as pa`.

## [2026-06-09] progress | BTC human fib facit counts synced to wiki

Labeling progress on disk: 1M=6, 1w=10, 1d=60, 4h=75 (151 total); 1h deferred.
Updated handoff, `data/labels/INDEX.md`, BTC protocol snapshot. Prior handoff
still said "start 1M" and empty `data/` — corrected.

## [2026-06-09] docs | CLAUDE.md + .rgignore for Claude onboarding

Cherry-picked intent from `claude/repo-audit-token-plan-65k9up`, updated for
BTC-first protocol, wiki handoff, labeling preflight, and archive §7. `.rgignore`
excludes archive/results/sidecars — not active `fib_*.json` facit.

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
