# Repo-aware agent setup (Cursor Chat + Qwen)

> **Full workspace checklist:** [CURSOR_WORKSPACE_AGENT.md](CURSOR_WORKSPACE_AGENT.md)  
> **Cursor folder index:** [.cursor/README.md](../.cursor/README.md)  
> **Slash command:** `/repo-agent` in Chat

**Goal:** When you use **Qwen3 Coder** (or any model) in Cursor **Chat**, it should behave like a coding agent: inspect the repo, follow rules, minimal diffs — not answer from memory alone.

**Distinction:** Qwen is the **model**. Cursor is the **agent shell** (rules, `@` context, tools depending on mode).

---

## What we added in the repo

| File | Role |
|------|------|
| [.cursor/rules/repo-aware-coding-agent.mdc](../.cursor/rules/repo-aware-coding-agent.mdc) | Always-on workflow: inspect → facts vs assumptions → minimal edits → tests |
| [.cursor/rules/agent-response-style.mdc](../.cursor/rules/agent-response-style.mdc) | Compact replies unless user opts in |
| [.cursor/rules/research-wiki-maintenance.mdc](../.cursor/rules/research-wiki-maintenance.mdc) | Wiki read/update for substantial research work |
| [AGENTS.md](../../AGENTS.md) | Repo agent entry + Qwen pointer |
| [.github/copilot-instructions.md](../.github/copilot-instructions.md) | Same policy for GitHub Copilot |

Cursor loads `.cursor/rules/*.mdc` into context for **Agent** and typically for **Chat** when project rules are enabled.

---

## Cursor settings (you)

### 1. Use Qwen in Chat (BYOK)

See [docs/research_wiki/reference/nvidia-qwen-api.md](research_wiki/reference/nvidia-qwen-api.md):

- Settings → Models → OpenAI API Key = `nvapi-...`
- Override base URL → `https://integrate.api.nvidia.com/v1`
- Add model `qwen/qwen3-coder-480b-a35b-instruct`
- **New Chat** (not this Auto/Agent thread) and select that model

**Product limit:** BYOK applies to **Chat / Plan**. **Agent / Composer / Tab** may still use Cursor’s default models. For full tool loops with Cursor’s agent stack, use **Agent** mode; for Qwen specifically, use **Chat** with rules + `@` context below.

### 2. Enable project rules

- Cursor Settings → **Rules** (or Features): ensure **project rules** from `.cursor/rules` are on.
- Confirm `repo-aware-coding-agent` appears / is active.

### 3. Optional: User Rules (paste once)

If Chat still feels “chatbot-like”, add to **Cursor Settings → Rules → User Rules**:

```text
In this workspace, act as a repo-aware coding agent. Before implementation answers: inspect relevant files (or ask me to @ them). Follow AGENTS.md and .cursor/rules. Separate observed facts from assumptions. Minimal diffs; ask before edit if scope is unclear. Run or recommend uv ruff + pytest after code changes.
```

### 4. Give the model evidence in Chat

When tools are limited in Chat, **attach context**:

- **Wiki first:** `@docs/research_wiki/index.md`, `@handoff.md`, `@log.md` (see [research_wiki/README.md](research_wiki/README.md))
- Then `@AGENTS.md` for commands/gotchas
- `@src/fibengine/...` for the area you change
- `@Folder` for broad search scope

Copy-paste prompts: [docs/prompts/qwen-chat-starter.md](prompts/qwen-chat-starter.md).

Quick pattern:

```text
Inspect the repo first (search/read AGENTS.md and relevant src files).
Then answer. Label facts vs assumptions. Propose minimal diff only.
```

CLI check (repo excerpt → Qwen):

```bash
uv run python scripts/qwen_repo_agent_check.py
```

---

## Expected behavior checklist

- [ ] Reads / cites repo paths before large implementation advice
- [ ] Mentions what it inspected (short)
- [ ] Does not invent facit, fib anchors, or promotion claims
- [ ] Proposes small diffs; asks if scope unclear
- [ ] Suggests `uv run pytest -q` / ruff after edits

---

## External script (no IDE tools)

`scripts/nvidia_qwen_smoke.py` is **API-only** (no repo tools). For agent-like behavior outside Cursor, you need an orchestrator (tool loop) — not documented here.

---

## Related

- [NVIDIA Qwen API](research_wiki/reference/nvidia-qwen-api.md)
- [Agent response style](AGENT_RESPONSE_STYLE.md)
