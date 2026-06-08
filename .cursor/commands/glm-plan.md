# GLM-5.1 lead — plan and handoff

**When:** GLM Chat (`z-ai/glm-5.1`). Non-trivial code → handoff + delegate; do not land large patches here.

@docs/research_wiki/index.md
@docs/research_wiki/handoff.md
@docs/research_wiki/log.md
@AGENTS.md
@docs/research_wiki/templates/model-handoff.md

GLM-5.1 lead mode (constitution: AGENTS.md §2, §4):

1. **Inspected** — wiki + relevant repo paths (or state what you still need).
2. **Observed** / **Assumptions** — separate facts from guesses.
3. **Implementation handoff** — fill template sections:
   - Goal, In scope, Out of scope, Files (read/write), Steps, Tests / verify, Risks / facit, Review criteria for GLM
4. **Delegate** — `Use the qwen-implementer subagent to implement this GLM handoff:` + handoff block.
   - Fallback: separate Qwen chat + `/qwen-implement` if subagent delegation unavailable.

Subagent spec: `.cursor/agents/glm-lead.md` · Ops: `docs/agent/MODEL_COLLABORATION.md`

**Task:** 
