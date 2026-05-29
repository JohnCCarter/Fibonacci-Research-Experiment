# 2026-05-28 Ta bort Optuna

Hypotes: Optuna har ingen legitim roll om vikter ska sättas på principer och labels endast är referens.

Beslut:
- Ta bort `src/fibengine/tuning/`, `optuna`-dependency, varianter, ledgers och körhistorik (ingen legacy-yta).
- Uppdatera README, TRACKS, REPO_POLICY, FIB_BACKTEST_PLAN.

Nästa: Validate via stabilitetsmatris + pivot recall; manuella viktändringar med premortem.
