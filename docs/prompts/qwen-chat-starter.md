# Qwen Chat — repo-aware starter prompts

Use in a **new Cursor Chat** with model `qwen/qwen3-coder-480b-a35b-instruct` (BYOK).
Attach context with `@` as listed below.

Prerequisites: [CURSOR_WORKSPACE_AGENT.md](../CURSOR_WORKSPACE_AGENT.md), project rules enabled.

**Fast path:** in Chat, run slash command **`/repo-agent`** (see `.cursor/commands/repo-agent.md`).

---

## Attach first (recommended) — wiki as bootstrap

The [research wiki](../research_wiki/README.md) is the agent map; source docs/code are truth.

```
@docs/research_wiki/index.md
@docs/research_wiki/handoff.md
@docs/research_wiki/log.md
```

Optional (commands + compact style):

```
@AGENTS.md
@.cursor/rules/repo-aware-coding-agent.mdc
```

For fib/labeling tasks add:

```
@docs/HUMAN_FIB_ANNOTATION.md
@src/fibengine/labeling/tool.py
```

---

## Prompt A — general implementation

```text
Repo-aware mode. You are in the IDE agent shell, not a standalone chatbot.

1. Inspect the attached files and any codebase context you have.
2. Reply with:
   - Inspected: (bullet list of paths/evidence)
   - Observed: (facts from repo only)
   - Assumptions: (if any, with what to verify)
   - Answer: (minimal, actionable)
3. Do not invent facit, fib anchors, or promotion claims.
4. If you need more files, list exact paths before guessing.

Task: <describe your task here>
```

---

## Prompt B — review only (no edits)

```text
Inspect @AGENTS.md and @docs/research_wiki/handoff.md first.
Summarize current research focus and open questions from handoff only (observed vs assumption).
Do not propose code changes unless I ask.
```

---

## Prompt C — after you propose a diff

```text
Before applying: list affected files, risks for human-fib/facit semantics, and commands to run (uv run pytest -q, ruff).
```

---

## CLI smoke (no Cursor UI)

```bash
uv run python scripts/qwen_repo_agent_check.py
```

Sends a short repo excerpt to NVIDIA NIM and checks for inspection-style reply.
