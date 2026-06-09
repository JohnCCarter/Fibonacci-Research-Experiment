# experiments/label_review

Versionerade checkpoints och review-artefakter för labels.

## Struktur

```
label_review/
  INDEX.md          # batch-översikt
  batches/          # manifest-checkpoints (primär källa)
  packs/            # PNG review-paket (review_pack)
```

**Reset 2026-06-08:** `batches/2026-06-01_hypothesis-a-btc-1d` archived to
`archive/research_superseded/2026-06-08_pre_btc_monthly_reset/`.
Older material: `archive/experiments/label_review/`.
No active batch until BTC monthly-first labeling checkpoint.

## Skapa ny batch

```bash
uv run python -m fibengine.labeling.batch --batch-id 2026-05-28_round7 --note "beskrivning"
```

Se `repository-layout-policy.md` §5 för vad som ska sparas/städas.
