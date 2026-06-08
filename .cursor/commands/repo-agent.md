# Repo-aware agent (wiki bootstrap)

**When:** Any model (Auto, Qwen before handoff, general inspect/review). Not a substitute for `/glm-plan` + `/qwen-implement` on scoped implementation.

@docs/research_wiki/index.md
@docs/research_wiki/handoff.md
@docs/research_wiki/log.md
@AGENTS.md

Repo-aware mode (constitution: AGENTS.md §3 — not a memory-only chatbot):

1. **Inspected** — paths/evidence used (wiki + codebase context).
2. **Observed** — facts from repo only.
3. **Assumptions** — mark explicitly; say what file/command would verify.
4. **Answer** — minimal, actionable; small diffs only if asked.
5. No invented fib facit, anchors, or promotion claims. `*_candidate` ≠ facit.

Non-trivial implementation → GLM `/glm-plan` → delegate `qwen-implementer` or Qwen `/qwen-implement`.

Alt starter prompts: `docs/prompts/qwen-chat-starter.md`

**Task:** 
