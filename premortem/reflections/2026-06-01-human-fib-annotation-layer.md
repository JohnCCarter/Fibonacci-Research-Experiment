# Human-fib annotation layer + behavior-candidates (2026-06-01)

## What we did

- New `fibengine.labeling.human_fib`: human-drawn fib is **ground truth**. Stores
  exact anchors + derived levels (`0.236..1.0`), classifies each candle vs each
  level as `above/below/touch/cross`. `w` key in the labeling tool + CLI. No auto-fib.
- New `fibengine.labeling.human_fib_events`: feeds the human fib into the existing
  `detect_level_events` → `*_candidate` (`rejection/continuation/failure/reaction`)
  per level. Same taxonomy as `docs/LEVEL_EVENTS.md`. **Candidates never facts.**
- Docs: `docs/HUMAN_FIB_ANNOTATION.md` (both layers), linked from `docs/README.md`
  and `docs/RESEARCH_HANDOFF.md`.

## Why it matters

- Splits the layering cleanly: **atoms** (per-candle geometry, human_fib) vs
  **path** (across-candle candidates, human_fib_events). Human anchors are the
  source of truth; machine only reads/stores/derives/classifies.
- Bridge needs no refactor: `swing.start = anchor_a` (ratio 1.0),
  `swing.end = anchor_b` (ratio 0.0) reproduce the human levels exactly, and the
  detector scans bars after the drawn leg.

## Decisions

- Emit-only for now: no `level_event_review_tool` wiring yet (deferred).
- Derived level prices rounded to 8 decimals for clean facit JSON.
- Raised `docs/**/*.md` repo-bound 200 → 300 lines (REPO_POLICY §2B + check_repo_bounds)
  so RESEARCH_HANDOFF/BEHAVIOR_FACIT edits pass; bytes cap unchanged (20 KiB).

## Guardrails held

- No auto-fib, no tuning, no edge claims. Additive: does not touch swing selection,
  `evaluate()`, recall, or promotion.

## Next

1. Optional: wire human-fib candidates into the review tool for the confirm-loop.
2. Draw more human fibs across symbols/timeframes; compare candidate distributions.
3. Commit sweep (rounding fix + facit files + both layers) when ready.
