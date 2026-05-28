# tuning

Optimerings- och tuningverktyg (experimentella), separata från standardrunnern.

- `optuna_runner.py` kör Optuna över `scoring.weights` (Lager A).
- Resultat skrivs till:
  - `experiments/results/optuna_trials.jsonl`
  - `experiments/results/optuna_best.json`
  - `experiments/runs/optuna/YYYY-MM-DD/optuna_.../`
