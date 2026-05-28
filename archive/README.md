# archive

**Enda platsen** för material som inte längre är aktivt i arbetsytorna, men ska finnas kvar spårbart.

## Regler

1. Inget arkiverat material på repo-roten eller i aktiva mappar som “lös fil”.
2. Skapa **undermapp per kategori** när en kategori växer (t.ex. `experiments/ledgers/`, `experiments/label_review/`).
3. Varje flytt dokumenteras i `archive/INDEX.md` (datum, källa, anledning).
4. Aktiva ytor pekar **inte** hit; kod och CLI läser bara canonical paths (t.ex. `experiments/results/`).

## Layout

```
archive/
  INDEX.md
  README.md
  docs/              # ersatta eller borttagna dokument (hela filer, inte stubs)
  experiments/
    ledgers/         # jsonl på fel path före results/-flytt
    label_review/    # dubletter, smoke, PNG-paket
  tests/             # (vid behov) duplicerade tester före tests/-struktur
```

Städning enligt `REPO_POLICY.md` §10 — permanent radering får ske **efter** att innehållet legat här och inte behövs.
