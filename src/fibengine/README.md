# fibengine

Huvudpaket för Fibonacci-motorn.

## Kategorier

- `core/` domänlogik (features, scoring, struktur, modeller, config).
- `data/` hämtning/laddning av candle-data.
- `pivots/` pivot-detektering.
- `labeling/` label-verktyg och lagring/checkpoints.
- `evaluation/` jämförelse och mätning mot labels.
- `backtest/` stabilitets- och trade-backtest.
- `sizing/` sizing-logik (Lager B).
- `viz/` plotting/visualisering.
- `experiment.py` standardrunner för experimentkörning.

**Skuld:** `labeling/tool.py` är medvetet stor (GUI) — ska delas; lägg inte till mer där utan split (`repository-layout-policy.md` §2B).
