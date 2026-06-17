# archive

**Enda platsen** för material som inte längre är aktivt i arbetsytorna, men ska finnas kvar spårbart.

## Regler

1. Inget arkiverat material på repo-roten eller i aktiva mappar som “lös fil”.
2. Skapa **undermapp per kategori** när en kategori växer (t.ex. `experiments/ledgers/`, `experiments/label_review/`, `experiments/runs/`).
3. Varje flytt dokumenteras i `archive/INDEX.md` (datum, källa, anledning).
4. Aktiva ytor pekar **inte** hit; kod och CLI läser bara canonical paths (t.ex. `experiments/results/`).
5. **Git:** arkivblobs (runs, reviews, labels, caches, PNG/JSONL under `experiments/` och
   `research_superseded/`) versioneras **inte** — bara `README.md`, `INDEX.md` och
   `MANIFEST.md`. Committa **inte** arkivdata om inte användaren uttryckligen ber om det.
   Se `repository-layout-policy.md` §7.

## Layout

```
archive/
  INDEX.md
  README.md
  docs/              # ersatta eller borttagna dokument (hela filer, inte stubs)
  experiments/
    ledgers/         # jsonl på fel path före results/-flytt
    label_review/    # äldre batchar, dubletter, smoke, PNG-paket
    review/          # exporter från experiments/review/
    runs/            # äldre audit-mappar från experiments/runs/
  tests/             # (vid behov) duplicerade tester före tests/-struktur
```

Städning enligt `repository-layout-policy.md` §10 — permanent radering får ske **efter** att innehållet legat här och inte behövs.
