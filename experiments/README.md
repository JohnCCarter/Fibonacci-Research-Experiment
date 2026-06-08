# experiments

Aktiva experimentytor och versionerade sammanställningar.

## Struktur

- `results/` append-only jsonl-ledgers (historik per körning).
- `runs/` aktiv yta för framtida per-körning audit-mappar + `INDEX.md`.
- `label_review/` versionerade label-checkpoints (`batches/`, `packs/`).

Historiska audit-mappar och review-exporter ligger i `archive/experiments/`.

Se även `repository-layout-policy.md` §5 och §10 för vad som ska sparas/städas.

## Koppling till 3 spår

- **Research / Experiment:** `label_review/`, principmotiverade `config/variants/`.
- **Validate:** `pivot_recall/backtests/backtest_matrix` i `results/`.
- **Promotion:** inga direkta ändringar här; promotion sker först efter validate-gate enligt `docs/TRACKS.md`.
