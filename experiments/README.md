# experiments

Körningsartefakter och sammanställningar från experiment.

## Struktur

- `results/` append-only jsonl-ledgers (historik per körning).
- `runs/` per-körning audit-mappar, kategoriserade som `experiment/` och `stability/` + `INDEX.md`.
- `label_review/` versionerade label-checkpoints (`batches/`, `packs/`).

Arkiverat material (gamla jsonl-paths, label-dubletter): `archive/experiments/`.

Se även `REPO_POLICY.md` §5 och §10 för vad som ska sparas/städas.

## Koppling till 3 spår

- **Research / Experiment:** `label_review/`, principmotiverade `config/variants/`.
- **Validate:** `runs/stability/`, `pivot_recall/backtests/backtest_matrix` i `results/`.
- **Promotion:** inga direkta ändringar här; promotion sker först efter validate-gate enligt `docs/TRACKS.md`.
