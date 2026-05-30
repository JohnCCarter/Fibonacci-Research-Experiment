# 2026-05-28 Ta bort Optuna (slutstädning)

Uppföljning på `2026-05-28-optuna-rollback.md` (som drog tillbaka själva runnern).
Den här noten städar de sista spåren så repot inte längre låtsas att Optuna finns.

Hypotes:
- Optuna har ingen legitim roll om vikter sätts på principer och labels endast är
  referens. Kvarvarande referenser i kod/docs skapar förvirring och frestelse.

Scope:
- Delsystem: dokumentation + repo-bokföring (ingen körning).
- Ytor: `README.md`, `docs/TRACKS.md`, `REPO_POLICY.md`, `docs/FIB_BACKTEST_PLAN.md`,
  `archive/INDEX.md`, `config/variants/`.

Observationer:
- `src/fibengine/tuning/` och `optuna`-dependencyn var redan borttagna (rollback);
  det som återstod var doc-referenser och arkiv-bokföring.
- Optuna-artefakterna behålls i `archive/` som historik (raderas inte) — `archive/`
  finns till för ersatt/legacy-material (REPO_POLICY §1).
- `config/variants/` ramas om till principmotiverade profiler (ingen auto-tuning).

Beslut:
- Ta bort kvarvarande Optuna-referenser i README/TRACKS/REPO_POLICY/FIB_BACKTEST_PLAN.
- Behåll arkiverade artefakter; håll `archive/INDEX.md` ärlig om vad som finns kvar.
- Vikter sätts manuellt på principgrund; ingen optimering mot `agreement`/labels.

Nästa steg:
- Validate via stabilitetsmatris + pivot recall; manuella viktändringar motiveras i
  premortem, aldrig auto-tunade mot ritningar.
