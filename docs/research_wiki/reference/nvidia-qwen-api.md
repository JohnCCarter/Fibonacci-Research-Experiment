# NVIDIA Qwen3 Coder API

External **implementation** model (scoped code per GLM handoff). Not part of
fibengine runtime or promotion. Lead agent: [nvidia-glm-api.md](nvidia-glm-api.md) ·
[MODEL_COLLABORATION.md](../../MODEL_COLLABORATION.md).

## Endpoint

| Field | Value |
|-------|--------|
| Base URL | `https://integrate.api.nvidia.com/v1` |
| Model | `qwen/qwen3-coder-480b-a35b-instruct` |
| Auth | `NVIDIA_API_KEY` (environment only) |

Catalog: [build.nvidia.com](https://build.nvidia.com/qwen/qwen3-coder-480b-a35b-instruct)

API reference (infer): [chat/completions](https://docs.api.nvidia.com/nim/reference/qwen-qwen3-coder-480b-a35b-instruct-infer)
— OpenAI-compatible `POST /v1/chat/completions`, Bearer `NVIDIA_API_KEY`.
First call can take 20–60s (large MoE); use streaming in the smoke script.

## Cursor chat (BYOK)

Use NVIDIA as an **OpenAI-compatible** provider in the IDE (not fibengine code).

1. **Cursor Settings → Models**
2. **OpenAI API Key** — paste your `nvapi-...` key (same as `NVIDIA_API_KEY`).
3. Enable **Override OpenAI Base URL** → `https://integrate.api.nvidia.com/v1`  
   (root path only — no `/chat/completions`).
4. **+ Add model** → `qwen/qwen3-coder-480b-a35b-instruct` (exact string).
5. **Verify**, Save, open a **new Chat**, pick that model in the model dropdown.

**Limits (Cursor product):**

- BYOK applies to **Chat / Plan** with your key; **Agent, Composer, Tab** stay on
  Cursor’s built-in routing ([API keys docs](https://cursor.com/docs/models-and-usage/api-keys)).
- This agent thread (Auto) is **not** switched by the steps above — start a normal Chat.
- With base URL override, only use models that exist on NVIDIA (disable unrelated OpenAI
  models in the list if calls fail).
- First reply can take **20–60 s** (cold 480B MoE).

## Setup (Windows PowerShell)

```powershell
$env:NVIDIA_API_KEY = "nvapi-..."
```

Optional local file (gitignored): create `.env` at repo root and load it in your
shell profile; never commit keys.

## Repo Smoke Script

No `openai` package required — uses stdlib HTTP:

```bash
uv run python scripts/nvidia_qwen_smoke.py
uv run python scripts/nvidia_qwen_smoke.py "Explain relation vs candidate in one sentence."
```

## OpenAI SDK (optional)

If you already have `openai` installed locally:

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ["NVIDIA_API_KEY"],
)
completion = client.chat.completions.create(
    model="qwen/qwen3-coder-480b-a35b-instruct",
    messages=[{"role": "user", "content": "Your prompt here"}],
    temperature=0.4,
    top_p=0.8,
    max_tokens=4096,
)
print(completion.choices[0].message)
```

## Repo-aware agent behavior (Chat + Qwen)

Qwen is only the model; Cursor is the shell. Workspace setup: [CURSOR_WORKSPACE_AGENT.md](../../CURSOR_WORKSPACE_AGENT.md) (BYOK, rules, `/repo-agent`). Policy: `.cursor/rules/repo-aware-coding-agent.mdc`.

## Guardrails

- Rotate the key if it was pasted into chat, logs, or committed files.
- Do not use this model to invent fib anchors, trading signals, or facit labels.
- Wiki and review workflows stay human-ground-truth first.

## Source Links

- [NVIDIA infer API](https://docs.api.nvidia.com/nim/reference/qwen-qwen3-coder-480b-a35b-instruct-infer)
- [Atomic runnable artifacts](../concepts/atomic-runnable-artifacts.md)
