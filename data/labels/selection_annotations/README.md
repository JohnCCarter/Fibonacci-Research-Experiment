# Selection annotations (contrastive fib-leg judgments)

Issue #42 v0. Durable store for **contrastive** fib-selection annotations: for one chart window,
the candidate A/B legs the human **accepts / rejects / marks ambiguous**, each with a free-text
`reason` and optional tags. This is the half the selection campaign never had — it only had
*accepted* examples (the `human_fib/` facit).

## Layout

```
selection_annotations/{exchange}/{SYMBOL-with-dash}/{timeframe}/window_<id>.yaml
```

Schema + round-trip: [`research/selection_annotation.py`](../../../src/fibengine/research/selection_annotation.py).
Baseline scorer + metrics: [`research/selection_baseline.py`](../../../src/fibengine/research/selection_baseline.py).

## Provenance (binding)

- `created_by: human` — real judgment; the accept/reject call is facit-grade for selection.
- `created_by: fixture` — illustrative scaffolding, **never truth** (same rule as `*_candidate` ≠ facit).

Only `human` windows count toward the ML gate (`research/selection_ranker_ml.py`). ML/Optuna stay
disabled until enough human windows + a pre-registered holdout exist — see the v0 doc.

## Not

No edge / PnL / auto-fib claim. Selection match = agreement with the human's pick, not a trade.
