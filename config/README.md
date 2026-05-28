# config

Konfiguration för körningar.

- `settings.yaml` styr data, pivots, scoring, evaluation, sizing och backtest.
- `variants/` innehåller alternativa settings-filer (t.ex. Optuna-förslag).
- `variants/INDEX.md` indexerar alla varianter.
- Laddas via `fibengine.core.config`.

Baseline:

- `settings.yaml` är baseline och ska hållas stabil.
- Experiment ska i första hand köras med `--config config/variants/<fil>.yaml`.

Spårkoppling:

- `settings.yaml` = **Promotion** (canonical baseline).
- `variants/*.yaml` = **Research / Experiment** (kandidater som måste validate:as innan promotion).
