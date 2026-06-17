# Guardrails

This wiki is documentation infrastructure. It does not change runtime behavior or
promotion status.

## Core Invariants

- Human-drawn fib anchors remain the source of truth for human-fib research.
- `*_candidate` labels are hypotheses until a human review label exists.
- Raw relations (`above/below/touch/cross`) are deterministic geometry, not
  behavior truth.
- Research modules must not feed back into canonical swing selection, evaluation,
  recall, or promotion.
- No auto-fib, buy/sell signals, edge claims, ML behavior classifier, or
  optimization loop belongs in this wiki.

## Track Boundary

Research can explore, document, and generate review artifacts. Validate proves a
candidate reproducibly. Promotion is the narrow trusted surface and requires the
gate in [Repo tracks](../../TRACKS.md).

## Repo Bounds

Wiki pages live under `docs/`, so they must stay below the docs size limits
enforced by `scripts/check_repo_bounds.py`. Prefer small linked pages over one
large narrative.

## Source Links

- [Repo tracks](../../TRACKS.md)
- [Research handoff](../../research/RESEARCH_HANDOFF.md)
- [Human fib annotation](../../labeling/HUMAN_FIB_ANNOTATION.md)
- [Level events](../../research/LEVEL_EVENTS.md)
- [Repository layout policy](../../../repository-layout-policy.md)
