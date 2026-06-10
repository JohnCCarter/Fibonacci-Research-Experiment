# Agent & subagent documentation map

**Constitution (canonical):** [AGENTS.md](../../AGENTS.md) — *CONSTITUTION FOR AGENTS AND SUBAGENTS*

Read the constitution first. Everything below is **setup, enforcement, or templates** — not a
second source of roles or authority.

---

## Layer 0 — Constitution

| Path | Role |
|------|------|
| [AGENTS.md](../../AGENTS.md) | Roster, workflow, duties, guardrails, navigation |

---

## Layer 1 — Subagent prompts (Cursor)

| Path | Model | Role |
|------|-------|------|
| [.cursor/agents/glm-lead.md](../../.cursor/agents/glm-lead.md) | `z-ai/glm-5.1` | Lead subagent — `/glm-plan` enforcement in Agent mode |
| [.cursor/agents/qwen-implementer.md](../../.cursor/agents/qwen-implementer.md) | `qwen/qwen3-coder-480b-a35b-instruct` | **Subagent of GLM** — `/qwen-implement` Chat fallback |

---

## Layer 2 — Always-on rules (`.cursor/rules/`)

| Path | Applies when |
|------|----------------|
| [model-collaboration-policy.mdc](../../.cursor/rules/model-collaboration-policy.mdc) | GLM↔Qwen workflow, delegation |
| [repo-aware-coding-agent.mdc](../../.cursor/rules/repo-aware-coding-agent.mdc) | All models — inspect, wiki, facts vs assumptions |
| [agent-response-style.mdc](../../.cursor/rules/agent-response-style.mdc) | All models — compact replies |
| [research-wiki-maintenance.mdc](../../.cursor/rules/research-wiki-maintenance.mdc) | Substantial research work — wiki updates |

---

## Layer 3 — Slash commands (`.cursor/commands/`)

| Command | File | Who / when |
|---------|------|------------|
| `/glm-plan` | [glm-plan.md](../../.cursor/commands/glm-plan.md) | GLM Chat — plan, handoff, delegate subagent |
| `/qwen-implement` | [qwen-implement.md](../../.cursor/commands/qwen-implement.md) | Qwen Chat fallback — implement pasted handoff only |
| `/repo-agent` | [repo-agent.md](../../.cursor/commands/repo-agent.md) | Any model — wiki bootstrap; Qwen send-gate bypass |

---

## Layer 4 — Setup & operations (`docs/agent/`)

| Doc | Purpose | Overlap note |
|-----|---------|----------------|
| [MODEL_COLLABORATION.md](MODEL_COLLABORATION.md) | BYOK, hooks, mermaid workflow, smoke scripts | Ops detail; constitution = AGENTS.md |
| [CURSOR_WORKSPACE_AGENT.md](CURSOR_WORKSPACE_AGENT.md) | Full Cursor checklist, mode matrix, hooks | **Primary setup guide** |
| [REPO_AWARE_AGENT.md](REPO_AWARE_AGENT.md) | Short Chat/Qwen companion | Points to CURSOR_WORKSPACE for full setup |
| [VSCODE_COPILOT_NVIDIA_MODELS.md](VSCODE_COPILOT_NVIDIA_MODELS.md) | VS Code Copilot BYOK (GLM + Qwen) | Parity with Cursor NIM |
| [AGENT_RESPONSE_STYLE.md](AGENT_RESPONSE_STYLE.md) | Compact vs expanded replies | Annex to constitution §3 |

---

## Layer 5 — Hooks & workspace index

| Path | Role |
|------|------|
| [.cursor/hooks.json](../../.cursor/hooks.json) | `sessionStart` / `beforeSubmitPrompt` wiring |
| [.cursor/hooks/on_glm_session.py](../../.cursor/hooks/on_glm_session.py) | GLM `sessionStart` — handoff + template (model-gated) |
| [.cursor/hooks/on_qwen_session.py](../../.cursor/hooks/on_qwen_session.py) | Qwen `sessionStart` — implementer context + handoff (model-gated) |
| [.cursor/hooks/on_qwen_prompt.py](../../.cursor/hooks/on_qwen_prompt.py) | Qwen `beforeSubmitPrompt` — handoff/bootstrap gate |
| [.cursor/README.md](../../.cursor/README.md) | Version-controlled Cursor shell index |

---

## Layer 6 — Templates & chat prompts

| Path | Role |
|------|------|
| [research_wiki/templates/model-handoff.md](../research_wiki/templates/model-handoff.md) | GLM → Qwen handoff block |
| [research_wiki/templates/handoff-entry.md](../research_wiki/templates/handoff-entry.md) | Wiki handoff/log sections |
| [prompts/qwen-chat-starter.md](../prompts/qwen-chat-starter.md) | Copy-paste Chat prompts |

---

## Layer 7 — Wiki (navigation, not constitution)

| Path | Role |
|------|------|
| [research_wiki/index.md](../research_wiki/index.md) | Map — links agent docs under *Architecture* |
| [research_wiki/handoff.md](../research_wiki/handoff.md) | Current focus (read before substantial work) |
| [research_wiki/log.md](../research_wiki/log.md) | Append-only trail |
| [research_wiki/concepts/agent-handoff-log.md](../research_wiki/concepts/agent-handoff-log.md) | Wiki handoff/log **pattern** (research sessions) |
| [research_wiki/reference/nvidia-glm-api.md](../research_wiki/reference/nvidia-glm-api.md) | GLM NIM API notes |
| [research_wiki/reference/nvidia-qwen-api.md](../research_wiki/reference/nvidia-qwen-api.md) | Qwen NIM API notes |

---

## Layer 8 — Other surfaces

| Path | Role |
|------|------|
| [.github/copilot-instructions.md](../../.github/copilot-instructions.md) | GitHub Copilot — same constitution |

---

## Read order (new session)

1. [AGENTS.md](../../AGENTS.md)
2. [research_wiki/handoff.md](../research_wiki/handoff.md)
3. Role-specific: GLM → `/glm-plan` + [MODEL_COLLABORATION.md](MODEL_COLLABORATION.md); Qwen → handoff + `/qwen-implement`
4. Setup once: [CURSOR_WORKSPACE_AGENT.md](CURSOR_WORKSPACE_AGENT.md)

---

## Maintenance rule

When adding agent/subagent docs: update **this INDEX**, [README.md](README.md), and
[AGENTS.md](../../AGENTS.md) §7 only if roles or workflow change. Do not duplicate
constitution text in setup docs — link instead.
