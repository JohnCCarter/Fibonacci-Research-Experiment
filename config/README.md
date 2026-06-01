# config

Konfiguration för körningar.

- `settings.yaml` styr data, pivots, scoring, evaluation, sizing och backtest.
- `variants/` innehåller alternativa settings-filer (manuellt satta på principgrund).
- `variants/INDEX.md` indexerar alla varianter.
- Laddas via `fibengine.core.config`.

Baseline:

- `settings.yaml` är baseline (`exchange: bitfinex`, USD-par) och ska hållas stabil.
- Experiment ska i första hand köras med `--config config/variants/<fil>.yaml`.

Bitfinex / Genesis validate:

- `settings.bitfinex.yaml` — samma som baseline (explicit profil för Genesis-dok).
- Körordning och symbol-mappning: [`docs/GENESIS_BITFINEX_VALIDATE.md`](../docs/GENESIS_BITFINEX_VALIDATE.md).

Spårkoppling:

- `settings.yaml` = **Promotion** (canonical baseline).
- `variants/*.yaml` = **Research / Experiment** (kandidater som måste validate:as innan promotion).
