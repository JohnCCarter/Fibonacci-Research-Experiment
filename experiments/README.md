# experiments

Aktiva experimentytor och versionerade sammanställningar.

## Struktur

- `results/` append-only jsonl-ledgers (historik per körning).
- `runs/` aktiv yta för framtida per-körning audit-mappar + `INDEX.md`.
- `label_review/` versionerade label-checkpoints (`batches/`, `packs/`).

**Reset 2026-06-08:** Pre-BTC-monthly generated outputs moved to
`archive/research_superseded/2026-06-08_pre_btc_monthly_reset/`.
Older May 2026 material remains in `archive/experiments/`.

Active protocol: [docs/BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md](../docs/BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md).

Se även `repository-layout-policy.md` §5 och §10 för vad som ska sparas/städas.

## Koppling till 3 spår

- **Research / Experiment:** `label_review/`, principmotiverade `config/variants/`.
- **Validate:** `pivot_recall/backtests/backtest_matrix` i `results/`.
- **Promotion:** inga direkta ändringar här; promotion sker först efter validate-gate enligt `docs/TRACKS.md`.
