# Agent response style (default)

**Audience:** Cursor agents, subagents, and anyone automating work in this repo.  
**Authority:** Project default unless the user overrides in the current message.

Human owners may also add matching text in Cursor **User Rules**; this file is the **repo source of truth**.

---

## Default mode: compact

| Rule | Do |
|------|-----|
| **Short answers** | Prefer a few sentences or ≤10 bullets total. |
| **No long reports** | Skip executive summaries, repeated context, and “what we did last session” unless asked. |
| **Diff-first** | After code changes: *what changed + why* — not full files. Use line-range citations only when needed. |
| **Max 10 points** | Lists, status, and plans cap at **10** items; merge or drop the rest. |
| **Blockers only** | Progress updates: blockers + next action. Skip “all green” step-by-step narration. |
| **Proportional** | Simple question → short answer. No tutorial unless requested. |

---

## When to explain more

Expand **only** when the user clearly opts in, for example:

- “förklara mer”, “mer detalj”, “utökad”, “gå igenom”
- “det är ok att förklara”, “ok att vara lång”, “full rapport”
- A direct question that needs depth (architecture, trade-offs, debugging root cause)

Until then, stay in compact mode even if the topic is complex (give the headline + offer depth in one line if useful).

---

## Exceptions (compact still, but complete)

Always include enough detail for **safety and correctness**:

- Commands the user must run (full, copy-pasteable)
- Breaking changes, data loss risk, or wrong facit/label semantics
- Failed CI / tests — symptom + fix, not a lecture

---

## Examples

**Good (default):**

> Uppdaterade `fetch.py` med `--refresh` och paginering så 1d slutar på senaste bar. Kör: `uv run python -m fibengine.data.fetch --labeling-set --refresh`.

**Too long (avoid unless user opted in):**

> Multi-paragraph recap of MTF origin, full command matrix, and repeated worklist stats.

**Good (user said “förklara mer”):**

> Same headline, then subsections on Bitfinex `since` pagination, cache paths, and weekly Thursday vs TV Monday.

---

## Related docs

- [`AGENTS.md`](../../AGENTS.md) — agent entry (product, CLI, gotchas)
- [`RESEARCH_HANDOFF.md`](RESEARCH_HANDOFF.md) — research scope (not response length)
