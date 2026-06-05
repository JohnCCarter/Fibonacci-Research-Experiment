# Cursor workspace — agent shell for this repo

**Qwen (or any BYOK model) is only the LLM.** Cursor provides the **agent shell**: project rules, `@` context, indexing, and tools (mode-dependent).

## What the repo configures (version-controlled)

| Path | Role |
|------|------|
| [rules/](rules/) | Always-on agent policy (`alwaysApply: true` on core rules) |
| [commands/](commands/) | Slash commands in Chat/Agent — prefill wiki `@` + repo-aware prompt |
| [skills/](skills/) | Optional deep dives (backtest, labeling, etc.) |
| [../AGENTS.md](../AGENTS.md) | Commands, product scope, gotchas |
| [../docs/research_wiki/](../docs/research_wiki/) | **Read first** — index, handoff, log |
| [../docs/CURSOR_WORKSPACE_AGENT.md](../docs/CURSOR_WORKSPACE_AGENT.md) | **Setup checklist** (BYOK Qwen + rules) |
| [hooks.json](hooks.json) | **GLM lead** / **Qwen implement** context on `sessionStart`; Qwen send gate |
| [commands/glm-plan.md](commands/glm-plan.md) | GLM: plan + handoff |
| [commands/qwen-implement.md](commands/qwen-implement.md) | Qwen: implement handoff only |

## One-time setup (human)

Follow [docs/CURSOR_WORKSPACE_AGENT.md](../docs/CURSOR_WORKSPACE_AGENT.md).

## Every session (Qwen in Chat)

1. **Cursor Settings → Rules** — project rules from this folder enabled.
2. **New Chat** → model `qwen/qwen3-coder-480b-a35b-instruct` (NVIDIA BYOK).
3. Run slash command **`/repo-agent`** (or paste from [docs/prompts/qwen-chat-starter.md](../docs/prompts/qwen-chat-starter.md)).
4. Add task-specific `@src/...` or `@docs/...` from wiki links.

## Verify

```bash
uv run python scripts/qwen_repo_agent_check.py
```
