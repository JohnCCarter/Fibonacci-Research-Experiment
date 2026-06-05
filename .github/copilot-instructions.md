# GitHub Copilot instructions (Fibonacci Research Experiment)

Copilot in this repo should behave as a **repo-aware coding agent**, not a generic chatbot.

## Source of truth

- [AGENTS.md](../AGENTS.md) — product, commands, gotchas
- [docs/AGENT_RESPONSE_STYLE.md](../docs/AGENT_RESPONSE_STYLE.md) — compact replies unless user asks for depth
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
