# Current Handoff

This page is the current working context for future agents. It is editable; the
append-only trail lives in [log.md](log.md).

## Current Focus

Model collaboration policy: **GLM-5.1** (NVIDIA `z-ai/glm-5.1`) = lead plan/review;
**Qwen3-Coder** = scoped implementation only. See [MODEL_COLLABORATION.md](../MODEL_COLLABORATION.md).

Human-fib-aware review workflow and research wiki remain the navigation layer.

## Recent Changes

- Review rendering was made fib-aware: H/L anchors, all fib levels, raw relation,
  and separate behavior candidates.
- `docs/research_wiki/` was expanded into a full seed wiki with glossary,
  concepts, references, decisions, sources, and logs.
- Atomic runnable artifact and agent handoff/log patterns are now repo workflow
  conventions.
- `.cursor/rules/research-wiki-maintenance.mdc` now makes wiki maintenance a
  persistent agent rule.
- `.cursor/rules/repo-aware-coding-agent.mdc` + `docs/REPO_AWARE_AGENT.md` — inspect
  repo before answer/edit; facts vs assumptions; for BYOK Qwen in Chat.

## Verification Snapshot

- Wiki docs have been checked against repo docs bounds.
- IDE lints reported no markdown diagnostics on the wiki files during setup.
- The wiki maintenance rule was added as an always-applied Cursor project rule.
- NVIDIA smoke: `scripts/nvidia_qwen_smoke.py` OK (~28s streaming, key in `.env`).
- Fib-aware review: `ruff check` OK; 12 research tests passed (2026-06-05).
- Human-fib smoke pack `human_fib_review_20260605T064610Z` — #15 acceptance criteria met on PNG inspection.

## Open Questions
- Should atomic artifact notes live only in the wiki, or should selected ones get
  small scripts under `scripts/`?
- When manual review findings exist, what review summary format is most useful?

## Next Useful Action

1. **Human review:** fill `review_sample.csv` in `human_fib_review_20260605T064610Z` (or re-run smoke command).
2. **Close issues:** #15 (smoke + acceptance), #16 (spike doc + smoke gate).
3. Optional: `level_event_review_tool --run-dir experiments/review/fib_level_events/human_fib_review_20260605T064610Z`.

## Guardrails

- Do not treat `*_candidate` as facit.
- Do not add auto-fib or trading signals.
- Do not promote wiki notes into canonical behavior.
- Keep new artifacts small and linked from [index.md](index.md).

## Links

- [Research wiki index](index.md)
- [Atomic runnable artifacts](concepts/atomic-runnable-artifacts.md)
- [Agent handoff and log](concepts/agent-handoff-log.md)
- [Karpathy LLM wiki source](sources/karpathy-llm-wiki.md)
- [Relation vs candidate](concepts/relation-vs-candidate.md)
- [Fib-aware review decision](decisions/2026-06-04-fib-aware-review.md)
