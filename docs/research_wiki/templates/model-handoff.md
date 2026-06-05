# Model handoff (GLM-5.1 → Qwen3-Coder)

Copy this block from **GLM-5.1 chat** into **Qwen chat** after `/qwen-implement`.

```markdown
## GLM handoff

**Goal:** (one sentence)

**In scope:**
- 

**Out of scope:**
- 

**Files (read/write):**
- 

**Steps:**
1. 

**Tests / verify:**
- `uv run pytest -q` (paths or markers)
- `uv run ruff check src tests`

**Risks / facit:**
- No new human fib facit; no `*_candidate` as truth

**Review criteria for GLM:**
- 
```

Qwen: implement **only** in-scope items. Return changed paths, rationale, and test commands run.
