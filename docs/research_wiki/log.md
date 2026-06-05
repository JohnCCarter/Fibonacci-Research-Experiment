# Research Wiki Log

Append-only trail of wiki ingests, decisions, and review sessions.

Use headings like:

```text
## [YYYY-MM-DD] type | Short title
```

Types: `ingest`, `decision`, `review`, `question`, `maintenance`.

## [2026-06-04] ingest | Karpathy LLM wiki pattern

Source: <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

Takeaway: use a persistent, agent-maintained wiki as a compounding research
artifact. Raw sources remain the source of truth; wiki pages summarize,
cross-link, and preserve decisions so future sessions do not re-derive context.

Repo mapping:

- `docs/research_wiki/index.md` is the content map.
- `docs/research_wiki/log.md` is the chronological trail.
- Future concept, decision, and review pages should link back to source docs and
  generated review artifacts.

Guardrail: this is documentation infrastructure only. It does not add auto-fib,
trading logic, ML behavior, or promotion-path changes.

## [2026-06-04] decision | Expand to full repo wiki

Decision: grow `docs/research_wiki/` from a minimal scaffold into a practical
repo knowledge base before the project structure grows further.

Added scope:

- glossary
- core concepts
- module and data reference pages
- CLI command reference
- first decision/source pages

Boundary: still docs-only. No runtime code, automation, promotion-path changes,
auto-fib, trading signals, or ML behavior.

## [2026-06-04] decision | Adopt atomic artifacts and handoff

Decision: adopt two workflow patterns from the Karpathy gist review as repo
conventions:

- atomic runnable artifacts for small, complete, bounded research work.
- agent handoff/log for current context and durable session trail.

Implementation:

- [Atomic runnable artifacts](concepts/atomic-runnable-artifacts.md)
- [Agent handoff and log](concepts/agent-handoff-log.md)
- [Current handoff](handoff.md)
- [Atomic artifact template](templates/atomic-artifact.md)
- [Handoff entry template](templates/handoff-entry.md)

Boundary: adopt the shape, not the external code. No ML code, auto-tuning,
runtime behavior, or promotion-path change.

## [2026-06-04] decision | Enforce wiki maintenance rule

Decision: operationalize the Karpathy LLM-wiki pattern with a persistent Cursor
rule.

Implementation:

- `.cursor/rules/research-wiki-maintenance.mdc`

Effect: future agents should read `index.md`, `log.md`, and `handoff.md` before
substantial work, then update the smallest relevant wiki pages after meaningful
research, review, architecture, workflow, or implementation changes.

Boundary: this is agent discipline, not runtime automation. It must not change
research results, promote behavior, add auto-fib, or turn candidates into facit.

## [2026-06-04] ingest | NVIDIA Qwen3 Coder API

Source: NVIDIA NIM / build.nvidia.com model `qwen/qwen3-coder-480b-a35b-instruct`.

Repo mapping:

- `scripts/nvidia_qwen_smoke.py` — stdlib smoke via `NVIDIA_API_KEY`.
- [NVIDIA Qwen API](reference/nvidia-qwen-api.md) — setup and guardrails.

Boundary: external assistant only; keys in env only; not fibengine runtime.

## [2026-06-04] verify | NVIDIA API docs + smoke

Source: [infer API](https://docs.api.nvidia.com/nim/reference/qwen-qwen3-coder-480b-a35b-instruct-infer)
confirms OpenAI-compatible `/v1/chat/completions` on `integrate.api.nvidia.com`.

Effect: smoke verified locally (~28s, streaming). Wiki reference updated with infer
link and cold-start latency note. Optional diag: `scripts/nvidia_qwen_diag.py`.

## [2026-06-04] doc | Cursor BYOK for Qwen3 Coder

Added [Cursor chat steps](reference/nvidia-qwen-api.md#cursor-chat-byok) for
`qwen/qwen3-coder-480b-a35b-instruct` via OpenAI override + custom model ID.

## [2026-06-04] maintenance | Repo-aware agent rules (Qwen in Chat)

Source: user request — Qwen should behave as repo-aware coding agent in Chat, not
memory-only chatbot.

Added:

- `.cursor/rules/repo-aware-coding-agent.mdc` (always apply)
- `docs/REPO_AWARE_AGENT.md` — Cursor settings, `@` context, User Rules snippet
- `.github/copilot-instructions.md` — Copilot parity
- `AGENTS.md` section + link from [nvidia-qwen-api.md](reference/nvidia-qwen-api.md)

Note: BYOK still limits which Cursor modes route to Qwen; rules apply when project
rules are enabled in Chat.

## [2026-06-04] maintenance | Qwen repo-agent prompts + CLI check

Added `docs/prompts/qwen-chat-starter.md` and `scripts/qwen_repo_agent_check.py`
(repo excerpt → NVIDIA NIM; expects Inspected/Observed/Assumptions sections). Verified OK locally.

## [2026-06-04] maintenance | Cursor workspace agent shell

Added `docs/CURSOR_WORKSPACE_AGENT.md`, `.cursor/README.md`, `.cursor/commands/repo-agent.md`
(slash command prefills wiki `@` + repo-aware prompt). AGENTS.md and wiki index updated.

## [2026-06-04] maintenance | Qwen hooks (sessionStart + beforeSubmitPrompt)

`.cursor/hooks.json`: when model contains `qwen`, inject repo-agent context at session
start and block bare prompts until `/repo-agent` or wiki `@` (see CURSOR_WORKSPACE_AGENT.md).

## [2026-06-04] decision | GLM-5.1 lead + Qwen3-Coder implement

Policy: GLM owns plan/review/approval; Qwen owns scoped implementation. Added
`docs/MODEL_COLLABORATION.md`, `.cursor/rules/model-collaboration-policy.mdc`,
`/glm-plan`, `/qwen-implement`, `on_glm_session.py`, updated Qwen hooks, `nvidia_glm_smoke.py`,
wiki [nvidia-glm-api.md](reference/nvidia-glm-api.md), [model-handoff template](templates/model-handoff.md).

## [2026-06-05] maintenance | Fib-aware review implementation (#15)

Implemented fib-aware rendering in `human_review_level_events.py` and aligned
`level_event_review_tool.py` titles. Human-fib event JSON path via
`--human-fib-events`; tests in `test_human_fib_review_rows.py`,
`test_human_review_sampling.py`, updated `test_human_review_level_events.py`.

Verification: `ruff check` OK; 12 research tests passed.

## [2026-06-05] review | ETH 1d human-fib smoke (#15 gate)

Smoke pack `human_fib_review_20260605T064610Z` from
`fib_ETH-USD_1d_20170618T000000_events.json` (10/35 events sampled).

Acceptance: H/L anchors, all fib levels, relation vs `*_candidate`, and `fib_id`
visible on PNG charts. Distilled page:
[2026-06-05 ETH 1d smoke](reviews/2026-06-05-eth-1d-human-fib-smoke.md).

## [2026-06-05] decision | Tooling spike conclusion (#16)

After smoke: keep Matplotlib PNG + JSON review path; defer Dash/Panel/React/HTML
until a human reviewer flags pan/zoom as blocker. Spike doc updated with smoke
outcome. Issue #16 deliverable (recommendation + comparison) was already in
[FIB_AWARE_TOOLING_SPIKE.md](../../FIB_AWARE_TOOLING_SPIKE.md).
