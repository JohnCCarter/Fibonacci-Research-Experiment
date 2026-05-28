# Reflektion: Optuna-tuning tillbakadragen (2026-05-28)

## Beslut
Den automatiska vikt-optimeringen (`fibengine.tuning.optuna_runner`) togs bort.
Vi återgår till ursprungsplanen: **principer styr, labels = referens.**

## Varför (ärligt)
Optuna-objektivet maximerade `mean_agreement − 0.15·mean_fib_err` — exakt de mått
som `evaluation/metrics.py:evaluate(...)` beräknar **mot de manuella labelsen**.
Det bryter mot den uttalade filosofin ("vi optimerar aldrig vikter mot dem", README
+ metrics-docstring) och mot den premortem-risk vi själva skrev ("Att smyga tillbaka
till att optimera mot exemplen").

Dessutom misslyckades det på sina egna premisser:
- Best (trial 31, 50 trials): `mean_agreement ≈ 0.025` (≈ noll), `mean_fib_err ≈ 0.92`.
- "Bästa" vikterna var principvidriga: `scale_confluence = −1.75` (negativ — tvärtemot
  hela multi-skala-tesen), `prominence = −1.02`, `round_number = −1.12`.
- Det är brusanpassning till 13–15 labels (under vår egen 20–30-tröskel), 7–8 vikter,
  ±1.5 spann, best-of-N på samma data utan train/val/holdout.

## Vad vi behåller
- Vikter sätts manuellt på principgrund (baseline `config/settings.yaml`).
- Varianter får ligga i `config/variants/` men valideras mot **stabilitet/recall**
  (Phase 7), aldrig mot en label-agreement-objektivfunktion.
- `agreement` förblir en mjuk *sanity*-signal i rapporter — inte ett optimeringsmål.

## Arkiverat (ej raderat)
- `archive/experiments/optuna/optuna_best.json`, `optuna_trials.jsonl`
- `archive/config_variants/optuna_2026-05-28_trial31.yaml`
- `premortem/reflections/2026-05-28-optuna-start.md` behålls som historik.

## Sidofynd (åtgärdas separat)
`_bar_of_timestamp` snäppte tyst label-tidsstämplar utanför candle-fönstret till
kant-baren → skräpmått för långa timeframes (1M/1w/1d med `limit=500`). Lagas i
samma städning (out-of-window-flagga).
