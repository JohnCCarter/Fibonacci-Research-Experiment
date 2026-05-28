# experiments/label_review

Versionerade checkpoints och review-artefakter för labels.

## Struktur

```
label_review/
  INDEX.md          # batch-översikt
  batches/          # manifest-checkpoints (primär källa)
  packs/            # PNG review-paket (review_pack)
```

Äldre batchar och temporära mappar → `archive/experiments/label_review/` (inte under denna mapp).

## Skapa ny batch

```bash
uv run python -m fibengine.labeling.batch --batch-id 2026-05-28_round7 --note "beskrivning"
```

Se `REPO_POLICY.md` §5 för vad som ska sparas/städas.
