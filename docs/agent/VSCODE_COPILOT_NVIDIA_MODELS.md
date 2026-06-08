# VS Code Copilot — NVIDIA GLM-5.1 + Qwen3-Coder (BYOK)

Guide for **GitHub Copilot Chat in VS Code** using the same NVIDIA NIM setup that works in Cursor for this repo.

**Not fibengine runtime** — external LLMs for plan (GLM) and implementation (Qwen). See [MODEL_COLLABORATION.md](MODEL_COLLABORATION.md).

---

## What you need

| Item | Value |
|------|--------|
| API key | `nvapi-...` from [build.nvidia.com](https://build.nvidia.com/) |
| Base URL | `https://integrate.api.nvidia.com/v1` |
| GLM model id | `z-ai/glm-5.1` |
| Qwen model id | `qwen/qwen3-coder-480b-a35b-instruct` |
| API type | OpenAI **Chat Completions** (`POST /v1/chat/completions`) |

Repo: copy `.env.example` → `.env` (gitignored) with `NVIDIA_API_KEY=nvapi-...`.

---

## Step 0 — Verify API before VS Code

From repo root (proves key + network, not VS Code config). VS Code uses **`python`**, not `uv`:

```powershell
python scripts/nvidia_qwen_diag.py
python scripts/nvidia_glm_smoke.py --no-stream
python scripts/nvidia_qwen_smoke.py --no-stream
```

Scripts are stdlib-only (no venv packages required). Use the same interpreter as your VS Code terminal (`python` on PATH).

- **401 / 403** → wrong or expired key; regenerate at build.nvidia.com.
- **Timeout 20–60 s on first call** → normal for large MoE; retry with `--timeout 600`.
- **OK** → proceed to VS Code.

---

## Step 1 — Prerequisites (VS Code)

1. **VS Code** with GitHub Copilot extension (Chat enabled).
2. **BYOK policy** — Copilot Business/Enterprise: org admin must allow *Bring Your Own Language Model Key in VS Code* ([changelog](https://github.blog/changelog/2026-04-22-bring-your-own-language-model-key-in-vs-code-now-available/)).
3. **Custom Endpoint** — use **VS Code Insiders** if *Custom Endpoint* is missing from *Add Models* ([language models docs](https://code.visualstudio.com/docs/copilot/customization/language-models)). Stable VS Code is catching up; Insiders has the current BYOK path.

---

## Step 2 — Add NVIDIA as Custom Endpoint

1. Open **Chat** view.
2. Model picker → **Manage Language Models** (gear), or run command **`Chat: Manage Language Models`**.
3. **Add Models** → **Custom Endpoint**.
4. Group name: e.g. `NVIDIA NIM`.
5. API key: your `nvapi-...` (stored in VS Code secret store — not in repo).
6. API type: **Chat Completions**.

VS Code opens `chatLanguageModels.json`. Replace/add a provider block like this:

```json
[
  {
    "name": "NVIDIA NIM",
    "vendor": "customendpoint",
    "apiType": "chat-completions",
    "apiKey": "${input:chat.lm.secret.NVIDIA_NIM}",
    "models": [
      {
        "id": "z-ai/glm-5.1",
        "name": "GLM-5.1 (lead)",
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "toolCalling": true,
        "vision": false,
        "maxInputTokens": 128000,
        "maxOutputTokens": 8192
      },
      {
        "id": "qwen/qwen3-coder-480b-a35b-instruct",
        "name": "Qwen3-Coder (implement)",
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "toolCalling": true,
        "vision": false,
        "maxInputTokens": 128000,
        "maxOutputTokens": 8192
      }
    ]
  }
]
```

Save the file. **Restart VS Code** if models do not appear in the picker.

### Critical details (common failures)

| Mistake | Fix |
|---------|-----|
| Wrong `id` | Must be **exact** strings above (slashes included). |
| Wrong `url` | Full URL `.../v1/chat/completions` — not base-only, not double `/v1/v1`. |
| `toolCalling: false` | Model hidden from **agent** chat; set `true` for coding agents. |
| Using deprecated `github.copilot.chat.customOAIModels` | Use **Custom Endpoint** + `chatLanguageModels.json` instead. |
| OpenAI provider + NVIDIA key | NVIDIA is **not** OpenAI; use Custom Endpoint. |
| First reply hangs | Wait up to **60 s** (cold start); smoke scripts use `--timeout 300`. |

---

## Step 3 — Select models in Chat

1. **New chat** (do not reuse old threads).
2. Model picker → **NVIDIA NIM** group:
   - **GLM-5.1** — plan, review, architecture, handoff.
   - **Qwen3-Coder** — scoped implementation only.
3. Pin both models (pin icon) for quick switching.

Workflow mirrors Cursor: [MODEL_COLLABORATION.md](MODEL_COLLABORATION.md) — GLM produces handoff; Qwen implements; GLM reviews.

---

## Step 4 — Repo-aware behavior

Copilot reads [.github/copilot-instructions.md](../.github/copilot-instructions.md) automatically.

Before implementation tasks, load:

- [docs/research_wiki/index.md](research_wiki/index.md)
- [docs/research_wiki/handoff.md](research_wiki/handoff.md)
- [AGENTS.md](../../AGENTS.md)

Paste or `@`-reference paths as needed. VS Code has no Cursor `/repo-agent` slash command; start chats with: *Inspect repo first; separate Observed vs Assumptions; minimal diffs.*

---

## Step 5 — Utility models (BYOK-only users)

If you use BYOK **without** GitHub sign-in, set lightweight utility models or title generation may fail:

- `chat.utilityModel` → one of your NVIDIA models (e.g. GLM).
- `chat.utilitySmallModel` → same or Qwen.

Settings → search `chat.utility`.

---

## Troubleshooting checklist for Copilot

Run in order:

1. `python scripts/nvidia_qwen_diag.py` — API reachable?
2. Confirm `chatLanguageModels.json` — `id`, `url`, `toolCalling`.
3. Restart VS Code; pick model in **new** chat.
4. Check org BYOK policy on github.com (Copilot settings).
5. Try **VS Code Insiders** if Custom Endpoint is unavailable.
6. For agent mode: model must support tools (`toolCalling: true`).

**Symptom: models listed but errors in chat**

- Read error body: 401 = key; 404 = wrong model id; timeout = increase patience or provider limits.

---

## Cursor vs VS Code (same API, different UI)

| | Cursor (working here) | VS Code Copilot |
|---|----------------------|-----------------|
| Key | Settings → Models → OpenAI API Key = `nvapi-...` | Custom Endpoint API key |
| Base URL | Override `https://integrate.api.nvidia.com/v1` | Per-model `url` = `.../v1/chat/completions` |
| Model ids | Add custom models in Settings | `id` in `chatLanguageModels.json` |
| Verify | `scripts/nvidia_*_smoke.py` | Same scripts + Chat picker |

---

## Related

- [MODEL_COLLABORATION.md](MODEL_COLLABORATION.md)
- [research_wiki/reference/nvidia-glm-api.md](research_wiki/reference/nvidia-glm-api.md)
- [research_wiki/reference/nvidia-qwen-api.md](research_wiki/reference/nvidia-qwen-api.md)
- [CURSOR_WORKSPACE_AGENT.md](CURSOR_WORKSPACE_AGENT.md) — Cursor-specific setup
