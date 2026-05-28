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
- `tuning/` experimentell parameteroptimering (t.ex. Optuna).
- `viz/` plotting/visualisering.
- `experiment.py` standardrunner för experimentkörning.
