# 2026-05-28 Optuna start

Hypotes:
- Optuna kan hitta bättre viktkombinationer snabbare än manuell sweep, utan att vi tappar spårbarhet.

Scope:
- Delsystem: Lager A (`scoring.weights`)
- Data: befintliga labels i `data/labels/`
- Mål: lägga minimal, robust Optuna-integration i befintligt experimentflöde

Observationer:
- Repo är nu organiserat och indexerat, vilket minskar friktion för tuning.
- Premortem/reflektion är formaliserat som MÅSTE i policy.
- Nästa steg kan implementeras utan att bryta nuvarande CLI-flöden.

Beslut:
- Starta med en liten Optuna-modul + CLI entrypoint, inte en stor ombyggnad.
- Behålla nuvarande metrics/outputformat och skriva Optuna-resultat separat.

Nästa steg:
- Implementera första version av Optuna-runner.
- Köra ett litet trial-antal (smoke) för att verifiera pipeline och resultatfil.
