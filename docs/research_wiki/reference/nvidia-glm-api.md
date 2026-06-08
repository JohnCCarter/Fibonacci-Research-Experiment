# NVIDIA GLM-5.1 API (lead agent)

External **lead** model: plan, review, verify. Implementation is **Qwen3-Coder** — see [MODEL_COLLABORATION.md](../../agent/MODEL_COLLABORATION.md).

## Endpoint

| Field | Value |
|-------|--------|
| Base URL | `https://integrate.api.nvidia.com/v1` |
| Model | `z-ai/glm-5.1` |
| Auth | `NVIDIA_API_KEY` (same as Qwen) |

Catalog: [build.nvidia.com/z-ai/glm-5.1](https://build.nvidia.com/z-ai/glm-5.1)  
Reference: [z-ai/glm5.1](https://docs.api.nvidia.com/nim/reference/z-ai-glm5.1)

## Cursor Chat (BYOK)

Same BYOK setup as Qwen — add a **second** custom model id `z-ai/glm-5.1`. Use a **dedicated Chat** for GLM (plan/review), separate from Qwen (implement).

Slash command: `/glm-plan`

## Smoke

```bash
uv run python scripts/nvidia_glm_smoke.py
```

## Guardrails

- GLM does not invent fib facit or approve promotion from wiki notes alone.
- Handoffs must be explicit scope; Qwen must not expand without new GLM approval.
