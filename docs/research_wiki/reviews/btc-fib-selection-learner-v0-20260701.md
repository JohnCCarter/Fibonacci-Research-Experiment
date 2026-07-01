# Fib Selection Learner — v0 scaffolding (Issue #42, 2026-07-01)

**Status:** v0 landed (schema + baseline + gated ML stub + fixture + tests + docs). Selection-learning
only — **no edge / PnL / auto-fib / Genesis claim**. Not a prereg; no run, no result to sign off.

## Why v0 is scoped the way it is

Issue [#38 postlock] + the selection campaign already showed a ranker over geometric features adds
nothing over prominence on the only powered cell (`no_pivot_signal_above_prominence`, AP 0.057), and
the 2026-07-01 decomposition put the *positive* selection rule off the geometric axis. The pivot-point
idea was disproved the same day (structural + empirical, continuity-controlled null).

So the missing ingredient is **not another model** — it is the data the campaign never had:
**contrastive** judgments (accept / reject / ambiguous + *why*). v0 builds exactly that capture
surface and a deterministic floor, and **gates ML/Optuna fail-closed** until the data justifies them.
This is the honest reading of Issue #42's own guardrails (selection-not-PnL, leakage split by window,
ML behind an optional extra), sequenced so tuning can never manufacture a signal the features lack.

## What landed

| Piece | Path |
|-------|------|
| Annotation schema + YAML round-trip | [`research/selection_annotation.py`](../../../src/fibengine/research/selection_annotation.py) |
| Deterministic baseline + metrics + window split | [`research/selection_baseline.py`](../../../src/fibengine/research/selection_baseline.py) |
| Gated ML/Optuna entry point (fail-closed) | [`research/selection_ranker_ml.py`](../../../src/fibengine/research/selection_ranker_ml.py) |
| Fixture window (`created_by: fixture`) + store | `data/labels/selection_annotations/` (README/INDEX) |
| Tests (round-trip, ranking, split-by-window, gate) | `tests/research/test_selection_{annotation,baseline,ranker_ml}.py` |
| Optional `[ml]` extra (sklearn/optuna/joblib) | `pyproject.toml` |

Reuses the human-fib anchor vocabulary and `evaluation/leg_agreement.py` philosophy — no new leg
representation, no parallel `selection_learning/` package (the `research/selection_learning*` family
already exists).

## The ML gate (binding)

`selection_ranker_ml.check_gate` raises unless **all** hold: (1) `[ml]` extra installed, (2)
≥ `MIN_HUMAN_WINDOWS` (=30) real `created_by: human` windows — fixtures never count, (3) a
pre-registered locked holdout is passed in (no inline split). The functional ranker + Optuna tuning
are deliberately **not built** in v0; they need a fresh baseline-beating prereg first.

## Acceptance criteria (Issue #42 v0) — status

Done: annotation schema; candidate/feature via the annotation shape; fixture (1 accepted / 2 rejected
/ 1 ambiguous); deterministic baseline; optional `[ml]` extra; gated ML stub + Optuna stub; tests
(round-trip, ranker scores, split-by-window-not-row); docs. **Deferred by design (gated):** the
functional sklearn ranker and Optuna tuning — until the human-window + prereg gate is met.

## Next

Capture the first **real** contrastive windows from Chamoun (reject/ambiguous + reasons); the paused
1w cascade is a natural first case. Then test whether the *reasons/tags* beat the magnitude baseline —
only if yes, register a ranker prereg and lift the gate.

## Sources

- Issue #42 (owner). Existing lane: `research/selection_learning*` +
  [selection-learning prereg](btc-fib-selection-learning-prereg-20260617.md).
- [Chamoun daily-fib style](../reference/chamoun-daily-fib-style.md) (Observed/Inferred/Unverified).
- [#38 daily wick-pair postlock](btc-fib-daily-wick-pair-anchor-prereg-20260629-postlock.md).
