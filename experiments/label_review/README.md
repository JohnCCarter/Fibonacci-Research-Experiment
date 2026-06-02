# experiments/label_review

Versionerade checkpoints och review-artefakter för labels.

## Struktur

```
label_review/
  INDEX.md          # batch-översikt
  batches/          # manifest-checkpoints (primär källa)
  packs/            # PNG review-paket (review_pack)
```

Äldre batchar ligger i `archive/experiments/label_review/`.
Äldre review-exporter ligger i `archive/experiments/review/`.
Aktiv checkpoint just nu: `batches/2026-06-01_hypothesis-a-btc-1d/`.

## Skapa ny batch

```bash
uv run python -m fibengine.labeling.batch --batch-id 2026-05-28_round7 --note "beskrivning"
```

Se `repository-layout-policy.md` §5 för vad som ska sparas/städas.
