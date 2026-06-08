# GitHub Copilot instructions (Fibonacci Research Experiment)

Copilot in this repo should behave as a **repo-aware coding agent**, not a generic chatbot.

## NVIDIA models (GLM + Qwen) — setup

If Chat cannot reach **GLM-5.1** or **Qwen3-Coder**, follow [docs/agent/VSCODE_COPILOT_NVIDIA_MODELS.md](../docs/agent/VSCODE_COPILOT_NVIDIA_MODELS.md):

1. Verify API: `python scripts/nvidia_qwen_diag.py` (key in `.env`; VS Code terminal uses `python`, not `uv`).
2. VS Code → **Chat: Manage Language Models** → **Custom Endpoint** → `chatLanguageModels.json`.
3. Provider **NVIDIA NIM**, `apiType` **chat-completions**, key `nvapi-...`.
4. Models (exact ids): `z-ai/glm-5.1`, `qwen/qwen3-coder-480b-a35b-instruct`.
5. URL per model: `https://integrate.api.nvidia.com/v1/chat/completions`, `toolCalling: true`.
6. New chat → pick model; first reply may take 20–60 s.

GLM = plan/review; Qwen = scoped implement — [MODEL_COLLABORATION.md](../docs/agent/MODEL_COLLABORATION.md).

## Source of truth

- [AGENTS.md](../AGENTS.md) — **constitution** (agents, subagents, workflow, guardrails)
- [docs/agent/AGENT_RESPONSE_STYLE.md](../docs/agent/AGENT_RESPONSE_STYLE.md) — compact replies unless user asks for depth
- [docs/research_wiki/index.md](../docs/research_wiki/index.md) — research context map
- [docs/research_wiki/concepts/guardrails.md](../docs/research_wiki/concepts/guardrails.md) — research invariants

## Workflow

1. Inspect relevant files before proposing implementation changes.
2. State what was read; separate **observed facts** from **assumptions**.
3. Prefer small, reviewable diffs; ask when scope is unclear.
4. Do not invent human fib facit or optimize weights against labels.
5. After code changes, suggest `uv run ruff check src tests` and `uv run pytest -q`.

## Domain guardrails

- Layer A = swing selection research; Layer B (sizing/trades) is decoupled.
- Machine labels are candidates only — never treat as facit without human review.
- `*_candidate` events are not human ground truth.
