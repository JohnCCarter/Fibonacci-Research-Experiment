# Module Map

High-level map of `src/fibengine`. This is navigation, not an API contract.

## Core Runtime

- `core/` — shared domain types, fib math, config, scoring, structure, scale.
- `data/` — OHLCV fetch/cache/load helpers.
- `validation/` — OHLCV pandera schemas + pydantic manifests (`import pandera.pandas as pa`).
- `pivots/` — pivot detection.
- `evaluation/` — compare predictions and labels.
- `backtest/` — walk-forward selection, matrices, and trade experiments.
- `viz/` — plotting helpers.
- `experiment.py` — main experiment runner.

## Research And Labeling

- `labeling/` — label storage, GUI, worklists, human fib, behavior facit, and
  candidate layers.
- `research/` — level-event detector, review package generation, and interactive
  review tooling.

## Decoupled Layer

- `sizing/` — Layer B experiments. This must remain decoupled from Layer A swing
  selection.

## Critical Files

- `src/fibengine/core/fib.py`
- `src/fibengine/core/models.py`
- `src/fibengine/core/scoring.py`
- `src/fibengine/labeling/human_fib.py`
- `src/fibengine/labeling/human_fib_events.py`
- `src/fibengine/research/level_events.py`
- `src/fibengine/research/human_review_level_events.py`

## Source Links

- [Repository layout policy](../../../repository-layout-policy.md)
- [Research handoff](../../research/RESEARCH_HANDOFF.md)
- [Repo tracks](../../TRACKS.md)
