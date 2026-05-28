# batches

Versionerade label-checkpoints (manifest + metadata + notes).

## Konvention

- Mappnamn: `YYYY-MM-DD_kort-beskrivning`
- Skapas med: `uv run python -m fibengine.labeling.batch --batch-id <id>`
- `labels_snapshot/` (valfritt) speglar samma struktur som `data/labels/`:
  `{exchange}/{symbol}/{timeframe}.json`
